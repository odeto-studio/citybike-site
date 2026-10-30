# Registered scripts (Webflow script registry)

Log of every script registered on site `676f05e19f0c2d276a11bbcd` via `data_scripts_tool`.
Hosted display names are alphanumeric + spaces ("DCB Bike Tour 1"); Webflow derives the id (`dcb_bike_tour_1`).
Registered scripts can't be updated in place: register `_N+1`, attach it, leave the old one registered and unused.
The approved mockup JS ships as one bundle (`tools/port-js.py` -> `islands/site.js`), served from jsDelivr pinned to a commit: `https://cdn.jsdelivr.net/gh/odeto-studio/citybike-site@<sha>/islands/site.js`. Mockup-only CSS selectors ship inline in each rebuilt page's head code from `styles/site.css`.

| Script id | Version | Island(s) | SRI | Pages | Registered |
|---|---|---|---|---|---|
| `gsap` | 3.12.5 | GSAP core (cdnjs) | sha384-g4NTh/Iv5PPU4xPyhEWqPcwtNXOvdaDI8LLnyYfyNZOjKJeYQyjzQ9X5275eBjpt | home, download (footer, before dcbsite) | 2026-10-29 |
| `gsapscrolltrigger` | 3.12.5 | ScrollTrigger (cdnjs) | sha384-Z3REaz79l2IaAZqJsSABtTbhjgOUYyV3p90XNnAPCSHg3EMTz1fouunq9WZRtj3d | home, download (footer, after gsap) | 2026-10-29 |
| `dcbsite` | 1.0.0 | `islands/site.js` @ 4ce4d99 (v2 + v3 + appsim + app-link + mux-video) | sha384-cmGvdMuai1+60RU0E473rm6xEnhvA333cHLKnQUVg3vWnQHk1tj8QuWxHywXSSLn | all rebuilt pages (footer, last) | 2026-10-29 |
| `dcbsite` | 1.0.6 | `islands/site.js` @ 2f9cd7f (Sponsorship hero film on Mux: muted loop + on-page player; Collectives cards for the CMS list) | sha384-8TDn+0I2Kp5xN/CKaCtrsx5XBO2fWtaMiP/CRXZwpFqhBCM2BXjKSx7iU4ktGYjG | home, download, sponsorship, collectives, faq (footer, last) | 2026-10-29 |
| `dcbsite` | 1.0.7 | `islands/site.js` @ 924f6d3 (Mux MP4 fallback when HLS errors: Chrome says "maybe" to HLS and fails it; film player too) | sha384-Oelt4DoQJoDbIi5IlE7/x2tc/7hzZlGKO4eESDeasn9jOGtoLhbr8soeFAE9dMXf | home, download, sponsorship, collectives, faq (footer, last) | 2026-10-30 |
| `dcbsite` | 1.0.8 | `islands/site.js` @ 5eb0f9f (Google Play pending: Android keeps /download; Play badges get .is-soon "Google Play coming soon" overlay on hover/focus/tap) | sha384-7qAt9YtgToxAFokb8vS3mi1LdazlxfiZYgFcc2vrDS7khJISQJgYZUf05xPpRHp3 | home, download, sponsorship, collectives, faq (footer, last) | 2026-10-30 |
