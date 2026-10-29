# Mockup class -> Client-First class

Filled section by section during the build. The mockup uses short names (`docks`, `appdl`, `lc`); Webflow gets the Client-First name.
Page structure is always `page-wrapper` > `main-wrapper` > `section_<name>` > `padding-global` > `container-large` > `padding-section-*` > component.

| Mockup | Webflow | Notes |
|---|---|---|
| `section bg-paper` | `section_<name>` + `background-color-paper` utility | background as utility, never on the section class |
| `section bg-ink` | `section_<name>` + `background-color-black` | |
| `hero_component is-cover` | `section_home-hero` / `home-hero_*` | film on the right edge, curtain over it |
| `why` | `section_why-ride` / `why-ride_*` | |
| `docks` | `section_station-sign` / `station-sign_*` | pinned sequence over `_sign.svg` |
| `smap` / stations list | `section_stations` / `station-map_*`, `station-list_*` | |
| fare card | `fare-card_*` (component: Fare Card) | used on home + download |
| `appdl` | `section_get-the-app` / `app-phone_*` | |
| `tour` | `section_bike-tour` / `bike-tour_*` | v3 |
| `story` | `section_story` / `story_*` | timeline rider in `story_ruler` |
| `comm` | `section_community` / `community_*` | |
| `sponsors` | `section_sponsors` / `sponsor-row_*` (component: Sponsor Row) | |
| `nav_component` | existing live navbar component, restyled | check live definition before editing (shared) |
| `footer_component` | existing live footer component | |
| `display is-l`, `h2`, `h3` | `heading-style-h1/h2/h3` | match live heading styles first |
| `lede` | `text-size-large` | |
