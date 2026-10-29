# Islands

Each island is a self-contained IIFE: it finds its `data-dcb-*` root, does nothing if the root is absent, and never throws on a page without it.
GSAP 3.12.5 + ScrollTrigger load once site-wide (cdnjs, before the islands). Every scroll-driven island honors `prefers-reduced-motion` and leaves the section readable with JS off.

Mockup attributes (`data-why`, `data-tour`, ...) get the `dcb-` prefix on port: `data-why` becomes `data-dcb-why`.
Source line refs are `mockup-v2/v2.js` and `mockup-v3/v3.js` as of 2026-10-29; port only after the section is locked in the v3 refinement pass.

| Island | Attribute root | Pages | Source | Status |
|---|---|---|---|---|
| `app-link.js` | `data-dcb-app-link` (any link) | all | v2.js 4-10 | ported; store URLs pending from Ian |
| `nav.js` | `.nav_component` + hero | all | v2.js 12-27 | todo. Could be a Webflow scroll interaction instead; decide at build |
| `reveal.js` | `.reveal` | all | v2.js 28-38 | todo. Prefer native Webflow interaction; island only if the stagger can't be matched |
| `why.js` | `data-dcb-why` (tabs + panes) | home | v2.js 421-434 | todo. Could be native Webflow Tabs |
| `stations-sign.js` | `data-dcb-docks` (tower, sign, line, trip, beats) | home | v2.js 320-354 | todo. Pinned; depends on `_sign.svg` as an uploaded asset |
| `station-map.js` | `data-dcb-smap`, `data-dcb-sscroll`, items with `data-x`/`data-y` | home | v2.js 355-409 | todo. 14 stations; CMS-bind the list later |
| `fare-card.js` | `data-dcb-fare` (tabs, range, plans, outputs) | home, download | v2.js 181-220 | todo. Prices pending Ian's confirm |
| `app-phone.js` | `data-dcb-appdl` | home | v2.js 410-420 | todo |
| `timeline-rider.js` | `data-dcb-ruler-actors` | home | v2.js 268-319 | todo |
| `bike-tour.js` | `data-dcb-tour` (stage, cam, bike, focus, beats, steps, counts, fit) | home | v3.js 1-156 + fit graphic v2.js 63-104 | todo. Largest island; phone keys and desktop keys both |
| `rail.js` | `data-dcb-rail` | home | v3.js 157-end | todo |
| `faq-search.js` | `data-dcb-faq-search`, groups, topics | faq | v2.js 105-126 | todo. FAQ items come from the General FAQs CMS |
| `fit-text.js` | `data-dcb-fit-text` (footer line) | all | v2.js 435-443 | todo |
| `scroll-order.js` | none (sorts ScrollTriggers; smooth-scrolls anchor links; refreshes after fonts and re-lands a #deep link) | home | v2.js 444-468 | todo. Load last. Never pair with CSS `scroll-behavior:smooth` or Webflow's smooth-scroll setting: it breaks ScrollTrigger's measuring and pins the station tower early |

Not ported (mockup only, or cut from v3): notes toggle, review bar, blog before/after, hotspots, fleet tiles, gauge, slot reels, route, image takeover.

Blog rich-text image fix is CSS, not JS: goes in the site's custom CSS (see `../styles/`).
