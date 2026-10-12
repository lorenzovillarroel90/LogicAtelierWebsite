#!/usr/bin/env python3
"""Build the dependency-free GitHub Pages site from approved repository assets.

The generated files in site/ are the deployment artifact.  Run this script from
macOS (where sips is available) after changing approved metadata or screenshots.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import posixpath
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEBSITE = Path(__file__).resolve().parent
SITE = WEBSITE / "site"
BASE = "https://lorenzovillarroel90.github.io/LogicAtelierWebsite/"
LANGS = ["en", "es", "fr", "it", "de"]
NON_EN = ["es", "fr", "it", "de"]
BRANDS = ["Evenbeam", "Knotide", "Pipebloom", "Rayfold", "Laneweave", "Shaplet", "Driftlings", "Overprint", "Rollmark", "Sproutbound"]
SLUGS = [b.lower() for b in BRANDS]
POCKET_BRANDS = ["Reedwake", "AfterlightRun", "Mothline", "Brassbird", "Hushshore", "Gustglass", "Spindlewatch"]
POCKET_SLUGS = [brand.lower() for brand in POCKET_BRANDS]
# Lead-approved complete five-language storefront matrices only. Add a game
# after its product media review; source file presence does not imply approval.
# New game galleries remain held until revised purchase-disclosure products
# receive complete localized lead acceptance. Preserve Reedwake’s active media.
APPROVED_POCKET_MEDIA = {"Reedwake"}
PUZZLE_SCREENSHOT_FILES = ("01_core", "02_depth", "03_solved", "04_home")
POCKET_SCREENSHOT_FILES = ("01_core", "02_world", "03_world", "04_depth", "05_solved", "06_home")
APP_STORE_IDS = {
    "pipebloom": "6812988605",
    "knotide": "6812988563",
    "shaplet": "6812988920",
    "rayfold": "6812989257",
    "laneweave": "6812991110",
    "evenbeam": "6812989398",
    "reedwake": "6819999218",
    "afterlightrun": "6819997915",
    "mothline": "6820000608",
    "brassbird": "6820001790",
    "hushshore": "6820003410",
    "gustglass": "6821880430",
    "spindlewatch": "6821881825",
}
STORE_LABELS = {
    "en": "Open on the App Store",
    "es": "Abrir en el App Store",
    "fr": "Ouvrir sur l’App Store",
    "it": "Apri sull’App Store",
    "de": "Im App Store öffnen",
}

THEMES = {
    "evenbeam": {"accent": "#B4DE8D", "companion": "#61E4C5", "wash": "#F1F9E8", "ink": "#28413A"},
    "knotide": {"accent": "#83C8FF", "companion": "#BAABFF", "wash": "#EDF7FF", "ink": "#1F3E5A"},
    "pipebloom": {"accent": "#61E4C5", "companion": "#83C8FF", "wash": "#E8FBF6", "ink": "#195148"},
    "rayfold": {"accent": "#FF8AA5", "companion": "#BAABFF", "wash": "#FFF0F3", "ink": "#573346"},
    "laneweave": {"accent": "#FFC178", "companion": "#83C8FF", "wash": "#FFF6E8", "ink": "#5A4129"},
    "shaplet": {"accent": "#BAABFF", "companion": "#FF8AA5", "wash": "#F4F1FF", "ink": "#463A68"},
    "driftlings": {"accent": "#A6E5B8", "companion": "#83C8FF", "wash": "#EDF8F1", "ink": "#294C49"},
    "overprint": {"accent": "#F47B58", "companion": "#FFC45B", "wash": "#FFF2E8", "ink": "#57392F"},
    "rollmark": {"accent": "#BAABFF", "companion": "#FFD166", "wash": "#F2EFFF", "ink": "#342C68"},
    "sproutbound": {"accent": "#A8D94F", "companion": "#F5A05B", "wash": "#F2F7E4", "ink": "#345138"},
}

LANGUAGE_NAMES = {"en": "English", "es": "Español", "fr": "Français", "it": "Italiano", "de": "Deutsch"}
LANGUAGE_SHORT = {"en": "EN", "es": "ES", "fr": "FR", "it": "IT", "de": "DE"}

COMMON = {
    "en": {
        "collection": "Puzzle worlds",
        "collection_short": "Puzzle worlds",
        "hub_title": "Ten puzzle worlds. One good reason to think.",
        "hub_lede": "Meet ten focused iPhone puzzle games built around one clear idea each. Learn the rule, feel the response, and keep finding better solutions.",
        "hub_eyebrow": "A small collection of big ideas",
        "orbit_alt": "Colorful puzzle shapes",
        "games": "The games",
        "games_intro": "Different mechanics, the same invitation: slow down, look closely, and solve one satisfying move at a time.",
        "explore": "Explore the game",
        "coming": "Coming soon on the App Store",
        "privacy": "Privacy",
        "all_games": "All games",
        "language": "Language",
        "how": "See the idea in motion",
        "collection_title": "100 curated puzzles, then keep going",
        "collection_copy": "Each game starts with a carefully arranged collection of 100 puzzles. Once the main collection is complete, endless challenges keep the same rules open for fresh problems.",
        "curated": "100 curated puzzles",
        "curated_copy": "A designed progression with increasing logical or spatial depth.",
        "endless": "Endless challenges",
        "endless_copy": "Continue exploring after the main collection is complete.",
        "calm": "No timer",
        "calm_copy": "Think, try, undo, and learn at your own pace.",
        "screens": "Inside the game",
        "screens_intro": "The four views below follow the approved App Store sequence: core mechanic, deeper puzzle, solved state, then the collection home.",
        "free_pro": "Free to play. Pro when you want it.",
        "free_copy": "The game is free to play. Free players may see an interstitial after selected completed puzzles and can watch a rewarded ad for a hint.",
        "pro_copy": "The one-time Pro upgrade removes ads and makes hints available directly.",
        "other": "Find another puzzle world",
        "other_intro": "Switch mechanics without leaving the collection.",
        "back_home": "Back to the collection",
        "read_privacy": "Read this app's privacy information",
        "site_privacy": "App privacy pages",
        "footer_note": "Ten focused puzzle games for iPhone. No account required.",
        "skip": "Skip to content",
        "privacy_eyebrow": "Privacy information",
        "privacy_title": "Privacy for {name}",
        "privacy_updated": "Last updated: September 17, 2026",
        "privacy_intro": "{name} is designed to be played without an account. This page explains what stays on your device and which services are involved when free features are used.",
        "privacy_summary_device": "Progress and settings",
        "privacy_summary_device_copy": "Stored locally on your device",
        "privacy_summary_account": "Account",
        "privacy_summary_account_copy": "No account is required",
        "privacy_summary_ads": "Free features",
        "privacy_summary_ads_copy": "Rewarded hints and selected interstitials",
        "website_heading": "This website",
        "website_body": "This static website has no accounts, forms, cookies, analytics, advertising, or third-party tracking scripts. GitHub Pages may receive ordinary request logs under GitHub's own policies. The website does not use those logs to identify you or build a profile.",
        "app_heading": "What the app stores",
        "app_body": "No account is required. Puzzle progress and app settings are stored locally on your device so the app can remember where you are. We do not operate a separate account database for this app.",
        "ads_heading": "Ads and rewarded hints",
        "ads_body": "Free players may see selected completion interstitials and can choose to watch a rewarded ad to receive a hint. Google Mobile Ads may process technical, device, and ad-interaction information to provide, measure, and protect the service under Google's privacy policy. Whether advertising is personalized depends on applicable consent, region, and platform settings; this page does not promise that every ad is personalized or non-personalized.",
        "pro_heading": "Pro purchase",
        "pro_body": "Apple and StoreKit process the one-time Pro purchase. The app receives the resulting entitlement state; it does not receive or store your payment-card details. Pro removes ads and makes hints available directly.",
        "sharing_heading": "Sharing and deletion",
        "sharing_body": "The app does not require you to submit personal information to play. Deleting the app removes its locally stored progress and settings from the device, subject to normal operating-system backups. If you need help after the app is available, contact the developer through the app's App Store listing.",
        "links_heading": "Related policies",
        "google_policy": "Google Privacy Policy",
        "apple_policy": "Apple Privacy",
        "privacy_contact": "For product support, use the developer contact shown on the App Store listing once the app is live.",
        "site_privacy_title": "Privacy information for the puzzle games",
        "site_privacy_desc": "How the ten puzzle apps and this static website handle local progress, ads, purchases, and ordinary website requests.",
    },
    "es": {
        "collection": "Mundos de puzle", "collection_short": "Mundos de puzle", "hub_title": "Diez mundos de puzle. Una buena razón para pensar.", "hub_lede": "Conoce diez juegos de puzles para iPhone, cada uno construido alrededor de una idea clara. Aprende la regla, siente la respuesta y sigue encontrando mejores soluciones.", "hub_eyebrow": "Una pequeña colección de grandes ideas", "orbit_alt": "Formas de puzle de colores", "games": "Los juegos", "games_intro": "Mecánicas diferentes, la misma invitación: baja el ritmo, observa con atención y resuelve un movimiento satisfactorio cada vez.", "explore": "Explorar el juego", "coming": "Próximamente en el App Store", "privacy": "Privacidad", "all_games": "Todos los juegos", "language": "Idioma", "how": "Mira la idea en movimiento", "collection_title": "100 puzles seleccionados y después, más", "collection_copy": "Cada juego comienza con una colección cuidada de 100 puzles. Al terminarla, los retos infinitos mantienen abiertas las mismas reglas para plantear nuevos problemas.", "curated": "100 puzles seleccionados", "curated_copy": "Una progresión diseñada con profundidad lógica o espacial creciente.", "endless": "Retos infinitos", "endless_copy": "Sigue explorando después de completar la colección principal.", "calm": "Sin cronómetro", "calm_copy": "Piensa, prueba, deshaz y aprende a tu ritmo.", "screens": "Dentro del juego", "screens_intro": "Las cuatro vistas siguen la secuencia aprobada del App Store: mecánica principal, puzle más profundo, estado resuelto y colección.", "free_pro": "Gratis para jugar. Pro cuando quieras.", "free_copy": "El juego es gratuito. La versión gratuita puede mostrar un anuncio intersticial tras determinados puzles completados y permite ver un anuncio recompensado para obtener una pista.", "pro_copy": "La mejora Pro, de pago único, elimina los anuncios y ofrece pistas directamente.", "other": "Descubre otro mundo de puzle", "other_intro": "Cambia de mecánica sin salir de la colección.", "back_home": "Volver a la colección", "read_privacy": "Leer la información de privacidad de este juego", "site_privacy": "Páginas de privacidad", "footer_note": "Diez juegos de puzles para iPhone. No necesitas una cuenta.", "skip": "Saltar al contenido", "privacy_eyebrow": "Información de privacidad", "privacy_title": "Privacidad de {name}", "privacy_updated": "Última actualización: 17 de septiembre de 2026", "privacy_intro": "{name} está diseñado para jugar sin una cuenta. Esta página explica qué permanece en tu dispositivo y qué servicios intervienen al usar las funciones gratuitas.", "privacy_summary_device": "Progreso y ajustes", "privacy_summary_device_copy": "Se guardan localmente en tu dispositivo", "privacy_summary_account": "Cuenta", "privacy_summary_account_copy": "No necesitas una cuenta", "privacy_summary_ads": "Funciones gratuitas", "privacy_summary_ads_copy": "Pistas recompensadas e intersticiales seleccionados", "website_heading": "Este sitio web", "website_body": "Este sitio web estático no tiene cuentas, formularios, cookies, analítica, publicidad ni scripts de seguimiento de terceros. GitHub Pages puede recibir registros ordinarios de solicitudes según sus propias políticas. El sitio no usa esos registros para identificarte ni crear un perfil.", "app_heading": "Qué guarda la app", "app_body": "No necesitas una cuenta. El progreso de los puzles y los ajustes se guardan localmente en tu dispositivo para que la app recuerde dónde estás. No gestionamos una base de datos de cuentas para esta app.", "ads_heading": "Anuncios y pistas recompensadas", "ads_body": "Los jugadores gratuitos pueden ver intersticiales tras determinadas finalizaciones y elegir ver un anuncio recompensado para obtener una pista. Google Mobile Ads puede procesar información técnica, del dispositivo y de interacción con anuncios para proporcionar, medir y proteger el servicio según la política de privacidad de Google. La personalización depende del consentimiento aplicable, la región y los ajustes de la plataforma; esta página no promete que todos los anuncios sean personalizados o no personalizados.", "pro_heading": "Compra Pro", "pro_body": "Apple y StoreKit procesan la compra única de Pro. La app recibe el estado de la autorización, pero no recibe ni guarda los datos de tu tarjeta. Pro elimina los anuncios y ofrece las pistas directamente.", "sharing_heading": "Compartir y eliminar", "sharing_body": "La app no te pide enviar información personal para jugar. Al eliminarla se borran del dispositivo el progreso y los ajustes guardados localmente, sujeto a las copias de seguridad normales del sistema operativo. Cuando la app esté disponible, contacta con el desarrollador mediante su ficha del App Store si necesitas ayuda.", "links_heading": "Políticas relacionadas", "google_policy": "Política de privacidad de Google", "apple_policy": "Privacidad de Apple", "privacy_contact": "Para recibir soporte del producto, usa el contacto del desarrollador que aparecerá en la ficha del App Store cuando la app esté disponible.", "site_privacy_title": "Privacidad de los juegos de puzles", "site_privacy_desc": "Cómo gestionan las diez apps de puzles y este sitio web estático el progreso local, los anuncios, las compras y las solicitudes web normales."
    },
    "fr": {
        "collection": "Univers de puzzles", "collection_short": "Univers de puzzles", "hub_title": "Dix univers de puzzles. Une belle raison de réfléchir.", "hub_lede": "Découvrez dix jeux de réflexion pour iPhone, chacun construit autour d'une idée claire. Comprenez la règle, ressentez la réponse et cherchez toujours une meilleure solution.", "hub_eyebrow": "Une petite collection de grandes idées", "orbit_alt": "Formes de puzzle colorées", "games": "Les jeux", "games_intro": "Des mécaniques différentes, une même invitation : ralentir, observer et résoudre un mouvement satisfaisant à la fois.", "explore": "Découvrir le jeu", "coming": "Bientôt sur l’App Store", "privacy": "Confidentialité", "all_games": "Tous les jeux", "language": "Langue", "how": "Voyez l’idée en mouvement", "collection_title": "100 puzzles conçus avec soin, puis la suite", "collection_copy": "Chaque jeu commence par une collection de 100 puzzles conçus avec soin. Une fois cette collection terminée, des défis sans fin prolongent les mêmes règles.", "curated": "100 puzzles conçus avec soin", "curated_copy": "Une progression pensée pour approfondir la logique ou l’espace.", "endless": "Défis sans fin", "endless_copy": "Continuez à explorer après la collection principale.", "calm": "Aucun chronomètre", "calm_copy": "Réfléchissez, essayez, annulez et apprenez à votre rythme.", "screens": "Dans le jeu", "screens_intro": "Les quatre vues suivent la séquence App Store approuvée : mécanique principale, puzzle avancé, état réussi, puis accueil de la collection.", "free_pro": "Jouable gratuitement. Pro si vous le souhaitez.", "free_copy": "Le jeu est jouable gratuitement. La version gratuite peut afficher une publicité interstitielle après certains puzzles terminés et propose une publicité récompensée pour obtenir un indice.", "pro_copy": "L’achat unique Pro supprime les publicités et donne directement accès aux indices.", "other": "Découvrez un autre univers", "other_intro": "Changez de mécanique sans quitter la collection.", "back_home": "Retour à la collection", "read_privacy": "Lire les informations de confidentialité", "site_privacy": "Pages de confidentialité", "footer_note": "Dix jeux de réflexion pour iPhone. Aucun compte nécessaire.", "skip": "Aller au contenu", "privacy_eyebrow": "Informations de confidentialité", "privacy_title": "Confidentialité de {name}", "privacy_updated": "Dernière mise à jour : 17 septembre 2026", "privacy_intro": "{name} est conçu pour être joué sans compte. Cette page explique ce qui reste sur votre appareil et quels services interviennent avec les fonctions gratuites.", "privacy_summary_device": "Progression et réglages", "privacy_summary_device_copy": "Enregistrés localement sur votre appareil", "privacy_summary_account": "Compte", "privacy_summary_account_copy": "Aucun compte nécessaire", "privacy_summary_ads": "Fonctions gratuites", "privacy_summary_ads_copy": "Indices récompensés et interstitiels sélectionnés", "website_heading": "Ce site web", "website_body": "Ce site web statique n’utilise ni compte, ni formulaire, ni cookie, ni outil d’analyse, ni publicité, ni script de suivi tiers. GitHub Pages peut recevoir les journaux ordinaires de requêtes selon ses propres règles. Le site n’utilise pas ces journaux pour vous identifier ou créer un profil.", "app_heading": "Ce que l’app conserve", "app_body": "Aucun compte n’est nécessaire. La progression des puzzles et les réglages sont enregistrés localement sur votre appareil afin que l’app se souvienne de votre parcours. Nous n’exploitons pas de base de comptes séparée pour cette app.", "ads_heading": "Publicités et indices récompensés", "ads_body": "Les joueurs gratuits peuvent voir des interstitiels après certaines réussites et choisir de regarder une publicité récompensée pour obtenir un indice. Google Mobile Ads peut traiter des informations techniques, liées à l’appareil et aux interactions publicitaires pour fournir, mesurer et protéger le service conformément à la politique de confidentialité de Google. La personnalisation dépend du consentement applicable, de la région et des réglages de la plateforme ; cette page ne prétend pas que toutes les publicités sont personnalisées ou non personnalisées.", "pro_heading": "Achat Pro", "pro_body": "Apple et StoreKit traitent l’achat unique Pro. L’app reçoit l’état de l’autorisation, mais ne reçoit ni ne conserve les données de votre carte bancaire. Pro supprime les publicités et rend les indices accessibles directement.", "sharing_heading": "Partage et suppression", "sharing_body": "L’app ne vous demande pas de transmettre des informations personnelles pour jouer. La suppression de l’app retire de l’appareil la progression et les réglages stockés localement, sous réserve des sauvegardes habituelles du système. Lorsque l’app sera disponible, contactez le développeur via sa fiche App Store si vous avez besoin d’aide.", "links_heading": "Politiques associées", "google_policy": "Politique de confidentialité de Google", "apple_policy": "Confidentialité Apple", "privacy_contact": "Pour l’assistance produit, utilisez le contact du développeur indiqué sur la fiche App Store lorsque l’app sera disponible.", "site_privacy_title": "Confidentialité des jeux de réflexion", "site_privacy_desc": "Comment les dix apps et ce site statique traitent la progression locale, les publicités, les achats et les requêtes web ordinaires."
    },
    "it": {
        "collection": "Mondi di puzzle", "collection_short": "Mondi di puzzle", "hub_title": "Dieci mondi di puzzle. Un buon motivo per ragionare.", "hub_lede": "Scopri dieci giochi di logica per iPhone, ognuno costruito attorno a un’idea chiara. Impara la regola, senti la risposta e continua a trovare soluzioni migliori.", "hub_eyebrow": "Una piccola raccolta di grandi idee", "orbit_alt": "Forme colorate di puzzle", "games": "I giochi", "games_intro": "Meccaniche diverse, lo stesso invito: rallenta, osserva e risolvi una mossa soddisfacente alla volta.", "explore": "Scopri il gioco", "coming": "In arrivo sull’App Store", "privacy": "Privacy", "all_games": "Tutti i giochi", "language": "Lingua", "how": "Guarda l’idea in movimento", "collection_title": "100 puzzle curati, poi continua", "collection_copy": "Ogni gioco inizia con una raccolta di 100 puzzle curati. Dopo averla completata, le sfide infinite mantengono aperte le stesse regole per nuovi problemi.", "curated": "100 puzzle curati", "curated_copy": "Una progressione progettata con profondità logica o spaziale crescente.", "endless": "Sfide infinite", "endless_copy": "Continua a esplorare dopo la raccolta principale.", "calm": "Nessun timer", "calm_copy": "Ragiona, prova, annulla e impara al tuo ritmo.", "screens": "Dentro il gioco", "screens_intro": "Le quattro viste seguono la sequenza App Store approvata: meccanica principale, puzzle più profondo, stato risolto e raccolta.", "free_pro": "Gioca gratis. Pro quando vuoi.", "free_copy": "Il gioco è gratuito. Nella versione gratuita può apparire un annuncio interstitial dopo alcuni puzzle completati e puoi guardare un annuncio con premio per ottenere un suggerimento.", "pro_copy": "L’acquisto una tantum Pro rimuove gli annunci e rende i suggerimenti subito disponibili.", "other": "Scopri un altro mondo di puzzle", "other_intro": "Cambia meccanica senza uscire dalla raccolta.", "back_home": "Torna alla raccolta", "read_privacy": "Leggi le informazioni sulla privacy", "site_privacy": "Pagine sulla privacy", "footer_note": "Dieci giochi di logica per iPhone. Non serve un account.", "skip": "Vai al contenuto", "privacy_eyebrow": "Informazioni sulla privacy", "privacy_title": "Privacy di {name}", "privacy_updated": "Ultimo aggiornamento: 17 settembre 2026", "privacy_intro": "{name} è progettato per giocare senza account. Questa pagina spiega cosa rimane sul dispositivo e quali servizi intervengono usando le funzioni gratuite.", "privacy_summary_device": "Progressi e impostazioni", "privacy_summary_device_copy": "Salvati localmente sul dispositivo", "privacy_summary_account": "Account", "privacy_summary_account_copy": "Non serve un account", "privacy_summary_ads": "Funzioni gratuite", "privacy_summary_ads_copy": "Suggerimenti con premio e interstitial selezionati", "website_heading": "Questo sito web", "website_body": "Questo sito web statico non usa account, moduli, cookie, analisi, pubblicità o script di tracciamento di terze parti. GitHub Pages può ricevere i normali log delle richieste secondo le proprie politiche. Il sito non usa questi log per identificarti o creare un profilo.", "app_heading": "Cosa salva l’app", "app_body": "Non serve un account. I progressi dei puzzle e le impostazioni vengono salvati localmente sul dispositivo, così l’app ricorda il tuo percorso. Non gestiamo un database separato di account per questa app.", "ads_heading": "Annunci e suggerimenti con premio", "ads_body": "I giocatori gratuiti possono vedere interstitial dopo alcuni completamenti e scegliere di guardare un annuncio con premio per ricevere un suggerimento. Google Mobile Ads può elaborare informazioni tecniche, del dispositivo e sulle interazioni con gli annunci per fornire, misurare e proteggere il servizio secondo la privacy policy di Google. La personalizzazione dipende dal consenso applicabile, dalla regione e dalle impostazioni della piattaforma; questa pagina non afferma che tutti gli annunci siano personalizzati o non personalizzati.", "pro_heading": "Acquisto Pro", "pro_body": "Apple e StoreKit elaborano l’acquisto una tantum Pro. L’app riceve lo stato dell’autorizzazione, ma non riceve né conserva i dati della carta. Pro rimuove gli annunci e rende disponibili direttamente i suggerimenti.", "sharing_heading": "Condivisione e cancellazione", "sharing_body": "L’app non ti chiede di inviare informazioni personali per giocare. Eliminando l’app rimuovi dal dispositivo i progressi e le impostazioni salvati localmente, salvo i normali backup del sistema operativo. Quando l’app sarà disponibile, contatta lo sviluppatore tramite la sua pagina App Store se ti serve aiuto.", "links_heading": "Politiche collegate", "google_policy": "Privacy policy di Google", "apple_policy": "Privacy Apple", "privacy_contact": "Per l’assistenza sul prodotto, usa il contatto dello sviluppatore indicato nella pagina App Store quando l’app sarà disponibile.", "site_privacy_title": "Privacy dei giochi di logica", "site_privacy_desc": "Come le dieci app di puzzle e questo sito statico gestiscono progressi locali, annunci, acquisti e normali richieste web."
    },
    "de": {
        "collection": "Puzzlewelten", "collection_short": "Puzzlewelten", "hub_title": "Zehn Puzzlewelten. Ein guter Grund zum Denken.", "hub_lede": "Entdecke zehn fokussierte iPhone-Puzzlespiele, jedes um eine klare Idee gebaut. Verstehe die Regel, spüre die Reaktion und finde immer bessere Lösungen.", "hub_eyebrow": "Eine kleine Sammlung großer Ideen", "orbit_alt": "Bunte Puzzleformen", "games": "Die Spiele", "games_intro": "Unterschiedliche Mechaniken, dieselbe Einladung: langsamer werden, genau hinsehen und Zug für Zug eine befriedigende Lösung finden.", "explore": "Spiel entdecken", "coming": "Demnächst im App Store", "privacy": "Datenschutz", "all_games": "Alle Spiele", "language": "Sprache", "how": "Die Idee in Bewegung", "collection_title": "100 gestaltete Rätsel, dann geht es weiter", "collection_copy": "Jedes Spiel beginnt mit einer sorgfältig gestalteten Sammlung von 100 Rätseln. Danach halten endlose Herausforderungen dieselben Regeln für neue Aufgaben offen.", "curated": "100 gestaltete Rätsel", "curated_copy": "Eine Entwicklung mit wachsender logischer oder räumlicher Tiefe.", "endless": "Endlose Herausforderungen", "endless_copy": "Erkunde weiter, nachdem die Hauptsammlung abgeschlossen ist.", "calm": "Kein Zeitdruck", "calm_copy": "Denke nach, probiere, mache Züge rückgängig und lerne in deinem Tempo.", "screens": "Im Spiel", "screens_intro": "Die vier Ansichten folgen der freigegebenen App-Store-Reihenfolge: Kernmechanik, tieferes Rätsel, gelöster Zustand und Sammlung.", "free_pro": "Kostenlos spielbar. Pro, wenn du möchtest.", "free_copy": "Das Spiel ist kostenlos spielbar. In der kostenlosen Version kann nach ausgewählten gelösten Rätseln eine Vollbildanzeige erscheinen; für einen Hinweis kann ein belohntes Video angesehen werden.", "pro_copy": "Das einmalige Pro-Upgrade entfernt Werbung und schaltet Hinweise direkt frei.", "other": "Entdecke eine weitere Puzzlewelt", "other_intro": "Wechsle die Mechanik, ohne die Sammlung zu verlassen.", "back_home": "Zur Sammlung", "read_privacy": "Datenschutzinformationen lesen", "site_privacy": "Datenschutzseiten", "footer_note": "Zehn fokussierte iPhone-Puzzlespiele. Kein Konto erforderlich.", "skip": "Zum Inhalt springen", "privacy_eyebrow": "Datenschutzinformationen", "privacy_title": "Datenschutz für {name}", "privacy_updated": "Zuletzt aktualisiert: 17. September 2026", "privacy_intro": "{name} ist zum Spielen ohne Konto gedacht. Diese Seite erklärt, was auf deinem Gerät bleibt und welche Dienste bei kostenlosen Funktionen beteiligt sind.", "privacy_summary_device": "Fortschritt und Einstellungen", "privacy_summary_device_copy": "Lokal auf deinem Gerät gespeichert", "privacy_summary_account": "Konto", "privacy_summary_account_copy": "Kein Konto erforderlich", "privacy_summary_ads": "Kostenlose Funktionen", "privacy_summary_ads_copy": "Belohnte Hinweise und ausgewählte Interstitials", "website_heading": "Diese Website", "website_body": "Diese statische Website nutzt keine Konten, Formulare, Cookies, Analyse, Werbung oder Tracking-Skripte von Drittanbietern. GitHub Pages kann gemäß den eigenen Richtlinien normale Anfrageprotokolle erhalten. Die Website verwendet diese Protokolle nicht, um dich zu identifizieren oder ein Profil zu erstellen.", "app_heading": "Was die App speichert", "app_body": "Kein Konto erforderlich. Puzzlefortschritt und Einstellungen werden lokal auf deinem Gerät gespeichert, damit die App deinen Stand merkt. Für diese App betreiben wir keine eigene Kontodatenbank.", "ads_heading": "Werbung und belohnte Hinweise", "ads_body": "Kostenlose Spieler können nach ausgewählten Abschlüssen Interstitials sehen und freiwillig ein belohntes Video für einen Hinweis ansehen. Google Mobile Ads kann technische Informationen, Geräteinformationen und Daten zur Anzeigeninteraktion gemäß Googles Datenschutzrichtlinie verarbeiten, um den Dienst bereitzustellen, zu messen und zu schützen. Ob Werbung personalisiert wird, hängt von geltender Einwilligung, Region und Plattformeinstellungen ab; diese Seite behauptet nicht, dass jede Anzeige personalisiert oder nicht personalisiert ist.", "pro_heading": "Pro-Kauf", "pro_body": "Apple und StoreKit verarbeiten den einmaligen Pro-Kauf. Die App erhält den Status der Berechtigung, aber keine Zahlungskartendaten. Pro entfernt Werbung und schaltet Hinweise direkt frei.", "sharing_heading": "Weitergabe und Löschung", "sharing_body": "Die App verlangt zum Spielen keine persönlichen Angaben. Wenn du die App löschst, werden lokal gespeicherter Fortschritt und Einstellungen vom Gerät entfernt, vorbehaltlich normaler Betriebssystem-Backups. Sobald die App verfügbar ist, kannst du den Entwickler bei Fragen über den App-Store-Eintrag kontaktieren.", "links_heading": "Verbundene Richtlinien", "google_policy": "Googles Datenschutzrichtlinie", "apple_policy": "Apple Datenschutz", "privacy_contact": "Für Produktsupport nutze den Entwicklerkontakt, der beim Start der App im App-Store-Eintrag angezeigt wird.", "site_privacy_title": "Datenschutz der Puzzlespiele", "site_privacy_desc": "Wie die zehn Puzzle-Apps und diese statische Website mit lokalem Fortschritt, Werbung, Käufen und normalen Webanfragen umgehen."
    },
}

# PocketColor pages use their own product and privacy language while sharing
# the existing layout, route, accessibility, and SEO helpers above.
POCKET_TEXT = {
    "en": {
        "support_nav": "Help & support", "journey_label": "The journey", "journey_title": "Cross the river on two depth layers",
        "screens_intro": "The six views follow the river journey in order: core mechanic, two new regions, a deeper puzzle, a solved crossing, then the home atlas.",
        "regions": "Regions", "story_routes": "Story crossings", "trials": "Tide Trials", "depths": "Depth layers",
        "free_title": "Begin with a complete opening region", "full_title": "Continue Nim’s journey",
        "one_time": "One-time purchase · No ads · No subscription", "price": "Spain base price €3.99; other storefront prices are set by Apple.",
        "free_replay": "The first six story crossings in Wakewater Gardens are free to play.",
        "faq_label": "Help & support", "faq_title": "Questions about Reedwake?", "support_intro": "Find practical answers about controls, saved progress, the free opening and your full-game purchase.",
        "controls_q": "How do I move Nim?", "save_q": "Where is my progress saved?", "content_q": "What is included for free?", "purchase_q": "What does the full-game purchase unlock?", "restore_q": "How do I restore a purchase?", "pending_q": "My purchase is pending or the store is unavailable. What should I do?",
        "controls_a": "The in-game guide explains movement, depth changes and crossing hazards. Use the movement control to move one tile at a time; the A action changes depth when the route allows it.",
        "save_a": "Crossing progress, badges and settings are saved locally on this device. Reedwake does not require an account. Deleting the app removes locally stored data, subject to normal operating-system backups.",
        "pending_a": "A pending purchase is waiting for authorization or completion; keep playing the free chapter and check again later. If the store cannot load, check your connection and retry. A verified purchase or restore unlocks the full game while preserving your progress.",
        "restore_a_prefix": "Open the in-game full-game purchase sheet and choose",
        "privacy_title": "Privacy for {name}", "privacy_intro": "Reedwake stores game progress and settings locally. It does not use accounts, ads, analytics or subscription services. This page describes the app and this website.",
        "privacy_updated": "Last updated: October 7, 2026", "privacy_device": "Progress and settings", "privacy_device_copy": "Stored locally on your device",
        "privacy_account": "Account", "privacy_account_copy": "No account required", "privacy_services": "Third-party services", "privacy_services_copy": "Apple StoreKit handles the one-time purchase",
        "website_heading": "This website", "website_body": "This static website has no accounts, forms, cookies, analytics, advertising, or third-party tracking scripts. GitHub Pages may receive ordinary request logs under GitHub’s own policies. The website does not use those logs to identify you or build a profile.",
        "app_heading": "What the app stores", "app_body": "Reedwake stores game progress, badges and settings locally on your device. No account is required, and game progress is not sent to a Reedwake server. Deleting the app removes its local data, subject to normal operating-system backups.",
        "purchase_heading": "One-time purchase", "purchase_body": "Apple and StoreKit process the optional non-consumable full-game purchase. The app receives the verified entitlement state; it does not receive or store payment-card details. The purchase unlocks the remaining seven regions, 42 story crossings, all eight Tide Trials, and the complete story and ending. The Spain base price is €3.99; other storefront prices are set by Apple.",
        "services_heading": "Ads, accounts and analytics", "services_body": "Reedwake contains no advertising, account system, subscription, or analytics service. The app uses StoreKit for the optional one-time full-game purchase.",
        "deletion_heading": "Progress and deletion", "deletion_body": "Game progress and settings stay on this device. Deleting Reedwake removes its locally stored data, subject to normal operating-system backups. If you unlock the full game, the entitlement can be restored through the in-game purchase sheet.",
        "privacy_contact": "For help, visit the Reedwake support section.", "privacy_back": "Reedwake help & support", "discover_title": "A story journey beyond the puzzle worlds", "discover_copy": "Discover Reedwake: a river-crossing adventure about finding a path through rain, traffic and two changing depths.",
        "footer": "A river-crossing adventure with a free opening region and a one-time full-game unlock.",
    },
    "es": {
        "support_nav": "Ayuda y soporte", "journey_label": "El viaje", "journey_title": "Cruza el río en dos capas de profundidad",
        "screens_intro": "Las seis vistas muestran el viaje por el río en orden: mecánica principal, dos regiones nuevas, un puzle más profundo, un cruce resuelto y el atlas.",
        "regions": "Regiones", "story_routes": "Cruces de historia", "trials": "Pruebas de marea", "depths": "Capas de profundidad",
        "free_title": "Empieza con una región inicial completa", "full_title": "Continúa el viaje de Nim",
        "one_time": "Pago único · Sin anuncios · Sin suscripción", "price": "Precio base en España: 3,99 €; Apple establece los precios en otros escaparates.",
        "free_replay": "Los seis primeros cruces de historia de Jardines de Agua Viva se pueden jugar gratis.",
        "faq_label": "Ayuda y soporte", "faq_title": "¿Tienes dudas sobre Reedwake?", "support_intro": "Encuentra respuestas prácticas sobre los controles, el progreso guardado, el capítulo gratuito y la compra del juego completo.",
        "controls_q": "¿Cómo muevo a Nim?", "save_q": "¿Dónde se guarda mi progreso?", "content_q": "¿Qué puedo jugar gratis?", "purchase_q": "¿Qué desbloquea la compra del juego completo?", "restore_q": "¿Cómo restauro una compra?", "pending_q": "La compra está pendiente o la tienda no está disponible. ¿Qué hago?",
        "controls_a": "La guía del juego explica el movimiento, los cambios de profundidad y los peligros de los cruces. Usa el control de movimiento para avanzar casilla a casilla; la acción A cambia de capa cuando la ruta lo permite.",
        "save_a": "El progreso de los cruces, las insignias y los ajustes se guardan localmente en este dispositivo. Reedwake no requiere una cuenta. Al borrar la app se eliminan los datos locales, sujeto a las copias de seguridad normales del sistema operativo.",
        "pending_a": "Una compra pendiente espera autorización o que se complete; puedes seguir jugando el capítulo gratuito y volver a comprobarlo más tarde. Si la tienda no carga, revisa la conexión e inténtalo de nuevo. Una compra o restauración verificada desbloquea el juego completo y conserva tu progreso.",
        "restore_a_prefix": "Abre la pantalla de compra del juego completo y selecciona",
        "privacy_title": "Privacidad de {name}", "privacy_intro": "Reedwake guarda el progreso y los ajustes localmente. No usa cuentas, anuncios, analítica ni suscripciones. Esta página describe la app y este sitio web.",
        "privacy_updated": "Última actualización: 7 de octubre de 2026", "privacy_device": "Progreso y ajustes", "privacy_device_copy": "Se guardan localmente en tu dispositivo",
        "privacy_account": "Cuenta", "privacy_account_copy": "No necesitas una cuenta", "privacy_services": "Servicios externos", "privacy_services_copy": "Apple StoreKit gestiona la compra única",
        "website_heading": "Este sitio web", "website_body": "Este sitio web estático no tiene cuentas, formularios, cookies, analítica, publicidad ni scripts de seguimiento de terceros. GitHub Pages puede recibir registros ordinarios de solicitudes según sus propias políticas. El sitio no usa esos registros para identificarte ni crear un perfil.",
        "app_heading": "Qué guarda la app", "app_body": "Reedwake guarda el progreso, las insignias y los ajustes localmente en tu dispositivo. No necesitas una cuenta y el progreso no se envía a un servidor de Reedwake. Al borrar la app se eliminan los datos locales, sujeto a las copias de seguridad normales del sistema operativo.",
        "purchase_heading": "Compra única", "purchase_body": "Apple y StoreKit procesan la compra opcional no consumible del juego completo. La app recibe el estado verificado de la autorización, pero no recibe ni guarda los datos de la tarjeta. La compra desbloquea las otras siete regiones, 42 cruces de historia, las ocho pruebas de marea y la historia completa con su final. El precio base en España es 3,99 €; Apple establece los precios en otros escaparates.",
        "services_heading": "Anuncios, cuentas y analítica", "services_body": "Reedwake no incluye publicidad, sistema de cuentas, suscripciones ni servicios de analítica. La compra opcional única del juego completo se gestiona con StoreKit.",
        "deletion_heading": "Progreso y eliminación", "deletion_body": "El progreso y los ajustes se quedan en este dispositivo. Al borrar Reedwake se eliminan sus datos locales, sujeto a las copias de seguridad normales del sistema operativo. Si desbloqueas el juego completo, puedes restaurar la autorización desde la pantalla de compra.",
        "privacy_contact": "Para recibir ayuda, visita la sección de soporte de Reedwake.", "privacy_back": "Ayuda y soporte de Reedwake", "discover_title": "Una aventura narrativa más allá de los mundos de puzle", "discover_copy": "Descubre Reedwake: una aventura de cruces fluviales para encontrar el camino entre la lluvia, el tráfico y dos profundidades cambiantes.",
        "footer": "Una aventura fluvial con una región inicial gratuita y un desbloqueo único del juego completo.",
    },
    "fr": {
        "support_nav": "Aide et assistance", "journey_label": "Le voyage", "journey_title": "Traversez la rivière sur deux profondeurs",
        "screens_intro": "Les six vues suivent le voyage dans l’ordre : mécanique centrale, deux nouvelles régions, puzzle plus approfondi, traversée réussie, puis atlas.",
        "regions": "Régions", "story_routes": "Traversées narratives", "trials": "Épreuves de marée", "depths": "Niveaux de profondeur",
        "free_title": "Commencez par une région d’ouverture complète", "full_title": "Poursuivez le voyage de Nim",
        "one_time": "Achat unique · Sans publicité · Sans abonnement", "price": "Prix de base en Espagne : 3,99 € ; Apple fixe les prix des autres boutiques.",
        "free_replay": "Les six premières traversées narratives des Jardins des Eaux vives sont gratuites.",
        "faq_label": "Aide et assistance", "faq_title": "Des questions sur Reedwake ?", "support_intro": "Trouvez des réponses pratiques sur les commandes, la progression sauvegardée, le début gratuit et l’achat du jeu complet.",
        "controls_q": "Comment déplacer Nim ?", "save_q": "Où ma progression est-elle sauvegardée ?", "content_q": "Que peut-on jouer gratuitement ?", "purchase_q": "Que débloque l’achat du jeu complet ?", "restore_q": "Comment restaurer un achat ?", "pending_q": "Mon achat est en attente ou la boutique est indisponible. Que faire ?",
        "controls_a": "Le guide intégré explique les déplacements, les changements de profondeur et les dangers. Utilisez la commande de déplacement pour avancer case par case ; l’action A change de couche lorsque le parcours le permet.",
        "save_a": "La progression, les badges et les réglages sont enregistrés localement sur cet appareil. Reedwake ne nécessite aucun compte. La suppression de l’app retire les données locales, sous réserve des sauvegardes habituelles du système d’exploitation.",
        "pending_a": "Un achat en attente nécessite encore une autorisation ou doit être finalisé ; vous pouvez continuer le chapitre gratuit et réessayer plus tard. Si la boutique ne se charge pas, vérifiez votre connexion puis réessayez. Un achat ou une restauration vérifiés débloquent le jeu complet tout en conservant votre progression.",
        "restore_a_prefix": "Ouvrez la fenêtre d’achat du jeu complet et choisissez",
        "privacy_title": "Confidentialité de {name}", "privacy_intro": "Reedwake conserve localement la progression et les réglages. Le jeu n’utilise ni compte, ni publicité, ni analyse, ni abonnement. Cette page décrit l’app et ce site web.",
        "privacy_updated": "Dernière mise à jour : 7 octobre 2026", "privacy_device": "Progression et réglages", "privacy_device_copy": "Enregistrés localement sur votre appareil",
        "privacy_account": "Compte", "privacy_account_copy": "Aucun compte nécessaire", "privacy_services": "Services tiers", "privacy_services_copy": "Apple StoreKit traite l’achat unique",
        "website_heading": "Ce site web", "website_body": "Ce site web statique n’utilise ni compte, ni formulaire, ni cookie, ni outil d’analyse, ni publicité, ni script de suivi tiers. GitHub Pages peut recevoir les journaux ordinaires de requêtes selon ses propres règles. Le site n’utilise pas ces journaux pour vous identifier ou créer un profil.",
        "app_heading": "Ce que l’app conserve", "app_body": "Reedwake enregistre localement sur votre appareil la progression, les badges et les réglages. Aucun compte n’est nécessaire et la progression n’est pas envoyée à un serveur Reedwake. La suppression de l’app retire les données locales, sous réserve des sauvegardes habituelles du système d’exploitation.",
        "purchase_heading": "Achat unique", "purchase_body": "Apple et StoreKit traitent l’achat facultatif non consommable du jeu complet. L’app reçoit l’état vérifié du droit d’accès ; elle ne reçoit ni ne conserve les données de votre carte bancaire. L’achat débloque les sept autres régions, 42 traversées narratives, les huit épreuves de marée et l’histoire complète jusqu’à sa fin. Le prix de base en Espagne est de 3,99 € ; Apple fixe les prix des autres boutiques.",
        "services_heading": "Publicité, comptes et analyse", "services_body": "Reedwake ne contient ni publicité, ni système de compte, ni abonnement, ni service d’analyse. StoreKit traite l’achat facultatif du jeu complet.",
        "deletion_heading": "Progression et suppression", "deletion_body": "La progression et les réglages restent sur cet appareil. La suppression de Reedwake retire ses données locales, sous réserve des sauvegardes habituelles du système d’exploitation. Si vous débloquez le jeu complet, vous pouvez restaurer votre achat depuis la fenêtre d’achat.",
        "privacy_contact": "Pour obtenir de l’aide, consultez la section d’assistance Reedwake.", "privacy_back": "Aide et assistance Reedwake", "discover_title": "Une aventure narrative au-delà des univers de puzzles", "discover_copy": "Découvrez Reedwake : une aventure de traversée où l’on cherche son chemin sous la pluie, entre circulation et deux profondeurs changeantes.",
        "footer": "Une aventure fluviale avec une région d’ouverture gratuite et un déblocage unique du jeu complet.",
    },
    "it": {
        "support_nav": "Aiuto e assistenza", "journey_label": "Il viaggio", "journey_title": "Attraversa il fiume su due livelli di profondità",
        "screens_intro": "Le sei schermate mostrano il viaggio sul fiume in ordine: meccanica principale, due nuove regioni, un puzzle più profondo, un attraversamento risolto e la schermata dell’atlante.",
        "regions": "Regioni", "story_routes": "Attraversamenti narrativi", "trials": "Prove di marea", "depths": "Livelli di profondità",
        "free_title": "Inizia con una regione introduttiva completa", "full_title": "Continua il viaggio di Nim",
        "one_time": "Acquisto una tantum · Senza annunci · Senza abbonamento", "price": "Prezzo base in Spagna: 3,99 €; Apple stabilisce i prezzi degli altri store.",
        "free_replay": "I primi sei attraversamenti narrativi dei Giardini di Acquafiorita sono gratuiti.",
        "faq_label": "Aiuto e assistenza", "faq_title": "Hai domande su Reedwake?", "support_intro": "Trova risposte pratiche su comandi, progressi salvati, capitolo gratuito e acquisto del gioco completo.",
        "controls_q": "Come muovo Nim?", "save_q": "Dove vengono salvati i progressi?", "content_q": "Cosa si può giocare gratis?", "purchase_q": "Cosa sblocca l’acquisto del gioco completo?", "restore_q": "Come ripristino un acquisto?", "pending_q": "L’acquisto è in attesa o lo store non è disponibile. Cosa posso fare?",
        "controls_a": "La guida del gioco spiega movimento, cambi di profondità e pericoli degli attraversamenti. Usa il comando di movimento per spostarti di una casella alla volta; l’azione A cambia livello quando il percorso lo consente.",
        "save_a": "Progressi negli attraversamenti, distintivi e impostazioni vengono salvati localmente su questo dispositivo. Reedwake non richiede un account. Eliminando l’app rimuovi i dati locali, salvo i normali backup del sistema operativo.",
        "pending_a": "Un acquisto in attesa deve ancora essere autorizzato o completato; puoi continuare il capitolo gratuito e riprovare più tardi. Se lo store non si carica, controlla la connessione e riprova. Un acquisto o ripristino verificato sblocca il gioco completo mantenendo i progressi.",
        "restore_a_prefix": "Apri la schermata d’acquisto del gioco completo e scegli",
        "privacy_title": "Privacy di {name}", "privacy_intro": "Reedwake salva progressi e impostazioni localmente. Non usa account, annunci, analisi o abbonamenti. Questa pagina descrive l’app e il sito web.",
        "privacy_updated": "Ultimo aggiornamento: 7 ottobre 2026", "privacy_device": "Progressi e impostazioni", "privacy_device_copy": "Salvati localmente sul dispositivo",
        "privacy_account": "Account", "privacy_account_copy": "Non serve un account", "privacy_services": "Servizi di terze parti", "privacy_services_copy": "Apple StoreKit gestisce l’acquisto una tantum",
        "website_heading": "Questo sito web", "website_body": "Questo sito web statico non usa account, moduli, cookie, analisi, pubblicità o script di tracciamento di terze parti. GitHub Pages può ricevere i normali log delle richieste secondo le proprie politiche. Il sito non usa questi log per identificarti o creare un profilo.",
        "app_heading": "Cosa salva l’app", "app_body": "Reedwake salva localmente sul dispositivo progressi, distintivi e impostazioni. Non serve un account e i progressi non vengono inviati a un server Reedwake. Eliminando l’app rimuovi i dati locali, salvo i normali backup del sistema operativo.",
        "purchase_heading": "Acquisto una tantum", "purchase_body": "Apple e StoreKit elaborano l’acquisto opzionale non consumabile del gioco completo. L’app riceve lo stato verificato dell’autorizzazione, ma non riceve né conserva i dati della carta. L’acquisto sblocca le altre sette regioni, 42 attraversamenti narrativi, tutte le otto prove di marea e la storia completa con finale. Il prezzo base in Spagna è 3,99 €; Apple stabilisce i prezzi degli altri store.",
        "services_heading": "Annunci, account e analisi", "services_body": "Reedwake non include pubblicità, account, abbonamenti o servizi di analisi. StoreKit gestisce l’acquisto opzionale una tantum del gioco completo.",
        "deletion_heading": "Progressi e cancellazione", "deletion_body": "Progressi e impostazioni restano su questo dispositivo. Eliminando Reedwake rimuovi i suoi dati locali, salvo i normali backup del sistema operativo. Se sblocchi il gioco completo, puoi ripristinare l’acquisto dalla schermata di acquisto.",
        "privacy_contact": "Per ricevere aiuto, visita la sezione assistenza di Reedwake.", "privacy_back": "Aiuto e assistenza Reedwake", "discover_title": "Un’avventura narrativa oltre i mondi di puzzle", "discover_copy": "Scopri Reedwake: un’avventura di attraversamenti fluviali per trovare la strada tra pioggia, traffico e due profondità mutevoli.",
        "footer": "Un’avventura fluviale con una regione introduttiva gratuita e uno sblocco una tantum del gioco completo.",
    },
    "de": {
        "support_nav": "Hilfe & Support", "journey_label": "Die Reise", "journey_title": "Überquere den Fluss auf zwei Tiefenebenen",
        "screens_intro": "Die sechs Ansichten zeigen die Flussreise der Reihe nach: Kernmechanik, zwei neue Regionen, ein tieferes Rätsel, eine gelöste Passage und anschließend der Atlas.",
        "regions": "Regionen", "story_routes": "Storyüberquerungen", "trials": "Gezeitenprüfungen", "depths": "Tiefenebenen",
        "free_title": "Beginne mit einer vollständigen Startregion", "full_title": "Setze Nims Reise fort",
        "one_time": "Einmalkauf · Keine Werbung · Kein Abo", "price": "Basispreis in Spanien: 3,99 €; Apple legt die Preise anderer Stores fest.",
        "free_replay": "Die ersten sechs Storyüberquerungen in den Gärten des Wacherwassers sind kostenlos spielbar.",
        "faq_label": "Hilfe & Support", "faq_title": "Fragen zu Reedwake?", "support_intro": "Hier findest du praktische Antworten zu Steuerung, Spielstand, kostenlosem Einstieg und dem Kauf der Vollversion.",
        "controls_q": "Wie bewege ich Nim?", "save_q": "Wo wird mein Fortschritt gespeichert?", "content_q": "Was kann ich kostenlos spielen?", "purchase_q": "Was schaltet der Vollversionskauf frei?", "restore_q": "Wie stelle ich einen Kauf wieder her?", "pending_q": "Mein Kauf ist ausstehend oder der Store nicht verfügbar. Was kann ich tun?",
        "controls_a": "Der Spieleführer erklärt Bewegung, Tiefenwechsel und Gefahren beim Überqueren. Bewege dich mit der Steuerung jeweils ein Feld; die A-Aktion wechselt die Ebene, wenn der Weg es erlaubt.",
        "save_a": "Fortschritt, Abzeichen und Einstellungen werden lokal auf diesem Gerät gespeichert. Reedwake benötigt kein Konto. Beim Löschen der App werden lokale Daten entfernt, vorbehaltlich normaler Betriebssystem-Backups.",
        "pending_a": "Ein ausstehender Kauf wartet noch auf eine Genehmigung oder seinen Abschluss. Spiele bis dahin das kostenlose Kapitel weiter und prüfe es später erneut. Wenn der Store nicht lädt, überprüfe deine Verbindung und versuche es erneut. Ein verifizierter Kauf oder eine Wiederherstellung schaltet das ganze Spiel frei und erhält deinen Fortschritt.",
        "restore_a_prefix": "Öffne den Kaufdialog für die Vollversion und wähle",
        "privacy_title": "Datenschutz für {name}", "privacy_intro": "Reedwake speichert Fortschritt und Einstellungen lokal. Das Spiel nutzt keine Konten, Werbung, Analyse oder Abonnements. Diese Seite beschreibt die App und diese Website.",
        "privacy_updated": "Zuletzt aktualisiert: 7. Oktober 2026", "privacy_device": "Fortschritt und Einstellungen", "privacy_device_copy": "Lokal auf deinem Gerät gespeichert",
        "privacy_account": "Konto", "privacy_account_copy": "Kein Konto erforderlich", "privacy_services": "Drittanbieter", "privacy_services_copy": "Apple StoreKit verarbeitet den Einmalkauf",
        "website_heading": "Diese Website", "website_body": "Diese statische Website nutzt keine Konten, Formulare, Cookies, Analyse, Werbung oder Tracking-Skripte von Drittanbietern. GitHub Pages kann gemäß den eigenen Richtlinien normale Anfrageprotokolle erhalten. Die Website verwendet diese Protokolle nicht, um dich zu identifizieren oder ein Profil zu erstellen.",
        "app_heading": "Was die App speichert", "app_body": "Reedwake speichert Fortschritt, Abzeichen und Einstellungen lokal auf deinem Gerät. Ein Konto ist nicht erforderlich und der Spielfortschritt wird nicht an einen Reedwake-Server gesendet. Wenn du die App löschst, werden lokale Daten entfernt, vorbehaltlich normaler Betriebssystem-Backups.",
        "purchase_heading": "Einmalkauf", "purchase_body": "Apple und StoreKit verarbeiten den optionalen, nicht verbrauchbaren Kauf der Vollversion. Die App erhält den verifizierten Berechtigungsstatus, aber keine Zahlungskartendaten. Der Kauf schaltet die sieben weiteren Regionen, 42 Storyüberquerungen, alle acht Gezeitenprüfungen und die vollständige Geschichte samt Ende frei. Der Basispreis in Spanien beträgt 3,99 €; Apple legt die Preise anderer Stores fest.",
        "services_heading": "Werbung, Konten und Analyse", "services_body": "Reedwake enthält keine Werbung, kein Kontosystem, kein Abonnement und keinen Analysedienst. StoreKit verarbeitet den optionalen Einmalkauf der Vollversion.",
        "deletion_heading": "Fortschritt und Löschen", "deletion_body": "Fortschritt und Einstellungen bleiben auf diesem Gerät. Wenn du Reedwake löschst, werden lokale Daten entfernt, vorbehaltlich normaler Betriebssystem-Backups. Wenn du die Vollversion freischaltest, kannst du den Kauf im Kaufdialog wiederherstellen.",
        "privacy_contact": "Hilfe findest du im Support-Bereich von Reedwake.", "privacy_back": "Hilfe & Support für Reedwake", "discover_title": "Eine erzählerische Reise jenseits der Puzzlewelten", "discover_copy": "Entdecke Reedwake: ein Flussabenteuer, in dem du zwischen Regen, Verkehr und zwei wechselnden Tiefen deinen Weg findest.",
        "footer": "Ein Flussabenteuer mit kostenloser Startregion und einmaliger Freischaltung des ganzen Spiels.",
    },
}


# Shared website language describes only common verified product behavior.
# Game-specific promises and controls remain in each metadata/website-content owner.
POCKET_SHARED = {
    "en": {"journey_label": "Pixel adventures", "journey_title": "A journey made for this game", "discover_title": "Seven pixel adventures to explore", "discover_copy": "Platform journeys, paired puzzles, shadow heists, a coast of memories, wind flights and a walking hearth. Each adventure begins with a free opening and offers one permanent full-game unlock.", "screens_intro": "Six native views show the core idea, two other worlds, deeper play, the journey’s rewards and its home or atlas.", "full_title": "Unlock the complete journey", "free_title": "Begin with the free opening", "controls_q": "How do I play?", "footer": "An authored pixel adventure with a free opening and one permanent full-game purchase.", "purchase_body": "Apple and StoreKit process the optional non-consumable full-game purchase. The app receives verified entitlement status; it does not receive or store payment-card details. The price appears in the purchase sheet before confirmation.", "privacy_updated": "Last updated: October 12, 2026"},
    "es": {"journey_label": "Aventuras píxel", "journey_title": "Un viaje propio de este juego", "discover_title": "Siete aventuras píxel por explorar", "discover_copy": "Plataformas, puzles en pareja, golpes de sombras, una costa de recuerdos, vuelos de viento y un hogar caminante. Cada aventura incluye un inicio gratuito y una compra permanente del juego completo.", "screens_intro": "Seis vistas nativas muestran la idea principal, otros dos mundos, mayor profundidad, las recompensas del viaje y su inicio o atlas.", "full_title": "Desbloquea el viaje completo", "free_title": "Empieza con el inicio gratuito", "controls_q": "¿Cómo se juega?", "footer": "Una aventura píxel diseñada con un inicio gratuito y una compra permanente del juego completo.", "purchase_body": "Apple y StoreKit gestionan la compra opcional no consumible del juego completo. La app recibe el estado de autorización verificado; no recibe ni guarda datos de tarjeta. El precio aparece en la pantalla de compra antes de confirmar.", "privacy_updated": "Última actualización: 12 de octubre de 2026"},
    "fr": {"journey_label": "Aventures en pixel art", "journey_title": "Un voyage propre à ce jeu", "discover_title": "Sept aventures en pixel art à explorer", "discover_copy": "Plateformes, puzzles en duo, casses d’ombre, côte de souvenirs, vols au vent et foyer ambulant. Chaque aventure propose un début gratuit et un achat permanent du jeu complet.", "screens_intro": "Six vues natives montrent l’idée principale, deux autres mondes, plus de profondeur, les récompenses du voyage et son accueil ou atlas.", "full_title": "Débloquez le voyage complet", "free_title": "Commencez gratuitement", "controls_q": "Comment jouer ?", "footer": "Une aventure en pixel art conçue avec un début gratuit et un achat permanent du jeu complet.", "purchase_body": "Apple et StoreKit gèrent l’achat facultatif non consommable du jeu complet. L’app reçoit l’état d’autorisation vérifié ; elle ne reçoit ni ne conserve les données de carte. Le prix apparaît avant confirmation dans la fenêtre d’achat.", "privacy_updated": "Dernière mise à jour : 12 octobre 2026"},
    "de": {"journey_label": "Pixelabenteuer", "journey_title": "Eine eigene Reise für dieses Spiel", "discover_title": "Sieben Pixelabenteuer zum Entdecken", "discover_copy": "Plattformreisen, Rätsel zu zweit, Schatten-Coups, eine Erinnerungsküste, Windflüge und eine wandernde Feuerstelle. Jedes Abenteuer bietet einen kostenlosen Einstieg und einen dauerhaften Vollspielkauf.", "screens_intro": "Sechs native Ansichten zeigen die Spielidee, zwei weitere Welten, tieferes Spiel, Reisebelohnungen und das Titelmenü oder den Atlas.", "full_title": "Schalte die ganze Reise frei", "free_title": "Beginne mit dem kostenlosen Einstieg", "controls_q": "Wie spiele ich?", "footer": "Ein gestaltetes Pixelabenteuer mit kostenlosem Einstieg und einem dauerhaften Vollspielkauf.", "purchase_body": "Apple und StoreKit verarbeiten den optionalen, nicht verbrauchbaren Vollspielkauf. Die App erhält den verifizierten Berechtigungsstatus, aber keine Zahlungskartendaten. Der Preis erscheint vor der Bestätigung im Kaufdialog.", "privacy_updated": "Zuletzt aktualisiert: 12. Oktober 2026"},
    "it": {"journey_label": "Avventure in pixel art", "journey_title": "Un viaggio proprio di questo gioco", "discover_title": "Sette avventure in pixel art da esplorare", "discover_copy": "Piattaforme, puzzle in coppia, colpi d’ombra, una costa di ricordi, voli nel vento e un focolare in cammino. Ogni avventura offre un inizio gratuito e un acquisto permanente del gioco completo.", "screens_intro": "Sei viste native mostrano l’idea principale, altri due mondi, maggiore profondità, le ricompense del viaggio e il titolo o l’atlante.", "full_title": "Sblocca il viaggio completo", "free_title": "Comincia con l’inizio gratuito", "controls_q": "Come si gioca?", "footer": "Un’avventura in pixel art progettata con un inizio gratuito e un acquisto permanente del gioco completo.", "purchase_body": "Apple e StoreKit gestiscono l’acquisto facoltativo non consumabile del gioco completo. L’app riceve lo stato verificato dell’autorizzazione, ma non riceve né conserva i dati della carta. Il prezzo appare nella schermata d’acquisto prima della conferma.", "privacy_updated": "Ultimo aggiornamento: 12 ottobre 2026"},
}


# Standing PocketColor default approved by the owner; see SUPPORT.md.
PUBLIC_SUPPORT_URL = "https://github.com/lorenzovillarroel90/LogicAtelierWebsite/issues/new"
SUPPORT_TEXT = {
    "en": {"title": "Contact support", "copy": "Ask a question or report a problem. Include the game name, your device and what happened.", "action": "Contact us on GitHub", "channel": "Reports are public and require a GitHub account."},
    "es": {"title": "Contactar con soporte", "copy": "Haz una pregunta o comunica un problema. Incluye el nombre del juego, tu dispositivo y qué ocurrió.", "action": "Contacta con nosotros en GitHub", "channel": "Los informes son públicos y requieren una cuenta de GitHub."},
    "fr": {"title": "Contacter l’assistance", "copy": "Posez une question ou signalez un problème. Indiquez le nom du jeu, votre appareil et ce qui s’est passé.", "action": "Contactez-nous sur GitHub", "channel": "Les signalements sont publics et nécessitent un compte GitHub."},
    "de": {"title": "Support kontaktieren", "copy": "Stelle eine Frage oder melde ein Problem. Nenne das Spiel, dein Gerät und was passiert ist.", "action": "Kontaktiere uns auf GitHub", "channel": "Meldungen sind öffentlich und erfordern ein GitHub-Konto."},
    "it": {"title": "Contatta l’assistenza", "copy": "Fai una domanda o segnala un problema. Indica il nome del gioco, il dispositivo e cosa è successo.", "action": "Contattaci su GitHub", "channel": "Le segnalazioni sono pubbliche e richiedono un account GitHub."},
}


def public_support_contact(lang: str) -> str:
    text = SUPPORT_TEXT[lang]
    return f'''<div class="support-contact"><h3>{esc(text["title"])}</h3><p>{esc(text["copy"])}</p><a class="button button-primary" href="{esc(PUBLIC_SUPPORT_URL)}" rel="noopener">{esc(text["action"])}</a><p>{esc(text["channel"])}</p></div>'''


VIDEO_TEXT = {
    "en": {"title": "English gameplay", "label": "{name} · English gameplay video", "copy": "A 24-second gameplay video in English. Additional content requires a one-time Full Game purchase.", "fallback": "Download the English gameplay video"},
    "es": {"title": "Vídeo de juego en inglés", "label": "{name} · vídeo de juego en inglés", "copy": "Un vídeo de juego de 24 segundos en inglés. El contenido adicional requiere una compra única del juego completo.", "fallback": "Descargar el vídeo de juego en inglés"},
    "fr": {"title": "Vidéo de jeu en anglais", "label": "{name} · vidéo de jeu en anglais", "copy": "Une vidéo de jeu de 24 secondes en anglais. Le contenu supplémentaire nécessite un achat unique du jeu complet.", "fallback": "Télécharger la vidéo de jeu en anglais"},
    "de": {"title": "Spielvideo auf Englisch", "label": "{name} · Spielvideo auf Englisch", "copy": "Ein 24-sekündiges Spielvideo auf Englisch. Zusätzliche Inhalte erfordern einen einmaligen Vollspielkauf.", "fallback": "Spielvideo auf Englisch herunterladen"},
    "it": {"title": "Video di gioco in inglese", "label": "{name} · video di gioco in inglese", "copy": "Un video di gioco di 24 secondi in inglese. I contenuti aggiuntivi richiedono un acquisto unico del gioco completo.", "fallback": "Scarica il video di gioco in inglese"},
}


def approved_videos() -> dict[str, dict]:
    """One explicit, hash-pinned source owner for lead-approved English movies."""
    manifest = json.loads(read_text(WEBSITE / "approved-videos.json"))
    if manifest["schemaVersion"] != 1:
        raise ValueError("Unsupported approved video manifest version.")
    # A lead hold removes all candidate movies from generated/public pages.
    # Durable accepted sources stay intact for the subsequent media review.
    videos = manifest["videos"] if manifest.get("publicationEnabled", True) else {}
    if set(videos) - set(POCKET_BRANDS):
        raise ValueError("Approved video manifest names an unknown game.")
    for video in videos.values():
        for key in ("movie", "report"):
            path = Path(video[key])
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Approved video sources must stay relative to the external source root.")
    return videos


def public_name(app: dict, lang: str) -> str:
    """Use approved localized game names; routing identities stay internal."""
    return app["name"][lang] if app.get("family") == "pocketcolor" else app["brand"]


def pocket_text(app: dict, lang: str) -> dict:
    """Keep Reedwake’s approved copy; replace shared facts for each new owner."""
    if app["brand"] == "Reedwake":
        return POCKET_TEXT[lang]
    text = {key: value.replace("Reedwake", public_name(app, lang)) for key, value in POCKET_TEXT[lang].items()}
    text.update(POCKET_SHARED[lang])
    product = app["website"][lang]
    text.update({"free_replay": product["free"], "controls_a": product["controls"], "save_a": product["save"], "app_body": product["save"], "price": ""})
    if "privacy_device" in product:
        text.update({"privacy_device": product["privacy_device"], "app_body": product["save"], "deletion_body": product["save"]})
        text["privacy_intro"] = f'{app["name"][lang]} · {product["privacy_device"]}. {text["services_body"]}'
    return text


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_apps() -> dict[str, dict]:
    apps = {}
    for brand, slug in zip(BRANDS, SLUGS):
        source = ROOT / "AppStoreMetaData" / brand / "v1.0"
        store_id = APP_STORE_IDS.get(slug)
        apps[slug] = {
            "brand": brand,
            "family": "puzzle",
            "name": {lang: read_text(source / "app-name" / f"{lang}.txt") for lang in LANGS},
            "subtitle": {lang: read_text(source / "subtitle" / f"{lang}.txt") for lang in LANGS},
            "promo": {lang: read_text(source / "promotional-text" / f"{lang}.txt") for lang in LANGS},
            "description": {lang: read_text(source / "app-description" / f"{lang}.txt") for lang in LANGS},
            "headlines": {lang: json.loads(read_text(source / "screenshot-headlines" / f"{lang}.json"))["screenshots"] for lang in LANGS},
            "screenshot_files": PUZZLE_SCREENSHOT_FILES,
            "theme": THEMES[slug],
            # The store CTA also requires a verified numeric ID and derived URL.
            "store_live": False,
            "store_id": store_id,
            "store_url": f"https://apps.apple.com/app/id{store_id}" if store_id else None,
        }
    return apps


def load_pocket_games(source_root: Path = ROOT) -> dict[str, dict]:
    """Load optional PocketColor products from the same approved metadata matrix."""
    apps: dict[str, dict] = {}
    videos = approved_videos()
    for brand, slug in zip(POCKET_BRANDS, POCKET_SLUGS):
        source = source_root / "AppStoreMetaData" / brand / "v1.0"
        if not source.is_dir():
            continue
        store_id = APP_STORE_IDS.get(slug)
        apps[slug] = {
            "brand": brand,
            "family": "pocketcolor",
            "name": {lang: read_text(source / "app-name" / f"{lang}.txt") for lang in LANGS},
            "subtitle": {lang: read_text(source / "subtitle" / f"{lang}.txt") for lang in LANGS},
            "promo": {lang: read_text(source / "promotional-text" / f"{lang}.txt") for lang in LANGS},
            "description": {lang: read_text(source / "app-description" / f"{lang}.txt") for lang in LANGS},
            "headlines": {lang: json.loads(read_text(source / "screenshot-headlines" / f"{lang}.json"))["screenshots"] for lang in LANGS},
            "screenshot_files": POCKET_SCREENSHOT_FILES if brand in APPROVED_POCKET_MEDIA else (),
            "theme": {"accent": "#D7D998", "companion": "#7ABC86", "wash": "#EFF6E4", "ink": "#28413C"},
            "video": videos.get(brand),
            "website": {lang: json.loads(read_text(source / "website-content" / f"{lang}.json")) for lang in LANGS} if brand != "Reedwake" else None,
            # A verified record ID never establishes public availability.
            "store_live": False,
            "store_id": store_id,
            "store_url": f"https://apps.apple.com/app/id{store_id}" if store_id else None,
        }
    return apps


def app_icon_source(source_root: Path, app: dict) -> Path:
    if app.get("family") == "pocketcolor":
        catalog = source_root / "ios" / "PocketColor" / "ios-projects" / app["brand"] / "App" / "Assets.xcassets" / "AppIcon.appiconset"
        images = json.loads(read_text(catalog / "Contents.json"))["images"]
        filenames = {image["filename"] for image in images if image.get("filename") and image.get("size") == "1024x1024"}
        if len(filenames) != 1:
            raise ValueError(f"{catalog}: expected one authoritative 1024px app icon; found {filenames}.")
        return catalog / next(iter(filenames))
    return source_root / "ios" / "LogicAtelier" / "ios-projects" / app["brand"] / app["brand"] / "Assets.xcassets" / "AppIcon.appiconset" / "AppIcon.png"


def app_screenshot_source(source_root: Path, app: dict, lang: str, filename: str) -> Path:
    return source_root / "AppStoreScreenshots" / app["brand"] / "v1.0" / "iPhone" / lang / f"{filename}.png"


def route_file(lang: str, slug: str | None = None, privacy: bool = False) -> Path:
    parts = [] if lang == "en" else [lang]
    if slug:
        parts.append(slug)
    if privacy:
        return Path(*parts) / "privacy.html"
    return Path(*parts) / "index.html"


def public_route(lang: str, slug: str | None = None, privacy: bool = False) -> str:
    parts = [] if lang == "en" else [lang]
    if slug:
        parts.append(slug)
    route = "/".join(parts)
    if privacy:
        route = f"{route}/privacy.html" if route else "privacy.html"
    else:
        route = f"{route}/" if route else ""
    return BASE + route


def rel_href(source: Path, target: Path) -> str:
    relative = posixpath.relpath(target.as_posix(), start=source.parent.as_posix())
    if relative.endswith("/index.html"):
        relative = relative[: -len("index.html")]
    elif relative == "index.html":
        relative = "./"
    return relative


def absolute_asset(source: Path, target: Path) -> str:
    return rel_href(source, target)


def parse_description(description: str) -> tuple[str, str, str, str, list[str], str, str]:
    parts = description.split("\n\n")
    while len(parts) < 6:
        parts.append("")
    section_lines = parts[3].splitlines()
    section_title = section_lines[0] if section_lines else ""
    bullets = [line[2:].strip() for line in section_lines[1:] if line.startswith("•")]
    return parts[0], parts[1], parts[2], section_title, bullets, parts[4], parts[5]


def make_hreflang(current: Path, slug: str | None, privacy: bool) -> str:
    lines = []
    for lang in LANGS:
        lines.append(f'<link rel="alternate" hreflang="{lang}" href="{esc(public_route(lang, slug, privacy))}">')
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{esc(public_route("en", slug, privacy))}">')
    return "\n    ".join(lines)


def make_language_links(current: Path, lang: str, slug: str | None, privacy: bool) -> str:
    links = []
    for target_lang in LANGS:
        target = SITE / route_file(target_lang, slug, privacy)
        current_flag = ' aria-current="true"' if target_lang == lang else ""
        links.append(f'<a href="{esc(rel_href(current, target))}" lang="{target_lang}"{current_flag}>{esc(LANGUAGE_SHORT[target_lang])}</a>')
    return "".join(links)


def make_header(current: Path, lang: str, slug: str | None, privacy: bool, apps: dict[str, dict]) -> str:
    c = COMMON[lang]
    home = route_file(lang)
    game_home = route_file(lang, slug) if slug else home
    privacy_target = route_file(lang, slug, True) if slug else None
    nav_game = f'<a href="{esc(rel_href(current, SITE / game_home))}">{esc(c["all_games"] if not slug else public_name(apps[slug], lang))}</a>'
    nav_privacy = f'<a href="{esc(rel_href(current, SITE / privacy_target))}">{esc(c["privacy"])}</a>' if privacy_target else f'<a href="#privacy-pages">{esc(c["privacy"])}</a>'
    nav_support = ""
    if slug and apps[slug].get("family") == "pocketcolor":
        support_href = rel_href(current, SITE / route_file(lang, slug)) + "#support"
        nav_support = f'<a href="{esc(support_href)}">{esc(POCKET_TEXT[lang]["support_nav"])}</a>'
    brand_image = ""
    if slug:
        icon = Path("assets") / "icons" / f"{slug}.png"
        brand_image = f'<img src="{esc(rel_href(current, SITE / icon))}" width="42" height="42" alt="">'
    else:
        brand_image = '<span class="brand-glyph" aria-hidden="true">✦</span>'
    return f'''<header class="site-header">
  <nav class="nav" aria-label="{esc(c["all_games"])}">
    <a class="brand" href="{esc(rel_href(current, SITE / home))}" aria-label="{esc(c["collection"])}"><span class="brand-mark">{brand_image}</span><span>{esc(c["collection_short"])}</span></a>
    <div class="nav-links">{nav_game}{nav_privacy}{nav_support}<details class="language"><summary aria-label="{esc(c["language"])}">{esc(LANGUAGE_SHORT[lang])}</summary><div class="language-panel">{make_language_links(current, lang, slug, privacy)}</div></details></div>
    <details class="nav-menu"><summary>{esc(c["all_games"])}</summary><div class="nav-menu-panel">{nav_game}{nav_privacy}{nav_support}<div class="mobile-languages"><span>{esc(c["language"])}</span>{make_language_links(current, lang, slug, privacy)}</div></div></details>
  </nav>
</header>'''


def make_footer(current: Path, lang: str, slug: str | None, apps: dict[str, dict]) -> str:
    c = COMMON[lang]
    footer_note = pocket_text(apps[slug], lang)["footer"] if slug and apps[slug].get("family") == "pocketcolor" else c["footer_note"]
    links = [f'<a href="{esc(rel_href(current, SITE / route_file(lang))) }">{esc(c["all_games"])}</a>']
    if slug:
        links.append(f'<a href="{esc(rel_href(current, SITE / route_file(lang, slug, True)))}">{esc(c["privacy"])}</a>')
        if apps[slug].get("family") == "pocketcolor":
            links.append(f'<a href="{esc(rel_href(current, SITE / route_file(lang, slug)))}#support">{esc(POCKET_TEXT[lang]["support_nav"])}</a>')
    else:
        links.append(f'<a href="#privacy-pages">{esc(c["site_privacy"])}</a>')
    return f'''<footer class="site-footer"><div class="footer-inner"><div><a class="brand" href="{esc(rel_href(current, SITE / route_file(lang)))}"><span class="brand-mark"><span class="brand-glyph" aria-hidden="true">✦</span></span><span>{esc(c["collection_short"])}</span></a><p>{esc(footer_note)}</p></div><nav aria-label="{esc(c["privacy"])}">{"".join(links)}</nav></div><p class="footer-bottom">© 2026 · {esc(c["collection_short"])}.</p></footer>'''


def make_head(current: Path, lang: str, title: str, description: str, canonical: str, og_image: str, og_alt: str, slug: str | None, privacy: bool, jsonld: dict | None = None) -> str:
    icon = SITE / "assets" / "icons" / f"{slug}.png" if slug else None
    icon_link = f'<link rel="icon" href="{esc(rel_href(current, icon))}" type="image/png">' if icon else ""
    css = rel_href(current, SITE / "styles.css")
    script = rel_href(current, SITE / "script.js")
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f'''<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{esc(canonical)}">{make_hreflang(current, slug, privacy)}
  <meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="{esc(og_image)}"><meta property="og:image:alt" content="{esc(og_alt)}"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#101A34">
  {icon_link}<link rel="stylesheet" href="{esc(css)}">{ld}
</head>'''


def page_shell(current: Path, lang: str, title: str, description: str, canonical: str, og_image: str, og_alt: str, slug: str | None, privacy: bool, content: str, jsonld: dict | None = None, apps: dict[str, dict] | None = None) -> str:
    theme = THEMES.get(slug or "", {})
    style = "" if not theme else f' style="--accent:{theme["accent"]};--companion:{theme["companion"]};--wash:{theme["wash"]};--brand-ink:{theme["ink"]}"'
    c = COMMON[lang]
    page_apps = apps or load_apps()
    page_class = "app-page" if slug and not privacy else "privacy-page" if privacy else "hub-page"
    return f'''<!doctype html><html lang="{lang}"><!-- Generated by Website/build.py; keep site/ deployable without a build step. --><body class="{page_class}"{style}><a class="skip-link" href="#main">{esc(c["skip"])}</a>{make_header(current, lang, slug, privacy, page_apps)}<main id="main">{content}</main>{make_footer(current, lang, slug, page_apps)}<script src="{esc(rel_href(current, SITE / "script.js"))}"></script></body></html>'''.replace("<body", f"{make_head(current, lang, title, description, canonical, og_image, og_alt, slug, privacy, jsonld)}<body", 1)


def image_path(slug: str, lang: str, filename: str) -> Path:
    return SITE / "assets" / "screens" / lang / slug / f"{filename}.jpg"


def app_card(current: Path, lang: str, app: dict, slug: str) -> str:
    c = COMMON[lang]
    route = SITE / route_file(lang, slug)
    icon = SITE / "assets" / "icons" / f"{slug}.png"
    theme = app["theme"]
    return f'''<article class="game-card" style="--accent:{theme["accent"]};--companion:{theme["companion"]};--wash:{theme["wash"]}">
  <a class="game-card-link" href="{esc(rel_href(current, route))}"><img src="{esc(rel_href(current, icon))}" width="96" height="96" loading="lazy" alt="{esc(f'{app["name"][lang]} app icon')}"><span class="game-card-copy"><strong>{esc(public_name(app, lang))}</strong><span>{esc(app["subtitle"][lang])}</span><em>{esc(c["explore"])} <span aria-hidden="true">↗</span></em></span></a>
</article>'''


def build_hub(lang: str, apps: dict[str, dict]) -> None:
    current = SITE / route_file(lang)
    c = COMMON[lang]
    title = f'{c["collection"]} · {c["hub_title"]}'
    description = c["hub_lede"]
    og = BASE + "assets/icons/evenbeam.png"
    cards = "".join(app_card(current, lang, apps[slug], slug) for slug in SLUGS)
    privacy_links = "".join(f'<a href="{esc(rel_href(current, SITE / route_file(lang, slug, True)))}">{esc(public_name(apps[slug], lang))} · {esc(c["privacy"])}</a>' for slug in SLUGS)
    pocket_section = ""
    pocket_slugs = [slug for slug in POCKET_SLUGS if slug in apps]
    if pocket_slugs:
        p = POCKET_SHARED[lang]
        pocket_cards = "".join(app_card(current, lang, apps[slug], slug) for slug in pocket_slugs)
        pocket_section = f'''<section class="section" aria-labelledby="pocket-games-title"><div class="section-heading"><div><p class="eyebrow">{esc(p["journey_label"])}</p><h2 id="pocket-games-title">{esc(p["discover_title"])}</h2></div><p>{esc(p["discover_copy"])}</p></div><div class="game-grid">{pocket_cards}</div></section>'''
        privacy_links += "".join(f'<a href="{esc(rel_href(current, SITE / route_file(lang, slug, True)))}">{esc(public_name(apps[slug], lang))} · {esc(c["privacy"])}</a>' for slug in pocket_slugs)
    content = f'''<section class="hub-hero"><div class="hero-grid"><div><p class="eyebrow">{esc(c["hub_eyebrow"])}</p><h1>{esc(c["hub_title"])}</h1><p class="lede">{esc(c["hub_lede"])}</p><a class="button button-primary" href="#games">{esc(c["games"])}</a></div><div class="orbit-art" aria-label="{esc(c["orbit_alt"])}"><span class="orbit orbit-a"></span><span class="orbit orbit-b"></span><span class="float-shape shape-a">✦</span><span class="float-shape shape-b">⌁</span><span class="float-shape shape-c">◆</span><span class="float-shape shape-d">●</span></div></div></section>
<section class="section" id="games" aria-labelledby="games-title"><div class="section-heading"><div><p class="eyebrow">{esc(c["games"])}</p><h2 id="games-title">{esc(c["games_intro"])}</h2></div></div><div class="game-grid">{cards}</div></section>
<section class="section soft-section" aria-labelledby="values-title"><div class="section-heading"><div><p class="eyebrow">{esc(c["collection"])}</p><h2 id="values-title">{esc(c["collection_title"])}</h2></div><p>{esc(c["collection_copy"])}</p></div><div class="value-grid"><article><strong>100</strong><h3>{esc(c["curated"])}</h3><p>{esc(c["curated_copy"])}</p></article><article><strong>∞</strong><h3>{esc(c["endless"])}</h3><p>{esc(c["endless_copy"])}</p></article><article><strong>◷</strong><h3>{esc(c["calm"])}</h3><p>{esc(c["calm_copy"])}</p></article></div></section>
{pocket_section}
<section class="section compact-section" id="privacy-pages" aria-labelledby="privacy-discover-title"><div class="section-heading"><div><p class="eyebrow">{esc(c["privacy"])}</p><h2 id="privacy-discover-title">{esc(c["site_privacy_title"])}</h2></div><p>{esc(c["site_privacy_desc"])}</p></div><div class="privacy-links">{privacy_links}</div></section>'''
    jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": c["collection"], "url": public_route(lang), "description": description, "inLanguage": lang}
    (SITE / route_file(lang)).parent.mkdir(parents=True, exist_ok=True)
    (SITE / route_file(lang)).write_text(page_shell(current, lang, title, description, public_route(lang), og, c["collection"], None, False, content, jsonld), encoding="utf-8")


def screenshot_cards(current: Path, lang: str, slug: str, app: dict, c: dict) -> str:
    cards = []
    headlines = app["headlines"][lang]
    screenshot_files = app["screenshot_files"]
    if len(headlines) != len(screenshot_files):
        raise ValueError(f"{slug}/{lang}: expected {len(screenshot_files)} screenshot headlines, found {len(headlines)}.")
    for idx, (filename, headline) in enumerate(zip(screenshot_files, headlines), start=1):
        target = image_path(slug, lang, filename)
        # JSON parsing yields a real newline; preserve the approved two-line
        # headline rather than relying on browser whitespace collapsing.
        lines = esc(headline["headline"]).replace("\n", "<br>")
        alt = f'{app["name"][lang]} · {headline["headline"].replace(chr(10), " ")}'
        cards.append(f'<figure class="shot-card"><div class="shot-frame"><img src="{esc(rel_href(current, target))}" width="720" height="1564" loading="lazy" alt="{esc(alt)}"></div><figcaption><span>{idx:02d}</span><strong>{lines}</strong></figcaption></figure>')
    return "".join(cards)


def build_app(lang: str, slug: str, app: dict, apps: dict[str, dict]) -> None:
    current = SITE / route_file(lang, slug)
    c = COMMON[lang]
    name = app["name"][lang]
    intro, body_one, body_two, section_title, bullets, monetization, no_account = parse_description(app["description"][lang])
    icon = SITE / "assets" / "icons" / f"{slug}.png"
    hero_image = image_path(slug, lang, app["screenshot_files"][0])
    og = BASE + f"assets/screens/{lang}/{slug}/{app['screenshot_files'][0]}.jpg"
    title = f"{name} · {app['subtitle'][lang]}"
    description = app["promo"][lang]
    bullet_html = "".join(f"<li>{esc(item)}</li>" for item in bullets)
    store_cta = (f'<a class="button button-primary" href="{esc(app["store_url"])}">{esc(STORE_LABELS[lang])}</a>' if app["store_live"] and app["store_url"] else f'<p class="coming"><span aria-hidden="true">●</span>{esc(c["coming"])}</p>')
    other = "".join(app_card(current, lang, apps[other_slug], other_slug) for other_slug in SLUGS if other_slug != slug)
    hero_alt = f'{name}: {app["headlines"][lang][0]["headline"].replace(chr(10), " ")}'
    content = f'''<section class="app-hero"><div class="app-hero-grid"><div class="app-hero-copy"><div class="app-title"><img src="{esc(rel_href(current, icon))}" width="88" height="88" alt="{esc(f'{name} app icon')}"><div><p class="eyebrow">{esc(public_name(app, lang))}</p><h1>{esc(name)}</h1></div></div><p class="lede">{esc(intro)}</p>{store_cta}</div><div class="hero-shot-wrap"><div class="hero-ring" aria-hidden="true"></div><div class="hero-shot"><img src="{esc(rel_href(current, hero_image))}" width="720" height="1564" alt="{esc(hero_alt)}"></div></div></div></section>
<section class="section" aria-labelledby="idea-title"><div class="split"><div><p class="eyebrow">{esc(c["how"])}</p><h2 id="idea-title">{esc(body_one)}</h2><p class="body-copy">{esc(body_two)}</p></div><div class="feature-panel"><h3>{esc(section_title.title())}</h3><ul class="checklist">{bullet_html}</ul></div></div></section>
<section class="section soft-section" aria-labelledby="collection-title"><div class="section-heading"><div><p class="eyebrow">{esc(c["collection"])}</p><h2 id="collection-title">{esc(c["collection_title"])}</h2></div><p>{esc(c["collection_copy"])}</p></div><div class="value-grid"><article><strong>100</strong><h3>{esc(c["curated"])}</h3><p>{esc(c["curated_copy"])}</p></article><article><strong>∞</strong><h3>{esc(c["endless"])}</h3><p>{esc(c["endless_copy"])}</p></article><article><strong>↺</strong><h3>{esc(c["calm"])}</h3><p>{esc(c["calm_copy"])}</p></article></div></section>
<section class="section shots-section" aria-labelledby="screens-title"><div class="section-heading"><div><p class="eyebrow">{esc(c["screens"])}</p><h2 id="screens-title">{esc(c["screens"])}</h2></div><p>{esc(c["screens_intro"])}</p></div><div class="shots-grid">{screenshot_cards(current, lang, slug, app, c)}</div></section>
<section class="section" aria-labelledby="pro-title"><div class="pro-panel"><div><p class="eyebrow">{esc(c["free_pro"])}</p><h2 id="pro-title">{esc(c["free_pro"])}</h2><p>{esc(c["free_copy"])}</p></div><div class="pro-card"><span>PRO</span><p>{esc(c["pro_copy"])}</p></div></div></section>
<section class="section soft-section" aria-labelledby="other-title"><div class="section-heading"><div><p class="eyebrow">{esc(c["other"])}</p><h2 id="other-title">{esc(c["other"])}</h2></div><p>{esc(c["other_intro"])}</p></div><div class="game-grid other-grid">{other}</div></section>'''
    jsonld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": name, "applicationCategory": "PuzzleGame", "operatingSystem": "iOS", "description": description, "image": og, "url": public_route(lang, slug), "inLanguage": lang}
    if app["store_live"] and app["store_url"]:
        jsonld["downloadUrl"] = app["store_url"]
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text(page_shell(current, lang, title, description, public_route(lang, slug), og, name, slug, False, content, jsonld), encoding="utf-8")


def build_privacy(lang: str, slug: str, app: dict, apps: dict[str, dict]) -> None:
    current = SITE / route_file(lang, slug, True)
    c = COMMON[lang]
    name = app["name"][lang]
    title = c["privacy_title"].format(name=name)
    description = f"{name}. {c['site_privacy_desc']}"
    icon = SITE / "assets" / "icons" / f"{slug}.png"
    og = BASE + f"assets/icons/{slug}.png"
    privacy_sections = [("website", c["website_heading"], c["website_body"]), ("app", c["app_heading"], c["app_body"]), ("ads", c["ads_heading"], c["ads_body"]), ("pro", c["pro_heading"], c["pro_body"]), ("sharing", c["sharing_heading"], c["sharing_body"])]
    body = "".join(f'<section class="policy-section" id="{key}"><h2>{esc(heading)}</h2><p>{esc(text)}</p></section>' for key, heading, text in privacy_sections)
    content = f'''<section class="page-hero"><div class="narrow"><p class="eyebrow">{esc(c["privacy_eyebrow"])}</p><h1>{esc(title)}</h1><p class="lede">{esc(c["privacy_intro"].format(name=name))}</p><p class="updated">{esc(c["privacy_updated"])}</p></div></section><section class="section policy-wrap"><div class="policy-summary"><div><strong>{esc(c["privacy_summary_device"])}</strong><span>{esc(c["privacy_summary_device_copy"])}</span></div><div><strong>{esc(c["privacy_summary_account"])}</strong><span>{esc(c["privacy_summary_account_copy"])}</span></div><div><strong>{esc(c["privacy_summary_ads"])}</strong><span>{esc(c["privacy_summary_ads_copy"])}</span></div></div><div class="policy-layout"><aside class="policy-nav"><strong>{esc(c["privacy"])}</strong><a href="#website">{esc(c["website_heading"])}</a><a href="#app">{esc(c["app_heading"])}</a><a href="#ads">{esc(c["ads_heading"])}</a><a href="#pro">{esc(c["pro_heading"])}</a><a href="#sharing">{esc(c["sharing_heading"])}</a><a href="#links">{esc(c["links_heading"])}</a></aside><div>{body}<section class="policy-section" id="links"><h2>{esc(c["links_heading"])}</h2><p><a href="https://policies.google.com/privacy" rel="noopener">{esc(c["google_policy"])}</a> · <a href="https://www.apple.com/legal/privacy/" rel="noopener">{esc(c["apple_policy"])}</a></p><p>{esc(c["privacy_contact"])}</p></section></div></div></section>'''
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text(page_shell(current, lang, title, description, public_route(lang, slug, True), og, name, slug, True, content), encoding="utf-8")


def catalog_text(relative_path: str, source_key: str, lang: str) -> str:
    catalog_path = ROOT / relative_path
    catalog = json.loads(read_text(catalog_path))
    value = catalog["strings"][source_key]["localizations"][lang]["stringUnit"]["value"]
    return value


def metadata_description(description: str) -> str:
    blocks = []
    for paragraph in description.split("\n\n"):
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue
        bullet_lines = [line for line in lines if line.startswith(("•", "-", "–"))]
        if len(bullet_lines) == len(lines):
            items = "".join(f"<li>{esc(line.lstrip('•-– '))}</li>" for line in lines)
            blocks.append(f'<ul class="checklist">{items}</ul>')
        elif lines[0].startswith("#"):
            blocks.append(f'<h3>{esc(lines[0].lstrip("# "))}</h3>')
            if len(lines) > 1:
                blocks.append(f'<p>{esc(" ".join(lines[1:]))}</p>')
        elif len(lines) == 1 and lines[0].upper() == lines[0] and any(char.isalpha() for char in lines[0]):
            blocks.append(f'<h3>{esc(lines[0])}</h3>')
        else:
            blocks.append(f'<p>{esc(" ".join(lines))}</p>')
    return "".join(blocks)


def gameplay_video(current: Path, lang: str, slug: str, app: dict) -> str:
    if not app.get("video"):
        return ""
    v = VIDEO_TEXT[lang]
    root = SITE / "assets" / "videos" / slug
    movie = esc(rel_href(current, root / "gameplay-en.mp4"))
    poster = esc(rel_href(current, root / "poster.jpg"))
    label = esc(v["label"].format(name=app["name"][lang]))
    return f'''<section class="section gameplay-section" aria-labelledby="gameplay-title"><div class="section-heading"><h2 id="gameplay-title">{esc(v["title"])}</h2><p id="gameplay-description">{esc(v["copy"])}</p></div><video class="gameplay-video" controls playsinline preload="metadata" poster="{poster}" width="886" height="1920" aria-label="{label}" aria-describedby="gameplay-description"><source src="{movie}" type="video/mp4"><a href="{movie}">{esc(v["fallback"])}</a></video></section>'''


def build_pocket_app(lang: str, slug: str, app: dict, apps: dict[str, dict]) -> None:
    current = SITE / route_file(lang, slug)
    c = COMMON[lang]
    p = pocket_text(app, lang)
    name = app["name"][lang]
    title = f'{name} · {app["subtitle"][lang]}'
    description = app["promo"][lang]
    icon = SITE / "assets" / "icons" / f"{slug}.png"
    has_media = bool(app["screenshot_files"])
    og = BASE + (f"assets/screens/{lang}/{slug}/{app['screenshot_files'][0]}.jpg" if has_media else f"assets/icons/{slug}.png")
    hero_html = ""
    gallery_html = ""
    if has_media:
        hero = image_path(slug, lang, app["screenshot_files"][0])
        headline = app["headlines"][lang][0]["headline"].replace("\n", " ")
        hero_html = f'<div class="hero-shot-wrap"><div class="hero-ring" aria-hidden="true"></div><div class="hero-shot"><img src="{esc(rel_href(current, hero))}" width="720" height="1564" alt="{esc(f"{name}: {headline}")}" fetchpriority="high"></div></div>'
        gallery_html = f'<section class="section shots-section" aria-labelledby="screens-title"><div class="section-heading"><div><p class="eyebrow">{esc(c["screens"])}</p><h2 id="screens-title">{esc(c["screens"])}</h2></div><p>{esc(p["screens_intro"])}</p></div><div class="shots-grid">{screenshot_cards(current, lang, slug, app, c)}</div></section>'

    if app["brand"] == "Reedwake":
        stats = "".join([
            f'<article><strong>48</strong><h3>{esc(p["story_routes"])}</h3></article>',
            f'<article><strong>8</strong><h3>{esc(p["regions"])}</h3></article>',
            f'<article><strong>8</strong><h3>{esc(p["trials"])}</h3></article>',
            f'<article><strong>2</strong><h3>{esc(p["depths"])}</h3></article>',
        ])
        free_copy = catalog_text("ios/PocketColor/Packages/Reedwake/Sources/ReedwakeKit/Resources/Reedwake.xcstrings", "Wakewater Gardens: the first six story crossings.", lang)
        full_copy = catalog_text("ios/PocketColor/Packages/Reedwake/Sources/ReedwakeKit/Resources/Reedwake.xcstrings", "Unlock seven more regions, 42 more story crossings, all eight Tide Trials, and the complete story and ending.", lang)
        move_copy = catalog_text("ios/PocketColor/Packages/Reedwake/Sources/ReedwakeKit/Resources/Reedwake.xcstrings", "D-pad moves Nim one tile per beat. Hold a direction to keep hopping. Reach the sun-tree at the far bank. There is no countdown or lives limit.", lang)
        depth_copy = catalog_text("ios/PocketColor/Packages/Reedwake/Sources/ReedwakeKit/Resources/Reedwake.xcstrings", "A dives or rises. Root roofs block the top. Shallow shelves block the bottom. Find their openings and change layers BEFORE crossing. A arrows beside lanes show the open layer.", lang)
        journey_copy = catalog_text("ios/PocketColor/Packages/Reedwake/Sources/ReedwakeKit/Resources/Reedwake.xcstrings", "X scouts both layers without losing time. START pauses. Settings offer gentle pace and quiet motion. The atlas has 48 story routes plus eight optional Tide Trials.", lang)
    else:
        product = app["website"][lang]
        stats = ""
        free_copy, full_copy = product["free"], product["full"]
        move_copy, depth_copy = "", ""
        journey_copy = product["journey"]
    restore_action = catalog_text("ios/PocketColor/Packages/PocketCommerce/Sources/PocketCommerce/Resources/PocketCommerce.xcstrings", "Restore purchases", lang)
    faq = [
        (p["controls_q"], f'{esc(p["controls_a"])}<p>{esc(move_copy)}</p><p>{esc(depth_copy)}</p>'),
        (p["save_q"], esc(p["save_a"])),
        (p["content_q"], esc(free_copy)),
        (p["purchase_q"], f'{esc(full_copy)}<p>{esc(p["one_time"])} {esc(p["price"])}</p>'),
        (p["restore_q"], f'{esc(p["restore_a_prefix"])} <strong>{esc(restore_action)}</strong>.'),
        (p["pending_q"], esc(p["pending_a"])),
    ]
    store_cta = f'<a class="button button-primary" href="{esc(app["store_url"])}">{esc(STORE_LABELS[lang])}</a>' if app["store_live"] and app["store_url"] else f'<p class="coming"><span aria-hidden="true">●</span>{esc(c["coming"])}</p>'
    faq_html = "".join(f'<details class="support-answer"><summary>{esc(question)}</summary><div>{answer}</div></details>' for question, answer in faq)
    content = f'''<section class="app-hero"><div class="app-hero-grid{' copy-only' if not has_media else ''}"><div class="app-hero-copy"><div class="app-title"><img src="{esc(rel_href(current, icon))}" width="88" height="88" alt="{esc(f'{name} app icon')}"><div><p class="eyebrow">{esc(public_name(app, lang))}</p><h1>{esc(name)}</h1></div></div><p class="lede">{esc(description)}</p>{store_cta}<p>{esc(p["free_replay"])}</p></div>{hero_html}</div></section>
<section class="section" aria-labelledby="journey-title"><div class="section-heading"><div><p class="eyebrow">{esc(p["journey_label"])}</p><h2 id="journey-title">{esc(p["journey_title"])}</h2></div><p>{esc(journey_copy)}</p></div><div class="value-grid pocket-stats">{stats}</div></section>
<section class="section soft-section" aria-labelledby="free-title"><div class="pro-panel"><div><p class="eyebrow">{esc(p["free_title"])}</p><h2 id="free-title">{esc(free_copy)}</h2><p>{esc(p["free_replay"])}</p></div><div class="pro-card"><span>{esc(p["full_title"])}</span><p>{esc(full_copy)}</p><p>{esc(p["one_time"])}</p><p>{esc(p["price"])}</p></div></div></section>
<section class="section" aria-labelledby="story-copy-title"><div class="section-heading"><div><p class="eyebrow">{esc(public_name(app, lang))}</p><h2 id="story-copy-title">{esc(app["subtitle"][lang])}</h2></div></div><div class="store-copy">{metadata_description(app["description"][lang])}</div></section>
{gallery_html}
{gameplay_video(current, lang, slug, app)}
<section class="section" id="support" aria-labelledby="support-title"><div class="section-heading"><div><p class="eyebrow">{esc(p["faq_label"])}</p><h2 id="support-title">{esc(p["faq_title"])}</h2></div><p>{esc(p["support_intro"])}</p></div><div class="support-list">{faq_html}</div>{public_support_contact(lang)}</section>'''
    jsonld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": name, "applicationCategory": "VideoGame", "operatingSystem": "iOS", "description": description, "image": og, "url": public_route(lang, slug), "inLanguage": lang}
    if app["store_live"] and app["store_url"]:
        jsonld["downloadUrl"] = app["store_url"]
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text(page_shell(current, lang, title, description, public_route(lang, slug), og, name, slug, False, content, jsonld, apps), encoding="utf-8")


def build_pocket_privacy(lang: str, slug: str, app: dict, apps: dict[str, dict]) -> None:
    current = SITE / route_file(lang, slug, True)
    c = COMMON[lang]
    p = pocket_text(app, lang)
    name = app["name"][lang]
    title = p["privacy_title"].format(name=name)
    description = p["privacy_intro"]
    og = BASE + f"assets/icons/{slug}.png"
    policies = [
        ("website", p["website_heading"], p["website_body"]),
        ("app", p["app_heading"], p["app_body"]),
        ("purchase", p["purchase_heading"], p["purchase_body"]),
        ("services", p["services_heading"], p["services_body"]),
        ("deletion", p["deletion_heading"], p["deletion_body"]),
    ]
    body = "".join(f'<section class="policy-section" id="{key}"><h2>{esc(heading)}</h2><p>{esc(text)}</p></section>' for key, heading, text in policies)
    support_href = rel_href(current, SITE / route_file(lang, slug)) + "#support"
    content = f'''<section class="page-hero"><div class="narrow"><p class="eyebrow">{esc(c["privacy_eyebrow"])}</p><h1>{esc(title)}</h1><p class="lede">{esc(p["privacy_intro"])}</p><p class="updated">{esc(p["privacy_updated"])}</p></div></section><section class="section policy-wrap"><div class="policy-summary"><div><strong>{esc(p["privacy_device"])}</strong><span>{esc(p["privacy_device_copy"])}</span></div><div><strong>{esc(p["privacy_account"])}</strong><span>{esc(p["privacy_account_copy"])}</span></div><div><strong>{esc(p["privacy_services"])}</strong><span>{esc(p["privacy_services_copy"])}</span></div></div><div class="policy-layout"><aside class="policy-nav"><strong>{esc(c["privacy"])}</strong>{"".join(f'<a href="#{key}">{esc(heading)}</a>' for key, heading, _ in policies)}<a href="{esc(support_href)}">{esc(p["support_nav"])}</a></aside><div>{body}<section class="policy-section" id="support"><h2>{esc(p["support_nav"])}</h2><p>{esc(p["privacy_contact"])}</p><a href="{esc(support_href)}">{esc(p["privacy_back"])}</a>{public_support_contact(lang)}</section></div></div></section>'''
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text(page_shell(current, lang, title, description, public_route(lang, slug, True), og, name, slug, True, content, apps=apps), encoding="utf-8")


def require_sips() -> str:
    sips = shutil.which("sips")
    if not sips:
        raise RuntimeError("Website/build.py requires macOS 'sips' for safe image conversion. Run this generator on macOS; the existing site/ artifact was not changed.")
    return sips


def validate_sources(source_root: Path = ROOT, require_all_media: bool = False) -> None:
    """Validate every input before creating a staging directory."""
    require_sips()
    required: list[Path] = []
    for brand in BRANDS:
        metadata = source_root / "AppStoreMetaData" / brand / "v1.0"
        for kind in ("app-name", "subtitle", "promotional-text", "app-description"):
            required.extend(metadata / kind / f"{lang}.txt" for lang in LANGS)
        required.extend(metadata / "screenshot-headlines" / f"{lang}.json" for lang in LANGS)
        required.append(app_icon_source(source_root, {"brand": brand, "family": "puzzle"}))
        required.extend(app_screenshot_source(source_root, {"brand": brand}, lang, filename) for lang in LANGS for filename in PUZZLE_SCREENSHOT_FILES)
    for brand in POCKET_BRANDS:
        metadata = source_root / "AppStoreMetaData" / brand / "v1.0"
        if not metadata.is_dir():
            continue
        for kind in ("app-name", "subtitle", "promotional-text", "app-description"):
            required.extend(metadata / kind / f"{lang}.txt" for lang in LANGS)
        if brand != "Reedwake":
            required.extend(metadata / "website-content" / f"{lang}.json" for lang in LANGS)
        headline_files = [metadata / "screenshot-headlines" / f"{lang}.json" for lang in LANGS]
        required.extend(headline_files)
        for lang, headline_path in zip(LANGS, headline_files):
            if headline_path.is_file():
                count = len(json.loads(read_text(headline_path))["screenshots"])
                if count != len(POCKET_SCREENSHOT_FILES):
                    raise ValueError(f"{headline_path} must contain {len(POCKET_SCREENSHOT_FILES)} screenshot headlines; found {count}.")
        required.extend([
            source_root / "ios" / "PocketColor" / "Packages" / "Reedwake" / "Sources" / "ReedwakeKit" / "Resources" / "Reedwake.xcstrings",
            source_root / "ios" / "PocketColor" / "Packages" / "PocketCommerce" / "Sources" / "PocketCommerce" / "Resources" / "PocketCommerce.xcstrings",
        ])
        for lang in LANGS:
            expected = {
                "marketing-url": public_route(lang, brand.lower()),
                "privacy-policy-url": public_route(lang, brand.lower(), True),
                "support-url": public_route(lang, brand.lower()),
            }
            for kind, url in expected.items():
                field = metadata / kind / f"{lang}.txt"
                required.append(field)
                if field.is_file() and read_text(field) != url:
                    raise ValueError(f"{field} must match the website route {url!r}.")
        required.append(app_icon_source(source_root, {"brand": brand, "family": "pocketcolor"}))
        if require_all_media or brand in APPROVED_POCKET_MEDIA:
            required.extend(app_screenshot_source(source_root, {"brand": brand}, lang, filename) for lang in LANGS for filename in POCKET_SCREENSHOT_FILES)
    missing = [path for path in required if not path.is_file() or path.stat().st_size == 0]
    if missing:
        sample = "\n".join(f"  - {path}" for path in missing[:12])
        suffix = "\n  ..." if len(missing) > 12 else ""
        raise FileNotFoundError(f"Website source validation failed before staging; missing or empty inputs ({len(missing)}):\n{sample}{suffix}")

    if require_all_media:
        held = set(POCKET_BRANDS) - APPROVED_POCKET_MEDIA
        if held:
            raise ValueError(f"Final all-game media approval remains held for {', '.join(sorted(held))}; file presence alone does not approve a revised gallery.")


def convert_image(source: Path, destination: Path, max_width: int | None = None, quality: int = 82) -> None:
    sips = require_sips()
    destination.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sips]
    if max_width:
        # -Z caps the largest dimension and would make portrait phones
        # only ~331px wide.  The web target is a readable 720px width.
        cmd += ["--resampleWidth", str(max_width)]
    cmd += ["--setProperty", "format", "jpeg", "--setProperty", "formatOptions", str(quality), str(source), "--out", str(destination)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def copy_assets(apps: dict[str, dict]) -> None:
    sips = require_sips()
    for slug, app in apps.items():
        source_icon = app_icon_source(ROOT, app)
        icon_destination = SITE / "assets" / "icons" / f"{slug}.png"
        icon_destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sips, "-Z", "512", str(source_icon), "--out", str(icon_destination)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for lang in LANGS:
            for filename in app["screenshot_files"]:
                source = app_screenshot_source(ROOT, app, lang, filename)
                convert_image(source, image_path(slug, lang, filename), 720, 84)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_video_sources(source_root: Path | None, ffmpeg: str | None, videos: dict[str, dict] | None = None) -> list[dict]:
    if videos is None:
        videos = approved_videos()
    if not videos:
        return []
    if source_root is None or not ffmpeg or not Path(ffmpeg).is_file():
        raise ValueError("Approved videos require --video-source-root and an existing --ffmpeg executable; site/ was not changed.")
    validated = []
    for brand, video in videos.items():
        source, report_path = source_root / video["movie"], source_root / video["report"]
        if not source.is_file() or not report_path.is_file():
            raise FileNotFoundError(f"{brand}: approved external movie/report is absent; site/ was not changed.")
        if file_sha256(source) != video["movieSHA256"] or file_sha256(report_path) != video["reportSHA256"]:
            raise ValueError(f"{brand}: approved movie/report hash changed; renewed lead acceptance is required.")
        report = json.loads(read_text(report_path))
        if not (report["outputSHA256"] == video["movieSHA256"] and report["language"] == "en" and report["duration"] == 24 and report["dimensions"] == [886, 1920] and report["completeDecodePassed"] and report["deviceCaptured"] is False and report["purchaseDisclosure"]):
            raise ValueError(f"{brand}: approved video provenance does not match the published format/source.")
        validated.append({"brand": brand, "source": source, "approval": video, "report": report})
    return validated


def make_video_derivatives(videos: list[dict], ffmpeg: str, output_root: Path) -> None:
    for video in videos:
        folder = output_root / video["brand"].lower()
        folder.mkdir(parents=True, exist_ok=True)
        movie, poster = folder / "gameplay-en.mp4", folder / "poster.jpg"
        # Remux only: preserve the accepted encoded video/audio streams, moving
        # MP4 metadata ahead of media for web playback. Do not reconstruct clips.
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(video["source"]), "-map", "0:v:0", "-map", "0:a:0", "-c", "copy", "-map_metadata", "-1", "-movflags", "+faststart", str(movie)], check=True)
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(movie), "-frames:v", "1", "-q:v", "3", str(poster)], check=True)
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(movie), "-f", "null", "-"], check=True)
        report = video["report"]
        provenance = {"schemaVersion": 1, "game": video["brand"], "language": "en", "durationSeconds": report["duration"], "dimensions": report["dimensions"], "sourceMovieSHA256": video["approval"]["movieSHA256"], "sourceReportSHA256": video["approval"]["reportSHA256"], "sourceKind": report["kind"], "deviceCaptured": False, "audio": report["audio"], "purchaseDisclosure": report["purchaseDisclosure"], "derivation": "stream-copy MP4 remux with faststart; first decoded frame JPEG poster", "movieSHA256": file_sha256(movie), "posterSHA256": file_sha256(poster), "completeDecodePassed": True}
        (folder / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")


def validate_owned_video(brand: str, video: dict) -> None:
    for field, filename in (("webMovie", "gameplay-en.mp4"), ("webPoster", "poster.jpg"), ("webProvenance", "provenance.json")):
        expected = Path("media") / brand.lower() / filename
        if video.get(field) != expected.as_posix():
            raise ValueError(f"{brand}: approved web media has not been imported; use the documented explicit import workflow.")
        source = WEBSITE / expected
        if not source.is_file() or file_sha256(source) != video[field + "SHA256"]:
            raise ValueError(f"{brand}: durable approved {field} is absent or changed; site/ was not changed.")
    provenance = json.loads(read_text(WEBSITE / video["webProvenance"]))
    if not (provenance["game"] == brand and provenance["language"] == "en" and provenance["sourceMovieSHA256"] == video["movieSHA256"] and provenance["sourceReportSHA256"] == video["reportSHA256"] and provenance["movieSHA256"] == video["webMovieSHA256"] and provenance["posterSHA256"] == video["webPosterSHA256"] and provenance["completeDecodePassed"]):
        raise ValueError(f"{brand}: web provenance does not match its accepted source.")


def validate_owned_videos() -> dict[str, dict]:
    """Ordinary builds require only the durable, lead-approved Website inputs."""
    videos = approved_videos()
    for brand, video in videos.items():
        validate_owned_video(brand, video)
    return videos


def import_approved_videos(source_root: Path | None, ffmpeg: str | None) -> None:
    """Import approved web derivatives once; original delivery/proofs stay external."""
    manifest = json.loads(read_text(WEBSITE / "approved-videos.json"))
    pending, retained = {}, {}
    for brand, video in approved_videos().items():
        try:
            validate_owned_video(brand, video)
            retained[brand] = video
        except (ValueError, KeyError, FileNotFoundError):
            pending[brand] = video
    if not pending:
        return
    videos = validate_video_sources(source_root, ffmpeg, pending)
    staging = Path(tempfile.mkdtemp(prefix=".media-import-", dir=WEBSITE))
    destination = WEBSITE / "media"
    backup = WEBSITE / f".media-backup-{uuid.uuid4().hex}"
    try:
        copy_video_assets(retained, staging)
        make_video_derivatives(videos, ffmpeg, staging)
        for brand, video in manifest["videos"].items():
            for field, filename in (("webMovie", "gameplay-en.mp4"), ("webPoster", "poster.jpg"), ("webProvenance", "provenance.json")):
                video[field] = (Path("media") / brand.lower() / filename).as_posix()
                video[field + "SHA256"] = file_sha256(staging / brand.lower() / filename)
        staged_manifest = WEBSITE / f".approved-videos-{uuid.uuid4().hex}.json"
        staged_manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if destination.exists():
            os.replace(destination, backup)
        try:
            os.replace(staging, destination)
            os.replace(staged_manifest, WEBSITE / "approved-videos.json")
        except BaseException:
            shutil.rmtree(destination, ignore_errors=True)
            if backup.exists():
                os.replace(backup, destination)
            raise
        shutil.rmtree(backup, ignore_errors=True)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        if "staged_manifest" in locals():
            staged_manifest.unlink(missing_ok=True)


def copy_video_assets(videos: dict[str, dict], output_root: Path | None = None) -> None:
    output_root = output_root if output_root is not None else SITE / "assets" / "videos"
    for brand, video in videos.items():
        folder = output_root / brand.lower()
        folder.mkdir(parents=True, exist_ok=True)
        for key in ("webMovie", "webPoster", "webProvenance"):
            source = WEBSITE / video[key]
            shutil.copyfile(source, folder / source.name)


def write_static_files(apps: dict[str, dict]) -> None:
    (SITE / "app-ads.txt").write_text("google.com, pub-8504168355168096, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")
    routes = [public_route(lang) for lang in LANGS]
    routes += [public_route(lang, slug) for lang in LANGS for slug in apps]
    routes += [public_route(lang, slug, True) for lang in LANGS for slug in apps]
    entries = "\n".join(f"  <url><loc>{esc(route)}</loc></url>" for route in routes)
    (SITE / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n', encoding="utf-8")
    (SITE / "404.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found · Puzzle worlds</title><meta name="robots" content="noindex"><link rel="stylesheet" href="{BASE}styles.css"></head><body class="error-page"><main><p class="eyebrow">404</p><h1>This puzzle piece is missing.</h1><p>The page you requested does not exist.</p><a class="button button-primary" href="{BASE}">Return to the puzzle worlds</a></main></body></html>''', encoding="utf-8")


def main() -> None:
    global SITE
    deploy_site = SITE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-all-media", action="store_true", help="Validate every game’s complete screenshot matrix before building; approval still controls public galleries.")
    parser.add_argument("--import-approved-videos", action="store_true", help="Explicitly import hash-pinned external deliveries into durable Website-owned web media; does not publish or build pages.")
    parser.add_argument("--video-source-root", type=Path, help="External directory containing the hash-pinned approved movie/report paths.")
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"), help="Existing FFmpeg executable for stream-copy web derivatives and posters.")
    args = parser.parse_args()
    if args.import_approved_videos:
        import_approved_videos(args.video_source_root, args.ffmpeg)
        print("Imported approved durable Website video sources; site/ was not changed.")
        return
    validate_sources(require_all_media=args.require_all_media)
    videos = validate_owned_videos()
    apps = {**load_apps(), **load_pocket_games()}
    if not deploy_site.is_dir():
        raise RuntimeError(f"Expected existing deployment directory at {deploy_site}; refusing to replace an unexpected path.")

    staging = Path(tempfile.mkdtemp(prefix=".site-staging-", dir=WEBSITE))
    SITE = staging
    try:
        copy_assets(apps)
        copy_video_assets(videos)
        (SITE / "styles.css").write_text(STYLES, encoding="utf-8")
        (SITE / "script.js").write_text(SCRIPT, encoding="utf-8")
        for lang in LANGS:
            build_hub(lang, apps)
            for slug, app in apps.items():
                if app["family"] == "pocketcolor":
                    build_pocket_app(lang, slug, app, apps)
                    build_pocket_privacy(lang, slug, app, apps)
                else:
                    build_app(lang, slug, app, apps)
                    build_privacy(lang, slug, app, apps)
        write_static_files(apps)
        generated_pages = len(list(SITE.rglob("*.html")))
        generated_assets = len(list((SITE / "assets").rglob("*")))
    except BaseException:
        SITE = deploy_site
        shutil.rmtree(staging, ignore_errors=True)
        raise

    SITE = deploy_site
    backup = WEBSITE / f".site-backup-{uuid.uuid4().hex}"
    try:
        # The existing artifact is moved aside only after the complete staging
        # build succeeds.  If the second rename fails, restore the old artifact.
        os.replace(deploy_site, backup)
        try:
            os.replace(staging, deploy_site)
        except BaseException:
            os.replace(backup, deploy_site)
            raise
        shutil.rmtree(backup, ignore_errors=True)
    except BaseException:
        if backup.exists() and not deploy_site.exists():
            os.replace(backup, deploy_site)
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise
    print(f"Built {generated_pages} HTML pages and {generated_assets} assets in {deploy_site}")


STYLES = r'''
:root { --ink:#101a34; --ink-soft:#2c3b60; --muted:#65738b; --paper:#fff; --cream:#fbfcff; --line:#dfe6f1; --accent:#b4de8d; --companion:#61e4c5; --wash:#f1f9e8; --brand-ink:#28413a; --radius:26px; --shadow:0 24px 70px rgba(16,26,52,.14); font-family:ui-rounded,"SF Pro Rounded",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:var(--ink); background:var(--cream); line-height:1.6; font-synthesis:none; }
*{box-sizing:border-box} html{scroll-behavior:smooth;scroll-padding-top:90px} body{margin:0;overflow-x:hidden;background:var(--cream)} img{display:block;max-width:100%} a{color:inherit} h1,h2,h3{margin-top:0;line-height:1.08;letter-spacing:-.045em} h1{font-size:clamp(3rem,7vw,6.6rem);margin-bottom:1.1rem} h2{font-size:clamp(2.2rem,4.5vw,4.2rem);margin-bottom:1rem} h3{font-size:1.35rem;margin-bottom:.55rem} p{margin-top:0}.skip-link{position:fixed;z-index:99;top:-5rem;left:1rem;padding:.7rem 1rem;border-radius:999px;background:var(--accent);font-weight:850}.skip-link:focus{top:1rem}.site-header{position:sticky;z-index:20;top:0;background:rgba(16,26,52,.95);color:#fff;border-bottom:1px solid rgba(255,255,255,.1);backdrop-filter:blur(18px)}.nav{width:min(100%,1180px);min-height:78px;margin:auto;padding:0 1.25rem;display:flex;align-items:center;justify-content:space-between;gap:1rem}.brand{display:inline-flex;align-items:center;gap:.7rem;color:inherit;text-decoration:none;font-weight:900;letter-spacing:-.025em}.brand-mark{display:grid;width:42px;height:42px;place-items:center;overflow:hidden;border-radius:14px;background:linear-gradient(135deg,var(--accent),var(--companion));color:var(--brand-ink);box-shadow:0 8px 22px rgba(0,0,0,.2)}.brand-mark img{width:100%;height:100%;object-fit:cover}.brand-glyph{font-size:1.45rem}.nav-links{display:flex;align-items:center;gap:1.2rem;font-size:.9rem;font-weight:800}.nav-links>a,.nav-menu-panel>a{color:#dbe4ff;text-decoration:none}.nav-links>a:hover,.nav-menu-panel>a:hover{color:var(--accent)}.language,.nav-menu{position:relative}.language summary,.nav-menu summary{cursor:pointer;list-style:none;padding:.45rem .7rem;border:1px solid rgba(255,255,255,.26);border-radius:999px;font-size:.78rem;font-weight:900}.language summary::-webkit-details-marker,.nav-menu summary::-webkit-details-marker{display:none}.language-panel,.nav-menu-panel{position:absolute;right:0;top:calc(100% + .7rem);display:grid;min-width:170px;padding:.55rem;border:1px solid rgba(255,255,255,.13);border-radius:18px;background:var(--ink);box-shadow:var(--shadow)}.language-panel a,.mobile-languages a{padding:.55rem .75rem;border-radius:10px;color:#fff;text-decoration:none;font-size:.86rem}.language-panel a:hover,.language-panel a[aria-current=true],.mobile-languages a:hover,.mobile-languages a[aria-current=true]{background:rgba(255,255,255,.1);color:var(--accent)}.nav-menu{display:none}.nav-menu-panel{right:0;min-width:220px;gap:.25rem}.mobile-languages{display:grid;grid-template-columns:repeat(2,1fr);gap:.2rem;margin-top:.5rem;padding-top:.6rem;border-top:1px solid rgba(255,255,255,.13)}.mobile-languages span{grid-column:1/-1;padding:.25rem .75rem;color:#aebbdc;font-size:.7rem;font-weight:900;letter-spacing:.09em;text-transform:uppercase}.hub-hero,.app-hero,.page-hero{position:relative;overflow:hidden;background:var(--ink);color:#fff}.hub-hero:before,.app-hero:before,.page-hero:before{position:absolute;content:"";width:530px;height:530px;border-radius:50%;background:color-mix(in srgb,var(--accent) 18%,transparent);top:-280px;left:-160px}.hub-hero:after,.app-hero:after,.page-hero:after{position:absolute;content:"";width:640px;height:640px;border:1px solid rgba(255,255,255,.1);border-radius:50%;right:-230px;bottom:-350px}.hero-grid,.app-hero-grid,.page-hero>.narrow{width:min(100%,1180px);margin:auto;padding:6.6rem 1.25rem 6rem;position:relative;z-index:1}.hero-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(350px,.9fr);align-items:center;gap:4rem;min-height:650px}.eyebrow{display:flex;align-items:center;gap:.6rem;margin:0 0 1.1rem;color:var(--accent);font-size:.76rem;font-weight:950;letter-spacing:.12em;text-transform:uppercase}.eyebrow:before{width:28px;height:4px;border-radius:99px;background:currentColor;content:""}.lede{max-width:690px;color:#c9d3ed;font-size:clamp(1.06rem,1.8vw,1.23rem);line-height:1.75}.button{display:inline-flex;align-items:center;justify-content:center;min-height:49px;padding:.75rem 1.15rem;border:1px solid transparent;border-radius:999px;font-weight:900;text-decoration:none;transition:transform .2s ease,box-shadow .2s ease}.button:hover{transform:translateY(-2px)}.button-primary{background:var(--accent);color:var(--brand-ink);box-shadow:0 12px 30px color-mix(in srgb,var(--accent) 25%,transparent)}.hub-hero .button{margin-top:1.1rem}.orbit-art{position:relative;min-height:450px}.orbit{position:absolute;inset:6% 4% 2% 5%;border:1px dashed rgba(255,255,255,.3);border-radius:48%;transform:rotate(-12deg)}.orbit-b{inset:18% 0 12% 20%;transform:rotate(32deg);border-color:color-mix(in srgb,var(--accent) 65%,transparent)}.float-shape{position:absolute;display:grid;place-items:center;border:6px solid white;box-shadow:0 20px 55px rgba(0,0,0,.25);font-size:2.1rem;font-weight:950}.shape-a{top:8%;left:17%;width:115px;height:115px;border-radius:35px;background:var(--accent);color:var(--brand-ink);transform:rotate(-12deg)}.shape-b{top:35%;right:11%;width:135px;height:85px;border-radius:45px;background:var(--companion);color:var(--brand-ink);transform:rotate(9deg)}.shape-c{bottom:8%;left:18%;width:105px;height:105px;border-radius:50%;background:#ff8aa5;color:#563447;transform:rotate(16deg)}.shape-d{bottom:16%;right:20%;width:72px;height:72px;border-radius:24px;background:#ffc178;color:#5a4129;font-size:1.6rem}.section{width:min(100%,1180px);margin:auto;padding:6.2rem 1.25rem}.section-heading{display:grid;grid-template-columns:minmax(0,1fr) minmax(280px,.65fr);align-items:end;gap:3rem;margin-bottom:2.4rem}.section-heading>p{margin:0;color:var(--muted)}.game-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.game-card{overflow:hidden;border:1px solid var(--line);border-radius:var(--radius);background:var(--wash);box-shadow:0 10px 30px rgba(16,26,52,.06);transition:transform .3s ease,box-shadow .3s ease}.game-card:hover{transform:translateY(-5px);box-shadow:var(--shadow)}.game-card-link{display:flex;align-items:center;gap:1rem;padding:1.15rem;color:var(--brand-ink);text-decoration:none}.game-card-link img{width:82px;height:82px;flex:0 0 auto;border-radius:22px;box-shadow:0 9px 22px rgba(16,26,52,.16)}.game-card-copy{display:grid;gap:.18rem}.game-card-copy strong{font-size:1.18rem}.game-card-copy span{color:var(--muted);font-size:.9rem}.game-card-copy em{margin-top:.55rem;color:var(--brand-ink);font-size:.78rem;font-style:normal;font-weight:900}.soft-section{width:100%;max-width:none;padding-right:max(1.25rem,calc((100vw - 1155px)/2));padding-left:max(1.25rem,calc((100vw - 1155px)/2));background:#eef3fa}.value-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.value-grid article{padding:1.7rem;border:1px solid var(--line);border-radius:var(--radius);background:#fff}.value-grid strong{display:block;margin-bottom:.75rem;color:var(--brand-ink);font-size:2.9rem;line-height:1}.value-grid p{margin:0;color:var(--muted)}.privacy-links{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem}.privacy-links a{padding:1rem 1.1rem;border:1px solid var(--line);border-radius:16px;background:#fff;text-decoration:none;font-weight:800}.privacy-links a:hover{border-color:var(--accent);background:var(--wash)}.compact-section{padding-top:4rem;padding-bottom:5rem}.app-hero-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(330px,.8fr);align-items:center;gap:4rem;min-height:680px}.app-title{display:flex;align-items:center;gap:1.25rem}.app-title img{width:88px;height:88px;border-radius:25px;box-shadow:0 16px 30px rgba(0,0,0,.25)}.app-title h1{font-size:clamp(2.7rem,5.8vw,5.7rem);margin:0}.coming{display:inline-flex;align-items:center;gap:.65rem;margin-top:1.25rem;color:#e1e8ff;font-weight:800}.coming span{color:var(--accent);font-size:.75rem}.hero-shot-wrap{position:relative;min-height:540px}.hero-ring{position:absolute;inset:8% 7% 6% 7%;border:1px dashed rgba(255,255,255,.28);border-radius:48%;transform:rotate(-12deg)}.hero-shot{position:absolute;z-index:1;top:3%;right:15%;width:min(55%,290px);overflow:hidden;border:9px solid #080e22;border-radius:37px;background:#080e22;box-shadow:0 30px 80px rgba(0,0,0,.35);transform:rotate(5deg);animation:float-main 6s ease-in-out infinite}.hero-shot img{width:100%;height:auto}.split{display:grid;grid-template-columns:minmax(0,.95fr) minmax(0,1fr);align-items:start;gap:4rem}.body-copy{max-width:630px;color:var(--muted);font-size:1.05rem}.feature-panel{padding:2rem;border-radius:var(--radius);background:var(--wash);border:1px solid color-mix(in srgb,var(--accent) 42%,var(--line));color:var(--brand-ink)}.feature-panel h3{font-size:1.8rem}.checklist{display:grid;gap:.7rem;padding:0;margin:1.3rem 0 0;list-style:none}.checklist li{display:flex;gap:.7rem;color:var(--muted)}.checklist li:before{display:grid;flex:0 0 auto;width:24px;height:24px;place-items:center;border-radius:50%;background:var(--accent);color:var(--brand-ink);content:"✓";font-weight:950}.shots-section{width:100%;max-width:none;padding-right:max(1.25rem,calc((100vw - 1155px)/2));padding-left:max(1.25rem,calc((100vw - 1155px)/2));background:#f3f6fb}.shots-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}.shot-card{min-width:0;margin:0}.shot-frame{overflow:hidden;border:8px solid #0b1431;border-radius:29px;background:#0b1431;box-shadow:var(--shadow);transition:transform .3s ease}.shot-card:nth-child(even){padding-top:2.3rem}.shot-card:hover .shot-frame{transform:translateY(-6px)}.shot-frame img{width:100%;height:auto}.shot-card figcaption{padding:1rem .2rem 0}.shot-card figcaption span{display:block;margin-bottom:.35rem;color:var(--accent);font-weight:950;font-size:.75rem;letter-spacing:.08em}.shot-card figcaption strong{font-size:1.05rem}.pro-panel{display:grid;grid-template-columns:minmax(0,1fr) minmax(230px,.5fr);gap:2rem;align-items:center;padding:clamp(2rem,5vw,4rem);border-radius:36px;background:var(--ink);color:#fff;box-shadow:var(--shadow)}.pro-panel h2{margin-bottom:.7rem}.pro-panel p{color:#c9d3ed}.pro-card{padding:1.5rem;border:1px solid color-mix(in srgb,var(--accent) 35%,transparent);border-radius:22px;background:color-mix(in srgb,var(--accent) 13%,transparent)}.pro-card span{display:inline-flex;padding:.3rem .6rem;border-radius:999px;background:var(--accent);color:var(--brand-ink);font-size:.7rem;font-weight:950;letter-spacing:.1em}.pro-card p{margin:1rem 0 0}.other-grid .game-card-link{padding:1rem}.page-hero>.narrow{max-width:1180px}.page-hero h1{font-size:clamp(3rem,6vw,5.8rem);max-width:840px}.updated{margin:1.4rem 0 0;color:#bbc8e7;font-size:.9rem}.policy-wrap{padding-top:4.5rem}.policy-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin-bottom:2.8rem}.policy-summary div{padding:1.15rem;border-radius:18px;background:var(--wash)}.policy-summary strong{display:block;color:var(--brand-ink)}.policy-summary span{color:var(--muted);font-size:.86rem}.policy-layout{display:grid;grid-template-columns:220px minmax(0,760px);gap:4rem;align-items:start}.policy-nav{position:sticky;top:105px;padding:1rem;border:1px solid var(--line);border-radius:18px;background:#fff}.policy-nav strong{display:block;margin-bottom:.5rem}.policy-nav a{display:block;padding:.4rem 0;color:var(--muted);font-size:.88rem;text-decoration:none}.policy-nav a:hover{color:var(--brand-ink)}.policy-section{padding:2rem 0;border-top:1px solid var(--line)}.policy-section h2{font-size:clamp(1.65rem,3vw,2.35rem)}.policy-section p{color:var(--muted)}.policy-section a{color:var(--brand-ink);font-weight:800}.site-footer{padding:4rem 1.25rem 2rem;background:#09122c;color:#fff}.footer-inner{display:grid;grid-template-columns:1fr auto;gap:3rem;width:min(100%,1180px);margin:auto}.footer-inner p{max-width:480px;margin:.8rem 0 0;color:#aebbdc}.footer-inner nav{display:grid;gap:.55rem}.footer-inner nav a{color:#dbe4ff;text-decoration:none}.footer-inner nav a:hover{color:var(--accent)}.footer-bottom{width:min(100%,1180px);margin:2.4rem auto 0;padding-top:1.3rem;border-top:1px solid rgba(255,255,255,.12);color:#8291b7;font-size:.82rem}.error-page{min-height:100vh;display:grid;place-items:center;padding:2rem;background:var(--ink);color:#fff}.error-page main{max-width:680px}.error-page h1{font-size:clamp(3rem,7vw,6rem)}.error-page p:not(.eyebrow){color:#c9d3ed;font-size:1.15rem}.reveal{opacity:0;transform:translateY(22px);transition:opacity .65s ease,transform .65s cubic-bezier(.22,1,.36,1)}.reveal.is-visible{opacity:1;transform:none}a:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:4px}
@keyframes float-main{0%,100%{transform:rotate(5deg) translateY(0)}50%{transform:rotate(5deg) translateY(-13px)}}
@media(max-width:850px){.nav-links{display:none}.nav-menu{display:block}.hero-grid,.app-hero-grid{grid-template-columns:1fr;gap:2rem;min-height:0}.hero-grid,.app-hero-grid{padding-top:5rem;padding-bottom:4rem}.orbit-art,.hero-shot-wrap{min-height:390px}.hero-shot{right:20%;width:min(52%,255px)}.section-heading,.split{grid-template-columns:1fr;gap:1rem}.game-grid{grid-template-columns:repeat(2,1fr)}.shots-grid{grid-template-columns:repeat(2,1fr)}.shot-card:nth-child(even){padding-top:1rem}.policy-layout{grid-template-columns:1fr;gap:1.5rem}.policy-nav{position:static}.privacy-links{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){h1{font-size:clamp(2.7rem,13vw,4.3rem)}h2{font-size:clamp(2rem,10vw,3rem)}.nav{min-height:70px}.hero-grid,.app-hero-grid{padding-top:4.2rem}.game-grid,.value-grid,.privacy-links,.shots-grid,.policy-summary{grid-template-columns:1fr}.orbit-art{min-height:325px}.shape-a{width:90px;height:90px;left:12%}.shape-b{width:110px;height:70px;right:5%}.shape-c{width:83px;height:83px;left:15%}.shape-d{right:15%;width:60px;height:60px}.app-title{align-items:flex-start;gap:.8rem}.app-title img{width:66px;height:66px;border-radius:19px}.app-title h1{font-size:clamp(2.35rem,10vw,3.6rem)}.hero-shot-wrap{min-height:340px}.hero-shot{right:19%;width:min(59%,230px)}.pro-panel{grid-template-columns:1fr}.footer-inner{grid-template-columns:1fr;gap:1.5rem}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.hero-shot,.float-shape,.game-card,.shot-frame,.button{animation:none!important;transition:none!important}.reveal{opacity:1;transform:none;transition:none}.game-card:hover,.shot-card:hover .shot-frame,.button:hover{transform:none}}
.support-contact{margin-top:2rem;padding:1.5rem;border:1px solid var(--line);border-radius:18px;max-width:900px}.support-contact p{margin:.8rem 0}.support-contact .button{margin:.5rem 0}.gameplay-video{display:block;width:min(100%,420px);height:auto;margin:2rem auto 0;border-radius:24px;background:#10172c;box-shadow:0 20px 50px rgba(15,23,42,.14)}.gameplay-video:focus-visible{outline:3px solid var(--accent);outline-offset:5px}.app-hero-grid.copy-only{grid-template-columns:minmax(0,900px);min-height:0}.pocket-stats{grid-template-columns:repeat(4,1fr)}.store-copy{display:grid;gap:.65rem;max-width:850px}.store-copy p{margin:0;color:var(--muted);font-size:1.05rem}.support-list{display:grid;gap:.75rem;max-width:900px}.support-answer{padding:1.15rem 1.35rem;border:1px solid var(--line);border-radius:18px;background:#fff}.support-answer summary{cursor:pointer;color:var(--brand-ink);font-weight:850}.support-answer>div{padding-top:.85rem;color:var(--muted)}.support-answer p{margin:.7rem 0 0}.support-answer p:first-child{margin-top:0}
@media(max-width:850px){.pocket-stats{grid-template-columns:repeat(2,1fr)}}
'''


SCRIPT = r'''
(() => {
  document.querySelectorAll('.nav-menu-panel a').forEach((link) => link.addEventListener('click', () => link.closest('details')?.removeAttribute('open')));
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const targets = document.querySelectorAll('.section-heading, .game-card, .value-grid article, .shot-card, .feature-panel, .pro-panel, .policy-section');
  if (!reduce && 'IntersectionObserver' in window) {
    targets.forEach((element) => element.classList.add('reveal'));
    const observer = new IntersectionObserver((entries, instance) => {
      entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add('is-visible'); instance.unobserve(entry.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    targets.forEach((element) => observer.observe(element));
  }
})();
'''


if __name__ == "__main__":
    main()
