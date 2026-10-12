# Puzzle worlds website

Static marketing, support and privacy pages for the ten LogicAtelier puzzle
games and all seven PocketColor adventures: Reedwake, Afterlight Run, Mothline, Brassbird, Hushshore, Gustglass and Spindlewatch.

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
screenshots for each puzzle app, approved six-shot PocketColor matrices, and the
matching app icons. Product/help/privacy routes can be published before new game
media is approved: these pages show their real icon and approved localized copy,
without an empty gallery, screenshot promise or placeholder. `APPROVED_POCKET_MEDIA`
is the explicit reviewed-matrix owner; Only Reedwake remains enabled while revised paid-content disclosure products for the six other games await renewed lead review. Add a
game there after lead approval of all six shots in all five languages. Missing or
empty approved sources still fail before replacing `site/`. Run
`python3 Website/build.py --require-all-media` for the separate final all-game media
gate; this stricter check does not itself approve a gallery. Reedwake's screenshot order is `01_core`, `02_world`, `03_world`,
`04_depth`, `05_solved`, `06_home`. It creates web-sized JPEG and 512px PNG
derivatives without modifying source assets. The generated `site/` output
remains committed so GitHub Pages does not need a build step.

## Content and localization rules

- Keep product names, subtitles, descriptions, and screenshot headlines in
  sync with `../AppStoreMetaData/<Brand>/v1.0/`. PocketColor cards, navigation,
  headings and shared help/privacy labels use the approved locale’s `app-name`
  through `public_name`; internal brand folders/slugs are only routing identities.
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
- Game-specific control, free/full-content and save text for the six additional games lives beside their listing in `website-content/<locale>.json`. The generator shares support/privacy layout and common verified StoreKit facts, while Reedwake retains its approved terms. Afterlight Run discloses local records/settings and no saved mid-run campaign.
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

## Approved English gameplay media

`approved-videos.json` is the single hash-pinned video owner. One English edit is
shared across all five languages with localized “English gameplay” labels, native
HTML controls, a real frame-zero poster, `preload="metadata"`, and no autoplay.
Only movies explicitly accepted by the lead may enter that map. Gallery acceptance
is independent; adding a video never approves screenshots or App Store availability.

Original delivery MP4s, detailed sidecars, traces and QA images remain outside the
parent repository, following its video workflow. A narrow authorized exception
allows lead-approved, Website-owned web movie/poster derivatives and sanitized
provenance as public product artifacts in this separate Website repository. These
are durable inputs under `media/<game>/`, copied into `site/assets/videos/<game>/`.
Do not copy original traces, absolute private paths or contact sheets into either
owner. Provenance truthfully identifies the offline/native-shell composite, paired
music or silence, paid-content disclosure, accepted source hashes and derivative
hashes; it never calls this device-captured footage or App Store submission-ready.

Import an accepted delivery once with an existing FFmpeg executable:

```sh
python3 Website/build.py --import-approved-videos \
  --video-source-root /absolute/external/delivery-root \
  --ffmpeg /absolute/existing/ffmpeg
python3 Website/build.py
```

The explicit import verifies each new or changed external movie/report against
the reviewed hashes before replacing owned inputs. Already valid durable movies
are retained, so importing a later game never requires prior temporary deliveries. It stream-copies the accepted picture/audio
into a faststart MP4, extracts the first decoded frame as a JPEG poster, checks full
decoding, and records safe source/derivative provenance. It does not publish or
replace `site/`. Regular builds need neither FFmpeg nor the original delivery
folders; they verify every durable input hash before staging. Changed or missing
approved originals during import, or changed/missing owned media during an ordinary
build, fail before replacing the deployable artifact. Adding later movies uses this
same owner and concrete lead review, followed by the authorized deployment workflow.

## Shared public support

[SUPPORT.md](SUPPORT.md) records the owner’s standing Reedwake contact choice for
all seven PocketColor games. The existing public repository issue-reporting link
is exposed on every localized game support and privacy page. Never ask the owner
for that default again, invent an email or publish private App Review contacts.

`approved-videos.json` can explicitly set `publicationEnabled: false` for a lead
media hold. Durable movie/poster/provenance inputs remain intact, while generation
omits all candidate movie references. Re-enable only after the concrete media
review; new galleries likewise require revised, approved product PNGs.
