"""Convert the approved mockup (projects/launch-site/mockup-v3-ian) into Webflow MCP payloads.

  styles   python3 -I tools/mock2wf.py styles            -> build/styles.json  (create/update actions, chain order)
                                                            styles/site.css     (rules Webflow classes can't express)
  section  python3 -I tools/mock2wf.py section <page> <n> -> build/<page>-<n>.json (element_schema tree for section n)

Mapping rules (desktop-first, same breakpoints as Webflow):
  @media (max-width:991px|767px|479px) -> breakpoint medium|small|tiny. Other media, @keyframes, @font-face, :root,
  element selectors, descendant/child/attribute/:not/:has selectors -> styles/site.css (shipped by the styles island).
  .a -> class a; .a.b -> combo b on a; :hover :focus-visible :first-child :last-child ::before ::after -> pseudo.
  Element class lists "a b c" become Webflow chains a > a.b > a.b.c; each combo gets the rules of its own class.
  var(--x) -> the City Bike Webflow variable (bound when it is the whole value, CSS var name otherwise).
  RENAME avoids the 4 live-site collisions; padding-global reuses the live Client-First utility (no styles written).
Needs tinycss2: run through `uv run -q --with tinycss2 python -I tools/mock2wf.py ...`."""
import csv
import html.parser
import json
import pathlib
import re
import sys

import tinycss2

HERE = pathlib.Path(__file__).resolve().parent.parent
SITE = HERE.parent.parent / "projects" / "launch-site"
CSS = [SITE / "mockup-v2/v2.css", SITE / "mockup-v3/v3.css", SITE / "mockup-v3/appsim.css"]
PAGES = SITE / "mockup-v3-ian"
OUT = HERE / "build"

RENAME = {"h2": "heading-title", "h3": "heading-card", "label": "text-label", "container": "container-site"}  # live site owns .heading-2/.heading-3/.container/.label/.heading-section
LIVE_REUSE = {"padding-global"}  # live Client-First utility: apply, never restyle
BP = {"991": "medium", "767": "small", "479": "tiny"}
PSEUDO = {":hover": "hover", ":focus-visible": "focus-visible", ":focus": "focus", ":active": "active",
          ":first-child": "first-child", ":last-child": "last-child", "::before": "before", "::after": "after",
          ":before": "before", ":after": "after", "::placeholder": "placeholder"}
VARS = {"ink": "--city-bike--ink", "ink-2": "--city-bike--ink-2", "ink-3": "--city-bike--ink-3", "ink-4": "--city-bike--ink-4",
        "paper": "--city-bike--paper", "paper-2": "--city-bike--paper-2", "line": "--city-bike--line", "line-dark": "--city-bike--line-dark",
        "gold": "--bike-share-gold", "zone-gold": "--bike-share-gold", "gold-deep": "--city-bike--gold-deep", "gold-pale": "--city-bike--gold-pale",
        "navy": "--city-bike--navy", "zone-purple": "--bike-share-purple", "zone-blue": "--bike-share-blue",
        "max": "--city-bike--container-max", "display": "--city-bike--font-display", "body": "--city-bike--font-body", "mono": "--city-bike--font-mono"}
VAR_IDS = {"--city-bike--ink": "variable-0874860c-94b8-63e8-bfca-8c39c0a34063", "--city-bike--ink-2": "variable-a912ff17-69d4-da6f-85d2-2866a57f05c7",
           "--city-bike--ink-3": "variable-e842d1c7-e25b-d56f-a07d-302869a41a6a", "--city-bike--ink-4": "variable-fee1b173-ee3b-8550-8dae-b688ad3dca52",
           "--city-bike--paper": "variable-1ddefcca-e948-cb9b-7fed-79b86f4a9a25", "--city-bike--paper-2": "variable-2bf0eb7f-3c1b-3122-c924-517e56285b2a",
           "--city-bike--line": "variable-4c226859-8226-fe2d-0512-4b61303ea0ce", "--city-bike--line-dark": "variable-e44b18e9-669a-b60a-fb5f-31044709e178",
           "--city-bike--gold-deep": "variable-a76255f0-9b46-e6d3-aece-3333a4683265", "--city-bike--gold-pale": "variable-8838cbfe-7004-714b-c0ef-084f42283943",
           "--city-bike--navy": "variable-48f1d811-8ca1-5eae-6cbd-7570edb95754", "--city-bike--container-max": "variable-6be286fb-479e-fa69-b1d4-975615dfb11c",
           "--city-bike--font-display": "variable-c7a4d6c3-00ea-351b-58a3-c4d090cb84d3", "--city-bike--font-body": "variable-660cdef8-678d-2884-ea11-11541b560128",
           "--city-bike--font-mono": "variable-6a8b4396-720f-0e18-ebeb-f9eec1a9d41c"}
