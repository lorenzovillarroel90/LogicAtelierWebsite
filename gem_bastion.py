"""Localized content and layouts for the standalone Gem Bastion TD pages."""

import json
from html import escape


BRAND = "GemBastionTD"
SLUG = BRAND.lower()
FAMILY = "gem-bastion"
ICON = "ios/GemBastionTD/App/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon.png"
THEME = {"accent": "#8EEAC1", "companion": "#FFC27A", "wash": "#E9F8F0", "ink": "#174A3F"}
GITHUB_POLICY = "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"

STYLES = """
.gem-hero { min-height: 0; }
.gem-hero-icon {
  width: min(100%, 26rem);
  height: auto;
  justify-self: center;
  border-radius: 16%;
  border: 1px solid color-mix(in srgb, var(--companion) 40%, transparent);
  box-shadow: 0 24px 70px rgba(0, 0, 0, .32);
}
@media (max-width: 850px) {
  .gem-hero-icon {
    width: min(100%, 16rem);
    justify-self: start;
  }
}
"""

TEXT = {
    "en": {
        "discover": "More games",
        "icon": "A glowing green gem set in a golden ring",
        "controls": "How do I play?",
        "save": "How do I save and resume?",
        "tips": "Is the game free?",
        "warning": "Leave out personal and payment details.",
        "privacy_intro": "How Gem Bastion TD handles game data, optional tips and requests for support.",
        "collection": "Data collection",
        "payments": "Optional tips",
        "github_policy": "GitHub Privacy Statement",
        "footer": "Free single-player tower defense for iPhone and iPad.",
    },
    "es": {
        "discover": "Más juegos",
        "icon": "Una gema verde luminosa engastada en un anillo dorado",
        "controls": "¿Cómo se juega?",
        "save": "¿Cómo guardo y continúo mi partida?",
        "tips": "¿El juego es gratis?",
        "warning": "Evita incluir datos personales o de pago.",
        "privacy_intro": "Cómo gestiona Gem Bastion TD los datos de juego, las propinas opcionales y las solicitudes de asistencia.",
        "collection": "Recogida de datos",
        "payments": "Propinas opcionales",
        "github_policy": "Declaración de privacidad de GitHub",
        "footer": "Defensa de torres gratuita para un jugador en iPhone y iPad.",
    },
    "fr": {
        "discover": "Autres jeux",
        "icon": "Une gemme verte lumineuse sertie dans un anneau doré",
        "controls": "Comment jouer ?",
        "save": "Comment sauvegarder et reprendre ma partie ?",
        "tips": "Le jeu est-il gratuit ?",
        "warning": "Évitez d’inclure des données personnelles ou de paiement.",
        "privacy_intro": "Comment Gem Bastion TD traite les données de jeu, les pourboires facultatifs et les demandes d’assistance.",
        "collection": "Collecte de données",
        "payments": "Pourboires facultatifs",
        "github_policy": "Déclaration de confidentialité de GitHub",
        "footer": "Jeu gratuit de défense de tours en solo sur iPhone et iPad.",
    },
    "it": {
        "discover": "Altri giochi",
        "icon": "Una gemma verde luminosa incastonata in un anello dorato",
        "controls": "Come si gioca?",
        "save": "Come si salva e si riprende la partita?",
        "tips": "Il gioco è gratuito?",
        "warning": "Evita di includere dati personali o di pagamento.",
        "privacy_intro": "Come Gem Bastion TD gestisce i dati di gioco, le mance facoltative e le richieste di assistenza.",
        "collection": "Raccolta dei dati",
        "payments": "Mance facoltative",
        "github_policy": "Informativa sulla privacy di GitHub",
        "footer": "Tower defense gratuito per un giocatore su iPhone e iPad.",
    },
    "de": {
        "discover": "Weitere Spiele",
        "icon": "Ein leuchtend grüner Edelstein in einer goldenen Fassung",
        "controls": "Wie spiele ich?",
        "save": "Wie speichere ich und spiele später weiter?",
        "tips": "Ist das Spiel kostenlos?",
        "warning": "Lass persönliche Daten und Zahlungsdaten weg.",
        "privacy_intro": "Wie Gem Bastion TD mit Spieldaten, freiwilligen Trinkgeldern und Supportanfragen umgeht.",
        "collection": "Datenerhebung",
        "payments": "Freiwillige Trinkgelder",
        "github_policy": "Datenschutzerklärung von GitHub",
        "footer": "Kostenloses Tower-Defense-Spiel für eine Person auf iPhone und iPad.",
    },
}


