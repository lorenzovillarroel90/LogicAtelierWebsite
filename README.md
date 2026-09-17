# Puzzle worlds website

Static marketing and privacy pages for Evenbeam, Knotide, Pipebloom, Rayfold,
Laneweave, and Shaplet.

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

The generator reads only approved App Store metadata, the four localized iPhone
screenshots for each app, and the app icons. It creates 720px-wide JPEG web
derivatives and 512px PNG icon derivatives without modifying source assets.
The generated `site/` output remains committed so GitHub Pages does not need a
build step.

## Content and localization rules

- Keep product names, subtitles, descriptions, and screenshot headlines in
  sync with `../AppStoreMetaData/<Brand>/v1.0/`.
- Every language has a hub, six app pages, and six matching privacy pages.
  Keep canonical URLs, reciprocal `hreflang`, sitemap entries, image locale,
  and internal links in step when adding or changing a route.
- Do not add App Store links until an app is actually published. Use the
  localized coming-soon label for unreleased apps.
- Future App Store IDs and canonical URLs are kept in `APP_STORE_IDS` and the
  `store_url` field in `build.py`. Each app also has one `store_live` switch,
  currently `False`; after its listing is live, change only that field to
  `True`, add/verify the localized live CTA label if needed, and rebuild. The
  generator then exposes the canonical URL in the CTA and JSON-LD. Never
  enable it for an unpublished listing.
- Privacy wording must remain conservative and factual: local progress and
  settings, Google Mobile Ads for free-user rewarded hints and selected
  completion interstitials, StoreKit entitlement state, and no payment-card
  data in the app.
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