# Mockup-only tokens with no Webflow variable: inlined.
INLINE = {"white": "#fff", "gutter": "clamp(1.25rem,4vw,3.5rem)", "ease": "cubic-bezier(.2,.7,.2,1)"}
SIMPLE = re.compile(r"^((?:\.[A-Za-z0-9_-]+)+)((?::{1,2}[a-z-]+)?)$")


def cls(name):
    return RENAME.get(name, name)


def sub_vars(value):
    def rep(m):
        name = m.group(1)
        if name in INLINE:
            return INLINE[name] if not m.group(2) else INLINE[name]
        return f"var({VARS[name]})" if name in VARS else m.group(0)
    return re.sub(r"var\(--([a-z0-9-]+)(,[^)]*)?\)", rep, value)


def webflow_can_hold(name, value):
    """Webflow rejects custom properties and -webkit- names, drops !important, and collapses composite shadows that contain var()."""
    return not (name.startswith("--") or name.startswith("-webkit-") or "!important" in value
                or (name in ("box-shadow", "text-shadow", "filter") and "var(" in value))


def prop(name, value):
    value = hosted(sub_vars(value.strip()))
    m = re.fullmatch(r"var\((--[a-z0-9-]+)\)", value)
    if m and m.group(1) in VAR_IDS:
        return {"property_name": "background-color" if name == "background" else name, "variable_as_value": VAR_IDS[m.group(1)]}
    return {"property_name": name, "property_value": value}


def decls(block):
    out = []
    for d in tinycss2.parse_blocks_contents(block, skip_comments=True, skip_whitespace=True):
        if d.type == "declaration":
            v = tinycss2.serialize(d.value).strip() + (" !important" if d.important else "")
            out.append((d.lower_name, v))
    return out


def parse_css():
    """Return (rules, leftover_css). rules: list of (chain tuple, pseudo, breakpoint, [(prop, value)])."""
    rules, left = [], []
    for f in CSS:
        sheet = tinycss2.parse_stylesheet(f.read_text(), skip_comments=True, skip_whitespace=True)
        for r in sheet:
            if r.type == "at-rule" and r.lower_at_keyword == "media":
                cond = tinycss2.serialize(r.prelude).strip()
                m = re.fullmatch(r"\(max-width:\s*(991|767|479)px\)", cond)
                if not m:
                    left.append(tinycss2.serialize([r]))
                    continue
                for rr in tinycss2.parse_rule_list(r.content, skip_comments=True, skip_whitespace=True):
                    take(rr, BP[m.group(1)], rules, left, wrap=f"@media {cond}")
            elif r.type == "qualified-rule":
                take(r, "main", rules, left)
            else:
                left.append(tinycss2.serialize([r]))
    return rules, "\n".join(left)


def take(r, bp, rules, left, wrap=None):
    sels = [s.strip() for s in tinycss2.serialize(r.prelude).split(",")]
    body = decls(r.content)
    keep = []
    for s in sels:
        m = SIMPLE.match(s)
        pseudo = m and (m.group(2) or "")
        if m and (pseudo == "" or pseudo in PSEUDO):
            chain = tuple(cls(c) for c in m.group(1).split(".")[1:])
            if chain[0] in LIVE_REUSE:
                continue
            ok = [(k, v) for k, v in body if webflow_can_hold(k, v)]
            spill = [(k, v) for k, v in body if not webflow_can_hold(k, v)]
            rules.append((chain, PSEUDO.get(pseudo, "noPseudo"), bp, ok, len(rules)))
            if spill:
                text = s + "{" + ";".join(f"{k}:{sub_vars(v)}" for k, v in spill) + "}"
                left.append(f"{wrap}{{{text}}}" if wrap else text)
        else:
            keep.append(s)
    if keep:
        text = ",".join(keep) + "{" + ";".join(f"{k}:{sub_vars(v)}" for k, v in body) + "}"
        left.append(f"{wrap}{{{text}}}" if wrap else text)


