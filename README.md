# Puzzle worlds website

Static marketing, support and privacy pages for the ten LogicAtelier puzzle
games and PocketColor adventures, beginning with Reedwake.

## Deployment

The deployable artifact is committed under `site/`. GitHub Pages is configured
by `.github/workflows/deploy-pages.yml` and publishes `site/` from the `main`
branch. The public base URL is:

`https://lorenzovillarroel90.github.io/LogicAtelierWebsite/`

There is no runtime framework, external JavaScript, analytics, cookie banner,
or web font. `site/app-ads.txt` is intentionally at the artifact root.

### AdMob declaration hosting

This project keeps a portable deployment copy at
`https://lorenzovillarroel90.github.io/LogicAtelierWebsite/app-ads.txt`, with
the exact required line. The current GitHub Pages setup's authoritative AdMob
discovery URL is the hostname-root declaration at
`https://lorenzovillarroel90.github.io/app-ads.txt`; it is mirrored/deployed
from the separate root user Pages repository, not from this project workflow.
All app-specific marketing URLs share the `lorenzovillarroel90.github.io`
hostname, but AdMob strips their paths and requests the hostname root. Keep the
project copy for portability and custom-domain deployment; do not treat the
project-path copy as a replacement for the current root declaration.

## Rebuilding

From the parent repository on macOS:

```sh
python3 Website/build.py
```

The generator reads approved App Store metadata, four localized iPhone
screenshots for each puzzle app, six for each PocketColor game, and the matching
app icons. Reedwake's screenshot order is `01_core`, `02_world`, `03_world`,
`04_depth`, `05_solved`, `06_home`. It creates web-sized JPEG and 512px PNG
derivatives without modifying source assets. The generated `site/` output
remains committed so GitHub Pages does not need a build step.

## Content and localization rules

- Keep product names, subtitles, descriptions, and screenshot headlines in
  sync with `../AppStoreMetaData/<Brand>/v1.0/`.
- Every language has the puzzle hub, the app pages, and matching privacy pages.
  PocketColor landing pages include a localized help section; Reedwake's
  support URL points to its landing page. Keep canonical URLs, reciprocal
  `hreflang`, sitemap entries, image locale, and internal links in step when
  adding or changing a route.
- Do not add App Store links until an app is actually published. Use the
  localized coming-soon label for unreleased apps.
- Verified numeric App Store IDs are kept in `APP_STORE_IDS`; the generator
  derives `store_url` only when an ID exists. Apps without a verified ID must
  keep both ID and URL absent. Every app currently has `store_live: False`.
  After a listing is live, enable that app only after its ID and URL are
  verified. The generator emits the CTA and JSON-LD `downloadUrl` only when
  both the live switch and verified URL are present.
- Privacy wording must remain conservative and factual for each app family.
  LogicAtelier puzzle games disclose their ad and Pro services. Reedwake has
  local progress/settings, no ads/accounts/analytics, and StoreKit for the
  one-time full-game unlock; the app does not receive payment-card data.
- Do not add trackers, forms, cookies, external runtime dependencies, invented
  ratings, prices, reviews, awards, or release dates.

## Local smoke check

```sh
cd Website
mkdir -p .preview/LogicAtelierWebsite
cp -R site/. .preview/LogicAtelierWebsite/
python3 -m http.server 4173 --directory .preview
```

Open `http://localhost:4173/LogicAtelierWebsite/`, an app page, and a
non-English privacy route. Remove `.preview/` after the check. Keep
`prefers-reduced-motion: reduce` enabled when checking the reduced-motion path.
