"""List every local media file the approved build references, for upload to Webflow Assets.
Scans the built mockup-v3-ian pages (the variant Chris approved 2026-10-29) plus the v2/v3 CSS and JS and the app sim. Writes webflow/assets.csv.
Run: python3 -I tools/assets.py (rebuild the mockups first: bash ../../projects/launch-site/deploy.sh builds them)."""
import csv
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent.parent
SITE = HERE.parent.parent / "projects" / "launch-site"
V3 = SITE / "mockup-v3"
BUILT = SITE / "mockup-v3-ian"  # approved variant; its pages load v3 CSS/JS from mockup-v3/
SOURCES = [p for p in BUILT.glob("*.html")] + [SITE / "mockup-v2" / "v2.css", SITE / "mockup-v2" / "v2.js", V3 / "v3.css", V3 / "v3.js",
                                             V3 / "appsim.css", V3 / "appsim.js"]
REF = re.compile(r"""(?:src|href|poster|data-[a-z-]+)=["']([^"'#?]+\.(?:jpe?g|png|webp|gif|svg|mp4|webm|ttf|otf|woff2?))|url\(["']?([^"')#?]+\.(?:jpe?g|png|webp|gif|svg|ttf|otf|woff2?))|["']([^"'\s]+\.(?:jpe?g|png|webp|mp4|svg))["']""", re.I)
FOLDER = [("brand/", "brand"), ("sponsor-", "sponsors"), ("part-", "bike"), ("bike", "bike"), ("ig/", "film-and-photos"),
          ("why-", "film-and-photos"), ("lineart", "illustration"), ("local/", "illustration"), ("tower", "stations"), ("station", "stations"), ("ian/", "film-and-photos"),
          ("collectives/", "collectives"), ("related/", "blog")]


def folder(path):
    for key, name in FOLDER:
        if key in path:
            return name
    return "misc"


def main():
    used = {}
    for src in SOURCES:
        page = src.name if src.suffix == ".html" else "(css/js)"
        for m in REF.finditer(src.read_text(errors="ignore")):
            ref = next(g for g in m.groups() if g)
            if ref.startswith(("http", "data:", "//")):
                continue
            f = (src.parent / ref).resolve()
            if f.exists():
                used.setdefault(f, set()).add(page)
    rows = sorted(used.items(), key=lambda kv: str(kv[0]))
    out = HERE / "webflow" / "assets.csv"
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "kb", "webflow_folder", "used_on", "webflow_asset_id"])
        for f, pages in rows:
            rel = str(f.relative_to(SITE)) if SITE in f.parents else str(f)
            w.writerow([rel, round(f.stat().st_size / 1024), folder(rel), " ".join(sorted(pages)), ""])
    total = sum(f.stat().st_size for f, _ in rows) / 1024 / 1024
    print(f"{len(rows)} files, {total:.1f} MB -> {out.relative_to(HERE)}")


main()