class Tree(html.parser.HTMLParser):
    VOID = {"img", "br", "source", "input", "hr", "meta", "link", "wbr", "use", "path", "circle", "rect", "line", "polyline", "polygon", "stop"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {"tag": "root", "attrs": {}, "kids": []}
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "kids": []}
        self.stack[-1]["kids"].append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1]["kids"].append({"tag": tag, "attrs": dict(attrs), "kids": []})

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if data.strip() or (data and self.stack[-1]["kids"]):
            self.stack[-1]["kids"].append({"tag": "#text", "text": data})


SVG_CASE = {k.lower(): k for k in ("viewBox", "preserveAspectRatio", "gradientUnits", "gradientTransform", "patternUnits", "clipPathUnits",
                                    "markerWidth", "markerHeight", "refX", "refY", "stdDeviation", "textLength", "lengthAdjust", "pathLength",
                                    "maskUnits", "maskContentUnits", "spreadMethod", "startOffset", "xlink:href", "patternTransform", "patternContentUnits", "primitiveUnits", "filterUnits", "baseFrequency", "numOctaves", "kernelMatrix", "tableValues", "attributeName", "repeatCount", "keyTimes", "keySplines", "calcMode")}
SVG_TAGS = {"lineargradient": "linearGradient", "radialgradient": "radialGradient", "clippath": "clipPath", "textpath": "textPath", "foreignobject": "foreignObject"}


def hosted(text):
    """Swap mockup image paths (../mockup/img/x.png, ../mockup-v3/img/x.webp) for the uploaded asset's Webflow CDN URL."""
    urls = json.loads((HERE / "webflow" / "asset-urls.json").read_text())

    def rep(m):
        hit = urls.get(pathlib.Path(m.group(0)).stem)
        return hit["url"] if hit else m.group(0)
    text = re.sub(r"(?:\.\./)+mockup[\w-]*/[\w/.-]+\.(?:png|jpe?g|webp|svg|gif)", rep, text)

    def rep_url(m):  # url(img/bike.webp) in CSS: relative to the mockup stylesheet, 404s anywhere else
        ref = m.group(2)
        if ref.startswith(("http", "data:", "//", "#")):
            return m.group(0)
        hit = urls.get(pathlib.Path(ref).stem)
        return f"url({hit['url']})" if hit else m.group(0)
    return re.sub(r"url\((['\"]?)([^)'\"]+)\1\)", rep_url, text)


def outer(n):
    if n["tag"] == "#text":
        return html.escape(n["text"], quote=False)
    a = "".join(f' {SVG_CASE.get(k, k)}="{html.escape(v or "", quote=True)}"' if v is not None else f" {k}" for k, v in n["attrs"].items())
    n = {**n, "tag": SVG_TAGS.get(n["tag"], n["tag"])}
    if n["tag"] in Tree.VOID:
        return f"<{n['tag']}{a}>" if n["tag"] not in ("use", "path", "circle", "rect", "line", "polyline", "polygon", "stop") else f"<{n['tag']}{a}/>"
    return f"<{n['tag']}{a}>{''.join(outer(k) for k in n['kids'])}</{n['tag']}>"


def assets():
    rows = csv.DictReader((HERE / "webflow" / "assets.csv").open())
    return {pathlib.Path(r["file"]).stem: r["webflow_asset_id"] for r in rows if r["webflow_asset_id"]}


STATE_BASE = {"data-why-tab": "why_tab", "data-fare-tab": "fare_tab"}
SKIP_ATTR = {"class", "style", "id"}  # Webflow reserves `id`; it goes in as the domId setting
INLINE_TAGS = {"span", "strong", "em", "b", "i", "small", "br", "a", "time", "sup", "sub", "mark", "abbr", "code"}


