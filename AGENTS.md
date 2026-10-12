# Website guidance

`site/` is a committed, dependency-free GitHub Pages artifact. Keep website
work isolated to this submodule and do not change the parent iOS project while
editing it.

## Source of truth

- Product names, subtitles, descriptions, promotional text, and screenshot
  headlines come from `../AppStoreMetaData/<Brand>/v1.0/` for both the ten
  LogicAtelier puzzle games and PocketColor games.
- Puzzle screenshot sources are four iPhone captures at
  `../AppStoreScreenshots/<Brand>/v1.0/iPhone/<locale>/`. PocketColor game
  pages use reviewed six-shot matrices; only games in `APPROVED_POCKET_MEDIA`
  render a gallery. Complete product/help/privacy copy and icons may ship before
  new media approval, with no placeholder or empty gallery promise. Reedwake's
  approved sequence is `01_core`,
  `02_world`, `03_world`, `04_depth`, `05_solved`, `06_home`. The generator
  makes web-sized derivatives; it does not synthesize or replace storefront
  shots.
- LogicAtelier icons come from their project asset catalogs. PocketColor icons
  come from `../ios/PocketColor/ios-projects/<Brand>/App/Assets.xcassets/`.
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
- Keep each app's privacy wording aligned with its shipped configuration. The
  LogicAtelier puzzle games use local progress/settings, Google Mobile Ads for
  free-user hints and selected interstitials, and StoreKit for Pro. PocketColor
  games such as Reedwake have local progress, no ads/accounts/analytics, and
  StoreKit only for an approved one-time entitlement. In both families the app
  does not receive payment-card data. Never copy the ad disclosure to a game
  that does not ship advertising.
- Localized app pages, support content, and privacy pages must use the approved
  locale's copy. Enabled galleries must use the complete reviewed screenshot
  matrix. PocketColor terminology should follow
  the game's reviewed `*.xcstrings` catalog. Do not silently machine-translate
  established product terminology.

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
python3 build.py --require-all-media # separate final matrix gate
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