def load_game(source_root, languages, public_route, read_text):
    source = source_root / "AppStoreMetaData" / BRAND / "v1.0"
    game = {
        "brand": BRAND,
        "family": FAMILY,
        "theme": THEME,
        "screenshot_files": (),
    }
    fields = {"name": "app-name", "subtitle": "subtitle", "promo": "promotional-text", "description": "app-description"}
    for key, folder in fields.items():
        game[key] = {}
        for lang in languages:
            field = source / folder / f"{lang}.txt"
            value = read_text(field)
            if not value:
                raise ValueError(f"{field} must contain localized product copy.")
            game[key][lang] = value

    game["website"] = {}
    for lang in languages:
        landing = public_route(lang, SLUG)
        urls = {
            "marketing-url": landing,
            "privacy-policy-url": public_route(lang, SLUG, True),
            "support-url": landing + "#support",
        }
        for folder, url in urls.items():
            field = source / folder / f"{lang}.txt"
            if read_text(field) != url:
                raise ValueError(f"{field} must match the website route {url!r}.")

        field = source / "website-content" / f"{lang}.json"
        copy = json.loads(read_text(field))
        required = [copy.get(key) for key in ("controls", "save", "tips")]
        required.extend(copy["privacy"].get(key) for key in ("collection", "device", "payments", "support"))
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError(f"{field} must contain complete support and privacy text.")
        game["website"][lang] = copy

    return game


def discover_section(lang, card_html):
    heading = escape(TEXT[lang]["discover"])
    return f'''<section class="section compact-section" aria-labelledby="more-games-title">
  <h2 id="more-games-title">{heading}</h2>
  <div class="game-grid">{card_html}</div>
</section>'''


def product_page(app, lang, canonical, icon_url, markup, support_label):
    name = app["name"][lang]
    description = app["promo"][lang]
    jsonld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": name,
        "applicationCategory": "VideoGame",
        "operatingSystem": "iOS",
        "description": description,
        "image": icon_url,
        "url": canonical,
        "inLanguage": lang,
    }
    if app.get("store_live") and app.get("store_url"):
        jsonld["downloadUrl"] = app["store_url"]
    return {
        "title": f'{name} · {app["subtitle"][lang]}',
        "description": description,
        "content": product_content(app, lang, markup, support_label),
        "jsonld": jsonld,
    }


def product_content(app, lang, markup, support_label):
    labels = TEXT[lang]
    copy = app["website"][lang]
    faq = "\n".join(
        f'<details class="support-answer"><summary>{escape(labels[key])}</summary>'
        f'<div><p>{escape(copy[key])}</p></div></details>'
        for key in ("controls", "save", "tips")
    )
    return f'''<section class="app-hero">
  <div class="app-hero-grid gem-hero">
    <div class="app-hero-copy">
      <h1>{escape(app["name"][lang])}</h1>
      <p class="lede">{escape(app["promo"][lang])}</p>
      {markup["store_action"]}
    </div>
    <img class="gem-hero-icon" src="{escape(markup["icon_href"])}" width="512" height="512" alt="{escape(labels["icon"])}" fetchpriority="high">
  </div>
</section>
<section class="section" aria-labelledby="gameplay-title">
  <h2 id="gameplay-title">{escape(app["subtitle"][lang])}</h2>
  <div class="store-copy">{markup["description"]}</div>
</section>
<section class="section soft-section" id="support" aria-labelledby="support-title">
  <h2 id="support-title">{escape(support_label)}</h2>
  <div class="support-list">{faq}</div>
  {markup["contact"]}
</section>'''


def privacy_page(app, lang, common, support_label, support_link):
    title = common["privacy_title"].format(name=app["name"][lang])
    return {
        "title": title,
        "description": TEXT[lang]["privacy_intro"],
        "content": privacy_content(app, lang, common, title, support_label, support_link),
    }


def privacy_content(app, lang, common, title, support_label, support_link):
    labels = TEXT[lang]
    policy = app["website"][lang]["privacy"]
    sections = (
        ("collection", labels["collection"], policy["collection"]),
        ("device", common["app_heading"], policy["device"]),
        ("payments", labels["payments"], policy["payments"]),
        ("website", common["website_heading"], common["website_body"]),
        ("support", support_label, policy["support"]),
    )
    navigation = "\n".join(f'<a href="#{key}">{escape(heading)}</a>' for key, heading, _ in sections)
    sections_html = []
    for key, heading, text in sections:
        link = support_link if key == "support" else ""
        sections_html.append(
            f'<section class="policy-section" id="{key}">'
            f'<h2>{escape(heading)}</h2><p>{escape(text)}</p>{link}</section>'
        )
    return f'''<section class="page-hero"><div class="narrow">
  <h1>{escape(title)}</h1>
  <p class="lede">{escape(labels["privacy_intro"])}</p>
</div></section>
<div class="section policy-wrap">
  <div class="policy-layout">
    <nav class="policy-nav" aria-label="{escape(common["privacy"])}">
      {navigation}
      <a href="#links">{escape(common["links_heading"])}</a>
    </nav>
    <div>
      {"".join(sections_html)}
      <section class="policy-section" id="links">
        <h2>{escape(common["links_heading"])}</h2>
        <ul>
          <li><a href="https://www.apple.com/legal/privacy/">{escape(common["apple_policy"])}</a></li>
          <li><a href="{GITHUB_POLICY}">{escape(labels["github_policy"])}</a></li>
        </ul>
      </section>
    </div>
  </div>
</div>'''