def schema(n, ids, report):
    """Webflow element_schema for a parsed node. SVGs, sprite <use> and <details> internals stay native where possible."""
    if n["tag"] == "#text":
        t = re.sub(r"\s+", " ", n["text"])
        return {"type": "BY_CUSTOM_TAG", "custom_tag": "span", "set_text": {"text": t}} if t.strip() else None
    tag, at = n["tag"], n["attrs"]
    s = {}
    classes = [cls(c) for c in (at.get("class") or "").split() if c]
    if classes:
        s["set_style"] = {"style_names": classes}
    attrs = [{"name": k, "value": hosted(v or "")} for k, v in at.items() if k not in SKIP_ATTR and not (tag == "a" and k == "href")
             and not (tag == "img" and k in ("src", "alt")) and not (tag == "video" and k in ("src", "poster", "autoplay", "muted", "loop", "playsinline", "controls"))]
    if tag == "svg":
        return {"type": "HtmlEmbed", "settings": [{"key": "code", "static_text": {"value": hosted(outer(n))}}]}  # the svg keeps its own class
    if tag == "img":
        src = pathlib.Path(at.get("src", "")).stem
        aid = ids.get(src)
        if not aid:
            report.append(f"no asset id for img {at.get('src')}")
            return {"type": "HtmlEmbed", "settings": [{"key": "code", "static_text": {"value": hosted(outer(n))}}]}
        s.update({"type": "Image", "set_image_asset": {"image_asset_id": aid, "alt_text": at.get("alt", "")}})
    elif tag == "video":
        mux = json.loads((HERE / "webflow" / "mux.json").read_text()).get(pathlib.Path(at.get("src", "")).stem)
        if mux:  # islands/mux-video.js picks HLS or MP4 and sets the poster (Webflow reserves `poster`)
            attrs += [{"name": "data-dcb-mux", "value": mux["playback_id"]}]
        else:
            report.append(f"video not on Mux: {at.get('src')} (upload with tools/mux-upload.mjs)")
        s.update({"type": "DOM", "set_dom_config": {"dom_tag": "video"}})  # BY_CUSTOM_TAG video becomes Webflow's embed Video
    elif re.fullmatch(r"h[1-6]", tag):
        s.update({"type": "Heading", "set_heading_level": {"heading_level": int(tag[1])}})
    elif tag == "p":
        s["type"] = "Paragraph"
    elif tag == "a":
        href = at.get("href", "#")
        href = re.sub(r"^(index|download|sponsorship|faq|collectives|blog-post)\.html", lambda m: "/" if m.group(1) == "index" else f"/{m.group(1)}", href)
        s.update({"type": "LinkBlock", "set_link": {"link_type": "email" if href.startswith("mailto:") else "url", "link": href.replace("mailto:", "")}})
    elif tag == "button":  # BY_CUSTOM_TAG button becomes a Webflow Button, i.e. <a href="#">
        s.update({"type": "DOM", "set_dom_config": {"dom_tag": "button"}})
    elif tag in ("ul", "ol", "li"):  # BY_CUSTOM_TAG ul/ol becomes a Webflow List: always <ul>, plus 3 default empty <li>
        s.update({"type": "DOM", "set_dom_config": {"dom_tag": tag}})
    else:
        s.update({"type": "BY_CUSTOM_TAG", "custom_tag": tag})
    # Webflow has no standalone `is-active`/`is-current` (combo only), so a lone state class gets a base class
    if classes and all(c in ("is-active", "is-current") for c in classes):
        base = next((STATE_BASE[k] for k in at if k in STATE_BASE), None)
        if base:
            s["set_style"] = {"style_names": [base] + classes}
    elif tag == "button" and not classes:
        base = next((STATE_BASE[k] for k in at if k in STATE_BASE), None)
        if base:
            s["set_style"] = {"style_names": [base]}
    if attrs:
        s["set_attributes"] = {"attributes": attrs}
    if at.get("id"):
        s["settings"] = [{"key": "domId", "static_text": {"value": at["id"]}}]
    kids = n["kids"]
    texts = [k for k in kids if k["tag"] == "#text"]
    if kids and len(texts) == len(kids) and s["type"] not in ("Image",):
        s["set_text"] = {"text": re.sub(r"\s+", " ", "".join(k["text"] for k in kids)).strip()}
    else:
        ch = [c for c in (schema(k, ids, report) for k in kids) if c]
        if ch:
            s["children"] = ch
    return s


