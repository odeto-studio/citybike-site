# citybike-site

Webflow build source for drifterscitybike.com, launch-week rebuild (Option 3 Showcase, chosen by Ian 2026-10-29).
Project spine: `../../projects/launch-site/PROJECT.md` (scope, approvals, status). Build order: `../../projects/launch-site/BUILD.md`.

The design source is the approved mockup, not this repo:
`../../projects/launch-site/mockup-v2/` (shared site, sections, CSS, JS) + `mockup-v3/` (bike tour on top of v2).
Refinements happen in the mockup first; this repo is what ships into Webflow once a section is locked.

## Layout

| Path | What |
|---|---|
| `islands/` | Vanilla JS behavior modules, one per job, configured by `data-dcb-*` attributes on native Webflow elements. Contract and port status: `islands/README.md` |
| `styles/` | CSS Webflow's Designer can't express (keyframes, `@property`, complex selectors), shipped inside an island, never in an embed |
| `webflow/variables.yaml` | Mockup tokens mapped to Webflow variables (live site naming) |
| `webflow/classes.md` | Mockup class to Client-First class map |
| `webflow/assets.csv` | Every media file the v3 build uses, with size and target asset folder. Regenerate: `python3 -I tools/assets.py` |
| `registered/` | Webflow script registry log: what is registered, version, SRI, which pages |
| `tools/sri.py` | Bundles `islands/*.js` into `dist/` and prints the sha384 SRI for each |

## Rules
- Target site: Ian's live site `676f05e19f0c2d276a11bbcd` via MCP `webflow-drifters-citybike` (the launch-site scope overrides the staging-only rule). Publish to `*.webflow.io` only; production on Chris's explicit go.
- First publish ships Ian's unpublished 9/9 and 9/18 home-page edits too: diff and ask him first.
- Client-First naming (`../../projects/site-rider-portal/working/build-rules.md` §1-4). No inline styles, no auto-named classes.
- Behavior never goes in an HTML embed (Webflow escapes quotes, inline scripts cap at 10k chars). Hosted script + SRI.
- Registered scripts can't be updated in place: register `name_N+1`, then reattach.
