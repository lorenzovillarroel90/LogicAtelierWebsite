# PocketColor public support

## Standing owner decision

All seven PocketColor games reuse Reedwake’s canonical **public support contact**
by default. The owner requested the same public contact as Reedwake on
2026-10-12. Because the previous Reedwake page had FAQs only, the lead selected
and verified the existing owner-controlled repository’s public issue-reporting
channel. This does not imply that the human directly chose GitHub. Do not ask
for a support contact again unless the owner specifically requests a change. Never invent an
email address or publish private App Review contacts or `.env` values.

- Canonical shared support landing: https://lorenzovillarroel90.github.io/LogicAtelierWebsite/reedwake/#support
- Direct public contact: https://github.com/lorenzovillarroel90/LogicAtelierWebsite/issues/new
- Public reports: https://github.com/lorenzovillarroel90/LogicAtelierWebsite/issues
- Code owner: `PUBLIC_SUPPORT_URL` and the five-language `SUPPORT_TEXT` in
  [build.py](build.py). Every game’s localized product/help and privacy page uses
  the same contact component. Game-specific FAQs and existing App Store Connect
  support URLs remain local to each game; their contact destination is shared.

Reports are public and require a GitHub account. The website explains this before
the link. No report is created automatically and no app data is transmitted by
rendering the link. Playing the games still requires no account.

## Verified provenance — 2026-10-12

Reedwake’s previously published website had FAQs and no public email or `mailto`
contact. Read-only GitHub repository inspection verified that the existing
`lorenzovillarroel90/LogicAtelierWebsite` repository is public, has issues enabled,
is not archived and is not disabled. Its issue list returned HTTP 200; anonymous
issue creation redirected to the normal GitHub login page (HTTP 200). This is the
existing owner-controlled repository, not invented hosting or a private review
email. The lead approved adding this direct contact to Reedwake and all six peers.

[Apple’s App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/#developer-information)
require an easy contact method in the app and its Support URL. Website publication
is still verified separately from native-app adoption and App Store readiness.