def used_classes():
    """Classes on the approved pages plus any the mockup JS adds at runtime (classList / className strings)."""
    used = {"smap_dot"}  # built by v2.js station map: zone.className.replace("board_zone", "smap_dot")
    for f in PAGES.glob("*.html"):
        for c in re.findall(r'class="([^"]*)"', f.read_text()):
            used.update(cls(x) for x in c.split())
    for js in [SITE / "mockup-v2/v2.js", SITE / "mockup-v3/v3.js", SITE / "mockup-v3/appsim.js"]:
        src = js.read_text()
        for m in re.findall(r"classList\.(?:add|remove|toggle|contains)\(([^)]*)\)", src):
            used.update(cls(x) for x in re.findall(r"['\"]([a-z][a-z0-9_-]*)['\"]", m))
        for m in re.findall(r"class(?:Name)?\s*=\s*['\"]([^'\"]+)['\"]", src):
            used.update(cls(x) for x in m.split())
        for m in re.findall(r'class=\\?"([^"\\]+)', src):
            used.update(cls(x) for x in m.split())
    return used


LEVELS = ["main", "medium", "small", "tiny"]  # desktop-first: each level inherits the ones before it


def cascade(rules):
    """For every multi-class chain on the pages, the CSS winner of each property two or more of its classes set.
    Webflow emits global classes in its own order, so the mockup's 'later rule wins' is lost; the chain's combo
    (more specific) carries the winners instead. Returns {chain: {level: {prop: value}}} (noPseudo only)."""
    chains = set()
    for f in PAGES.glob("*.html"):
        for c in re.findall(r'class="([^"]*)"', f.read_text()):
            names = [cls(x) for x in c.split() if not x.startswith("w-")]
            for i in range(2, len(names) + 1):
                chains.add(tuple(names[:i]))
    out = {}
    for chain in chains:
        members = set(chain)
        prev = {}
        for li, level in enumerate(LEVELS):
            win, setters = {}, {}
            for rchain, pseudo, bp, body, idx in rules:
                if pseudo != "noPseudo" or bp not in LEVELS[: li + 1] or not set(rchain) <= members:
                    continue
                key = (len(rchain), LEVELS.index(bp), idx)  # specificity, then later media block, then source order
                for k, v in body:
                    setters.setdefault(k, set()).add(rchain)
                    if k not in win or key >= win[k][0]:
                        win[k] = (key, v)
            vals = {k: v for k, (key, v) in win.items() if len(setters[k]) > 1}
            if level == "main":
                emit = vals
            else:
                emit = {k: v for k, v in vals.items() if prev.get(k) != v}
            merged = dict(prev); merged.update(vals)
            prev = merged
            if emit:
                out.setdefault(chain, {})[level] = emit
    return out


