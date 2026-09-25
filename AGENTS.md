# Website guidance

`site/` is a committed, dependency-free GitHub Pages artifact. Keep website
work isolated to this submodule and do not change the parent iOS project while
editing it.

## Source of truth

- Product names, subtitles, descriptions, promotional text, and screenshot
  headlines come from `../AppStoreMetaData/<Brand>/v1.0/`.
- Screenshot sources are the four iPhone captures at
  `../AppStoreScreenshots/<Brand>/v1.0/iPhone/<locale>/`.
- Icons come from the matching iOS app asset catalog.
- Run `python3 build.py` to regenerate deployable output after source changes.

## Public content

- Never show the collection's internal studio name in user-facing copy.
- Never invent App Store availability, prices, ratings, reviews, awards,
  release dates, or support addresses. Apps currently use localized
  “Coming soon on the App Store” text without a link.
- `APP_STORE_IDS` contains only verified numeric IDs; `build.py` derives a
  `store_url` only when an ID exists. Apps without a verified ID must keep the
  ID and URL absent. Every app currently has `store_live: False`. After a
  listing is live, enable it only once its ID and URL are verified. The
  generator must render a CTA and JSON-LD `downloadUrl` only when both the
  live switch and verified URL are present.
- Keep the app privacy wording aligned with the evidence in the iOS project:
  local progress/settings, no account, Google Mobile Ads for rewarded hints
  and selected completion interstitials for free users, StoreKit entitlement
  state for the one-time Pro purchase, and no payment-card data received by
  the app. Do not imply all ads are personalized or non-personalized.
- Localized app pages and privacy pages must use the approved locale's copy and
  screenshot matrix. Do not silently machine-translate established product
  terminology.

## SEO and accessibility

Every public page needs one useful `h1`, distinct title/description, canonical,
reciprocal `hreflang` including `x-default`, OpenGraph metadata, semantic
landmarks, descriptive image alternatives, visible keyboard focus, and a
responsive layout. Keep important facts in HTML. Use JSON-LD only for facts
visible on that page. Keep `robots.txt`, `sitemap.xml`, `404.html`, and
`app-ads.txt` valid when routes change.

## Validation

```sh
python3 build.py
python3 -m http.server 4173 --directory site
```

Check page/file counts, local `href`/`src` targets, canonical and alternate
routes, image dimensions, and the exact trailing-newline `app-ads.txt` line.
Do not commit temporary screenshots or contact sheets.

## Deployment

`.github/workflows/deploy-pages.yml` deploys `site/` on pushes to `main` and
manual dispatch. Keep Pages permissions and concurrency intact. Do not add a
runtime dependency or a separate build pipeline without owner approval.

## AdMob declaration hosting

Keep the exact declaration in `site/app-ads.txt` at the deployed project path
`https://lorenzovillarroel90.github.io/LogicAtelierWebsite/app-ads.txt` for
portability and future custom-domain use. The current GitHub Pages setup is
authoritative at the hostname root,
`https://lorenzovillarroel90.github.io/app-ads.txt`, which is mirrored/deployed
from the separate root user Pages repository. All app-specific marketing URLs
use the same `lorenzovillarroel90.github.io` hostname; AdMob strips their
paths, so it discovers the root declaration rather than an app route. A P1
release check is that the root URL returns HTTP 200 as plain text with the exact
seller declaration.