def cmd_styles():
    rules, left = parse_css()
    used = used_classes()
    dropped = sorted({c for ch, *_ in rules for c in ch if c not in used})
    rules = [r for r in rules if all(c in used for c in r[0])]
    resolved = cascade(rules)
    left = hosted(re.sub(r"@font-face\{[^}]*\}\n?", "", left))
    # Webflow wraps every code embed in div.w-embed; on rebuilt pages the wrapper must not take part in layout, so the
    # svg inside sits in the grid/flex exactly as in the mockup (the class lives on the svg, not the wrapper).
    left = "main .w-embed,.end_component .w-embed,.nav_component .w-embed{display:contents}\n" + left
    order, props = [], {}
    for chain, pseudo, bp, body, _ in rules:
        for i in range(1, len(chain) + 1):
            if chain[:i] not in props:
                props[chain[:i]] = {}
                order.append(chain[:i])
        props[chain].setdefault((bp, pseudo), []).extend(body)
    used_chains = set()
    for f in PAGES.glob("*.html"):
        for c in re.findall(r'class="([^"]*)"', f.read_text()):
            names = [cls(x) for x in c.split() if not x.startswith("w-")]
            for i in range(1, len(names) + 1):
                used_chains.add(tuple(names[:i]))
    extra = []
    for chain in sorted(used_chains, key=len):
        if chain not in props and not (len(chain) == 1 and chain[0] in LIVE_REUSE):
            props[chain] = {}
            order.append(chain)
            extra.append(chain)
    actions = []
    for chain in order:
        base = props[chain].get(("main", "noPseudo"), [])
        merged = dict(base)
        actions.append({"label": ".".join(chain), "create_style": {"name": chain[-1], **({"parent_style_names": list(chain[:-1])} if len(chain) > 1 else {}),
                                                                     "properties": [prop(k, v) for k, v in merged.items()]}})
    for chain in order:
        for (bp, pseudo), body in props[chain].items():
            if (bp, pseudo) == ("main", "noPseudo"):
                continue
            u = {"style_name": chain[-1], "properties": [prop(k, v) for k, v in dict(body).items()]}
            if len(chain) > 1:
                u["parent_style_names"] = list(chain[:-1])
            if bp != "main":
                u["breakpoint_id"] = bp
            if pseudo != "noPseudo":
                u["pseudo"] = pseudo
            actions.append({"label": f"{'.'.join(chain)}@{bp}:{pseudo}", "update_style": u})
    OUT.mkdir(exist_ok=True)
    fixes = []
    for chain, levels in sorted(resolved.items()):
        for level, vals in levels.items():
            u = {"style_name": chain[-1], "parent_style_names": list(chain[:-1]), "properties": [prop(k, v) for k, v in vals.items()]}
            if level != "main":
                u["breakpoint_id"] = level
            fixes.append({"label": f"{'.'.join(chain)}@{level}", "update_style": u})
    (OUT / "styles-cascade.json").write_text(json.dumps(fixes, indent=1))
    print(f"{len(fixes)} cascade fixes for multi-class chains -> build/styles-cascade.json")
    (OUT / "styles.json").write_text(json.dumps(actions, indent=1))
    (OUT / "styles-extra.json").write_text(json.dumps([a for a in actions if "create_style" in a and tuple(
        (a["create_style"].get("parent_style_names") or []) + [a["create_style"]["name"]]) in set(extra)], indent=1))
    print(f"{len(extra)} chains/classes with no CSS rule of their own -> build/styles-extra.json")
    fixes_css = (HERE / "styles" / "fixes.css").read_text()
    (HERE / "styles" / "site.css").write_text("/* Generated by tools/mock2wf.py from the approved mockup: rules Webflow classes can't express. Do not edit by hand; hand fixes go in fixes.css. */\n" + left + "\n" + fixes_css)
    creates = sum(1 for a in actions if "create_style" in a)
    print(f"dropped {len(dropped)} unused classes: {' '.join(dropped)}")
    print(f"{creates} styles, {len(actions) - creates} breakpoint/pseudo updates -> build/styles.json; site.css {len(left)} chars")


BLOCKS = ("section", "nav", "footer", "header")


def blocks(page):
    """Section-level nodes (any depth, not nested in another block) with the wrapper chain above each."""
    t = Tree()
    src = (PAGES / f"{page}.html").read_text()
    t.feed(re.search(r"<body[^>]*>(.*)</body>", src, re.S).group(1))
    out = []

    def walk(n, chain):
        for k in n["kids"]:
            if k["tag"] == "#text":
                continue
            if k["tag"] in BLOCKS:
                out.append((k, chain))
            elif k["tag"] not in ("script", "template"):
                walk(k, chain + [f"{k['tag']}.{(k['attrs'].get('class') or '').replace(' ', '.')}"])
    walk(t.root, [])
    return out


def cmd_list(page):
    for i, (k, chain) in enumerate(blocks(page)):
        print(i, " > ".join(chain) or "(body)", "|", k["tag"], k["attrs"].get("class"), k["attrs"].get("id") or "")


def cmd_section(page, n):
    node, chain = blocks(page)[int(n)]
    report = []
    sch = schema(node, assets(), report)
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{page}-{n}.json"
    out.write_text(json.dumps(sch, indent=1))
    print(f"{page} {n} [{' > '.join(chain) or 'body'}] <{node['tag']} class={node['attrs'].get('class')}> -> {out.name} ({len(json.dumps(sch))} chars)")
    for r in sorted(set(report)):
        print("  !", r)


if __name__ == "__main__":
    {"styles": lambda: cmd_styles(), "section": lambda: cmd_section(sys.argv[2], sys.argv[3]),
     "list": lambda: cmd_list(sys.argv[2])}[sys.argv[1]]()
