#!/usr/bin/env python3
"""Builds the static Garnet Events site.

Run from the repo root:  python3 tools/build.py
Writes index.html, about.html, services.html, gallery.html, contact.html,
404.html, sitemap.xml and robots.txt. Shared header/footer live here so the
pages never drift apart. CSS/JS URLs carry a content hash (?v=...) so a new
deploy is never hidden behind a cached stylesheet.
"""
import hashlib
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://garnetevents.in"

PHONE_DISPLAY = "+91 76868 63556"
PHONE_TEL = "+917686863556"
WA_NUMBER = "918777868614"
WA_DISPLAY = "+91 87778 68614"
EMAIL = "garneteventspromotion@gmail.com"
CITIES = ["Kolkata", "Guwahati", "Jaipur", "Bikaner", "Jamshedpur", "Hyderabad", "Siliguri", "Dubai"]

NAV = [
    ("index.html", "Home"),
    ("about.html", "About"),
    ("services.html", "Services"),
    ("gallery.html", "Gallery"),
    ("contact.html", "Contact"),
]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

# width x height of the largest WebP for each image (the smaller one is always 800w)
IMAGES = {
    "gallery-01": (1400, 1810), "gallery-02": (1400, 1810), "gallery-03": (1400, 1810),
    "gallery-04": (1400, 1810), "gallery-05": (1400, 1810), "gallery-06": (1400, 1810),
    "gallery-07": (1400, 1810), "gallery-08": (1400, 1810),
    "service-social": (1400, 1048), "service-destination": (1400, 1048),
    "founder-amit": (987, 1200),
}


def asset_version(rel):
    return hashlib.sha1((ROOT / rel).read_bytes()).hexdigest()[:10]


CSS_V = asset_version("assets/css/site.css")
JS_V = asset_version("assets/js/site.js")

ARROW = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" stroke="currentColor" stroke-width="1.2"/></svg>'
WA_ICON = ('<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16 3C9 3 3.5 8.5 3.5 15.5c0 2.4.7 4.7 1.9 6.7L3 29l7-1.8c1.9 1 4 1.6 6 1.6 7 0 12.5-5.5 12.5-12.5S23 3 16 3zm0 22.8c-1.8 0-3.6-.5-5.1-1.4l-.4-.2-4.2 1.1 1.1-4.1-.2-.4c-1-1.6-1.5-3.4-1.5-5.3C5.5 9.6 10.2 5 16 5s10.5 4.7 10.5 10.5S21.8 25.8 16 25.8zm5.8-7.9c-.3-.2-1.9-.9-2.1-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.2-1.3-.5-2.5-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-1-2.3c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.1 3.3 5.2 4.6.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.9-.8 2.1-1.5.3-.8.3-1.4.2-1.5-.1-.2-.3-.2-.6-.4z"/></svg>')
PAUSE = '<svg class="icon-pause" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2h3v12H4zM9 2h3v12H9z" fill="currentColor"/></svg>'
PLAY = '<svg class="icon-play" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2l10 6-10 6z" fill="currentColor"/></svg>'


def img(name, alt, sizes, eager=False, cls="", parallax=False):
    w, h = IMAGES[name]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    p = " data-parallax" if parallax else ""
    return (f'<img{c} src="assets/img/{name}-800.webp" '
            f'srcset="assets/img/{name}-800.webp 800w, assets/img/{name}-{w}.webp {w}w" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{escape(alt)}" {load} decoding="async"{p}>')


def poster(page, alt, sizes, parallax=False):
    """A hero video's still frame, reused as a landscape photograph."""
    p = " data-parallax" if parallax else ""
    return (f'<img src="assets/img/hero-{page}-poster-960.webp" '
            f'srcset="assets/img/hero-{page}-poster-960.webp 960w, assets/img/hero-{page}-poster-1920.webp 1920w" '
            f'sizes="{sizes}" width="1920" height="1080" alt="{escape(alt)}" loading="lazy" decoding="async"{p}>')


def hero_video(page):
    return f'''<div class="hero__media">
    <video muted loop playsinline preload="none" aria-hidden="true"
      poster="assets/img/hero-{page}-poster-960.webp"
      data-poster-lg="assets/img/hero-{page}-poster-1920.webp"
      data-src-sm="assets/videos/hero-{page}-sm.mp4"
      data-src-lg="assets/videos/hero-{page}.mp4"></video>
  </div>
  <div class="hero__frame" aria-hidden="true"></div>
  <button class="media-toggle" type="button" aria-pressed="false" aria-label="Pause background video">{PAUSE}{PLAY}</button>'''


def inner_hero(page, eyebrow, caps, script, lead):
    return f'''<section class="hero hero--inner" aria-labelledby="page-title">
  {hero_video(page)}
  <div class="wrap hero__content">
    <div class="hero__row">
      <div>
        <p class="eyebrow fade" style="margin-bottom:18px">[ {eyebrow} ]</p>
        <h1 id="page-title" class="hero__title"><span class="rise"><span>{caps}<span class="script">{script}</span></span></span></h1>
      </div>
      <p class="hero__lead fade" style="--d:2">{lead}</p>
    </div>
  </div>
</section>'''


SERVICES = [
    ("योजना", "Event planning", "from concept to execution", "gallery-04", "Place setting with gold charger and garnet napkin",
     "One plan, one budget and one timeline that everyone works from."),
    ("रचना", "Event design", "built around your vision", "gallery-03", "Velvet-draped wedding mandap with gold columns and floral urns",
     "Theme, colour, layout and mood, designed as one look."),
    ("स्थल", "Venue selection", "the right room, the right city", "gallery-01", "Ballroom wedding reception with tall floral centrepieces",
     "We shortlist, visit and negotiate, so you only see the good ones."),
    ("समन्वय", "Vendor coordination", "one team, every vendor", "gallery-07", "Tiered garnet cake on a styled dessert table",
     "Caterers, florists, decorators and artists, briefed and held to the plan."),
    ("सज्जा", "Décor & styling", "the atmosphere", "gallery-02", "Garnet rose beside gold filigree candle holders",
     "Flowers, fabric, light and tablescapes that look as good in person as in photographs."),
    ("संचालन", "On-site management", "so the day runs to plan", "gallery-06", "Outdoor marquee dinner lit by lanterns and string lights",
     "Our team runs the floor, the timings and the surprises."),
    ("व्यवस्था", "Logistics", "the unglamorous part, done well", "service-destination", "Marquee reception at sunset with chandeliers and draped velvet",
     "Guest movement, transport, schedules and contingencies."),
    ("ध्वनि · प्रकाश", "Sound & light", "audio-visual production", "gallery-05", "Corporate gala stage with a red backdrop and gold-lit runway",
     "Stage, sound, lighting and screens for performances and presentations."),
    ("मनोरंजन", "Entertainment", "artists and performers", "gallery-08", "Guests dancing under falling gold confetti",
     "Singers, DJs, dancers and anchors, booked and cued."),
]
CARD_TONES = ["sage", "garnet", "sage", "black"]


def services_rail(title_id="svc-title"):
    cards = "\n".join(
        f'''      <article class="rail__item svc-card svc-card--{CARD_TONES[i % 4]}">
        <p class="svc-card__hi" lang="hi">{hi}</p>
        <h3 class="svc-card__title"><span class="svc-card__num">{ROMAN[i]}</span>{t}</h3>
        <p class="svc-card__sub">({sub})</p>
        <div class="svc-card__img">{img(im, alt, "300px")}</div>
        <p class="tiny">{d}</p>
      </article>''' for i, (hi, t, sub, im, alt, d) in enumerate(SERVICES))
    return f'''<section class="sec" aria-labelledby="{title_id}">
  <div class="wrap">
    <div class="sec-bar">
      <h2 id="{title_id}" class="eyebrow">Under one roof</h2>
      <p class="eyebrow sec-bar__mid">Nine services</p>
      <a class="eyebrow" href="services.html" style="text-decoration:none">● See services</a>
    </div>
    <div class="rail" data-rail>
      <div class="rail__track" tabindex="0" role="region" aria-label="Our nine services, scroll sideways">
{cards}
      </div>
      <div class="rail__nav">
        <button class="rail__btn" type="button" data-rail-prev>Previous</button>
        <div class="rail__progress" aria-hidden="true"><span></span></div>
        <button class="rail__btn" type="button" data-rail-next>Next</button>
      </div>
    </div>
    <div class="rail-foot">
      <p class="tiny muted">The foundation of everything we do</p>
      <p class="tiny">When two hundred people gather for one day, nothing can be left to chance. Take the whole list, or only the parts you need help with.</p>
    </div>
  </div>
</section>'''


def credits():
    logos = [
        ("credit-danceplus", "Dance+", 425),
        ("credit-tatasteel", "Tata Steel Kolkata 25K", 440),
        ("credit-kidsfashion", "India Kids Fashion Week", 240),
        ("credit-dancedeewane", "Dance Deewane", 426),
    ]
    imgs = "\n        ".join(
        f'<li><img src="assets/img/{n}.webp" alt="{escape(a)}" width="{w}" height="240" loading="lazy" decoding="async"></li>'
        for n, a, w in logos)
    return f'''<section class="sec sec--tight sec--rule" aria-labelledby="credits-title">
  <div class="wrap credits" data-reveal>
    <p class="eyebrow muted">[ Before Garnet ]</p>
    <h2 id="credits-title" class="caps-s" style="max-width:44ch">Our founder learned the craft on large productions, including</h2>
    <ul class="credits__logos">
        {imgs}
    </ul>
  </div>
</section>'''


QUOTES = [
    ("Hamara experience Garnet Events ke saath bahut hi accha raha. Unki hard work aur commitment ne hamari shaadi ko unforgettable bana diya. Highly recommended!", "Aniket Goyel"),
    ("From start to finish, Team Garnet exceeded our expectations. Their professionalism and creativity made our special day absolutely magical. Thank you!", "Namrata Garg"),
    ("Aplog ki dedication aur creativity ne hamari betiya ki wedding ko ekdum magical bana diya. Amit you are fantastic, aur humari expectations ko exceed kar diya!", "Lokesh Agarwal"),
    ("Thank you so much Team for the amazing events you guys did. Everyone told that the decor was amazing in all the events. You did everything from your heart and selflessly. … Special thanks to Amit Bhaiya, you are amazing!", "Roshni Jain"),
]


def quotes():
    items = "\n".join(
        f'''        <figure class="quote{' is-active' if i == 0 else ''}"><blockquote><p>“{escape(q)}”</p></blockquote><figcaption>{escape(n)}</figcaption></figure>'''
        for i, (q, n) in enumerate(QUOTES))
    return f'''<section class="sec sec--black texture" aria-labelledby="quotes-title">
  <div class="wrap quotes" data-quotes>
    <h2 id="quotes-title" class="script-head" data-reveal>Kind words</h2>
    <div class="quotes__stage" aria-live="polite">
{items}
    </div>
    <div class="quotes__nav">
      <button class="rail__btn" type="button" data-q-prev>Previous</button>
      <span class="quotes__count" data-q-count>01 / {len(QUOTES):02d}</span>
      <button class="rail__btn" type="button" data-q-next>Next</button>
    </div>
  </div>
</section>'''


def cities_block():
    items = "".join(f"<li>{c}</li>" for c in CITIES)
    return f'''<section class="sec sec--tight" aria-labelledby="cities-title">
  <div class="wrap center" data-reveal>
    <p id="cities-title" class="eyebrow muted" style="margin-bottom:28px">[ Where we've worked ]</p>
    <ul class="cities">{items}</ul>
  </div>
</section>'''


def cta():
    return f'''<section class="cta" aria-labelledby="cta-title">
  <div class="cta__bg" aria-hidden="true">{poster("contact", "", "100vw", parallax=True)}</div>
  <div class="wrap">
    <p class="eyebrow" data-reveal>[ Enquiries ]</p>
    <h2 id="cta-title" class="cta__title" data-reveal style="--d:1">
      <span class="sans">Planning something?</span>
      <span class="serif">Let's make it the one everyone remembers.</span>
    </h2>
    <a class="btn btn--light" href="contact.html" data-reveal style="--d:2">Enquire now</a>
    <p class="cta__links" data-reveal style="--d:3">
      <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
      <a href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener">WhatsApp {WA_DISPLAY}</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
    </p>
  </div>
</section>'''


def page(slug, title, description, body, preload_poster=None, jsonld=None, noindex=False):
    current = f"{slug}.html"
    canonical = f"{SITE}/" if slug == "index" else f"{SITE}/{slug}.html"
    aria = ' aria-current="page"'
    nav_items = "\n".join(
        f'          <li><a href="{href}"{aria if href == current else ""}><span>{i:02d}</span>{label}</a></li>'
        for i, (href, label) in enumerate(NAV, 1))
    mobile_items = "\n".join(
        f'      <a href="{href}"{aria if href == current else ""}><span>{ROMAN[i]}</span>{label}</a>'
        for i, (href, label) in enumerate(NAV))
    ld = f'\n<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    robots = '\n<meta name="robots" content="noindex">' if noindex else ""
    preload = (f'\n<link rel="preload" as="image" href="assets/img/hero-{preload_poster}-poster-960.webp" media="(max-width: 899px)">'
               f'\n<link rel="preload" as="image" href="assets/img/hero-{preload_poster}-poster-1920.webp" media="(min-width: 900px)">'
               if preload_poster else "")
    full_title = title if slug == "index" else f"{title} | Garnet Events & Production"
    header_cls = "site-header" if preload_poster else "site-header is-solid"
    return f'''<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(full_title)}</title>
<meta name="description" content="{escape(description)}">{robots}
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Garnet Events &amp; Production">
<meta property="og:title" content="{escape(full_title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/cormorant-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/geist-latin.woff2" as="font" type="font/woff2" crossorigin>{preload}
<link rel="stylesheet" href="assets/css/site.css?v={CSS_V}">{ld}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

<header class="{header_cls}">
  <div class="wrap site-header__inner">
    <nav class="primary-nav" aria-label="Main">
      <ul>
{nav_items}
      </ul>
    </nav>
    <a class="brand" href="index.html" aria-label="Garnet Events &amp; Production, home">
      <span class="brand__crown"><img class="crown-white" src="assets/img/crown-white.png" alt="" width="247" height="162"><img class="crown-ink" src="assets/img/crown-ink.png" alt="" width="247" height="162"></span>
      <span class="brand__word">Garnet</span>
      <span class="brand__sub">Events &amp; Production</span>
    </a>
    <div class="header-actions">
      <a class="btn" href="contact.html">Enquire</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu"><span class="menu-toggle__bars"></span></button>
    </div>
  </div>
</header>

<div class="mobile-menu texture" id="mobile-menu">
  <nav aria-label="Mobile">
{mobile_items}
  </nav>
  <div class="mobile-menu__foot">
    <p class="script">Let's celebrate</p>
    <div class="mobile-menu__contact">
      <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
      <a href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener">WhatsApp {WA_DISPLAY}</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
  </div>
</div>

<main id="main">
{body}
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="assets/img/logo-nav-dark.png" alt="Garnet Events &amp; Production" width="247" height="220" loading="lazy">
        <p>Event design and production for weddings, corporate events and private celebrations. Since 2020.</p>
      </div>
      <div class="footer-col">
        <h2>Pages</h2>
        <ul>
{"".join(f'          <li><a href="{h}">{l}</a></li>{chr(10)}' for h, l in NAV)}        </ul>
      </div>
      <div class="footer-col">
        <h2>Get in touch</h2>
        <ul>
          <li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li>
          <li><a href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener">WhatsApp {WA_DISPLAY}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        </ul>
      </div>
    </div>
  </div>
  <p class="footer-word" aria-hidden="true">Garnet</p>
  <div class="wrap">
    <div class="footer-bottom">
      <span>© <span data-year>2026</span> Garnet Events &amp; Production</span>
      <span>{" · ".join(CITIES)}</span>
    </div>
  </div>
</footer>

<a class="wa-fab" href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{WA_ICON}</a>

<script src="assets/js/site.js?v={JS_V}" defer></script>
</body>
</html>
'''


# ---------------------------------------------------------------- pages

def home():
    tiles = [
        ("weddings", "Weddings", "gallery-03", "Velvet-draped wedding mandap with gold columns and floral urns", True,
         "The experience", "Ceremony and reception design, multi-day functions, and the planning that holds them together."),
        ("corporate", "Corporate", "gallery-05", "Corporate gala stage with a red backdrop and gold-lit runway", False,
         "", "Conferences, launches, annual days and award nights, produced like a show."),
        ("social", "Celebrations", "service-social", "Birthday table styled with garnet and gold balloons, roses and candles", False,
         "", "Birthdays, anniversaries and family gatherings, styled with the care of a wedding."),
        ("destination", "Destination", "service-destination", "Marquee reception at sunset with chandeliers and draped velvet", True,
         "Away from home", "Celebrations in another city, with venues, vendors and logistics sorted on the ground."),
    ]
    tile_html = "\n".join(
        f'''      <a class="tile{' tile--wide' if wide else ''}" href="services.html#{a}" data-reveal="mask" style="--d:{n % 2}">
        {img(i, alt, "100vw" if wide else "(min-width: 900px) 50vw, 100vw", parallax=wide)}
        <span class="tile__label"><span>{n:02d}.</span>{t}</span>
        <span class="tile__body">{f'<span class="eyebrow">{k}</span>' if k else ''}<p>{d}</p><span class="link-line">Explore {ARROW}</span></span>
      </a>''' for n, (a, t, i, alt, wide, k, d) in enumerate(tiles, 1))
    work = [
        ("gallery-01", "Ballroom wedding reception with tall floral centrepieces", "Reception, ballroom"),
        ("gallery-08", "Guests dancing under falling gold confetti", "Gala night"),
        ("gallery-07", "Tiered garnet cake on a styled dessert table", "Dessert table"),
        ("gallery-02", "Garnet rose beside gold filigree candle holders", "Table details"),
        ("gallery-06", "Outdoor marquee dinner lit by lanterns and string lights", "Marquee dinner"),
        ("gallery-04", "Place setting with gold charger and garnet napkin", "Place setting"),
    ]
    work_items = "\n".join(
        f'        <div class="rail__item"><figure>{img(n, alt, "(min-width: 1100px) 33vw, (min-width: 700px) 46vw, 82vw")}<figcaption>{cap}</figcaption></figure></div>'
        for n, alt, cap in work)

    body = f'''<section class="hero" aria-labelledby="page-title">
  {hero_video("home")}
  <div class="wrap hero__content">
    <div class="hero__center">
      <p class="eyebrow fade">[ Event design &amp; production ]</p>
      <h1 id="page-title" class="hero__title">
        <span class="rise"><span>Remembered,</span></span>
        <span class="rise" style="--d:1"><span class="script">not just</span></span>
        <span class="rise" style="--d:2"><span>noticed.</span></span>
      </h1>
    </div>
    <div class="hero__corners tiny fade" style="--d:4">
      <p>Your celebration isn't just an event.</p>
      <p>It's the one day everyone you love is in one room. We make sure it feels that way.</p>
    </div>
    <div class="hero__foot fade" style="--d:5"><a class="scroll-cue eyebrow" href="#studio"><span>Scroll</span><i></i></a></div>
  </div>
</section>

<section class="sec sec--garnet texture" id="studio" aria-labelledby="studio-title">
  <div class="wrap">
    <div class="statement__top">
      <h2 id="studio-title" class="caps-xl" data-reveal>We design days<br>people remember</h2>
      <p class="statement__since" data-reveal style="--d:1">[Since 2020]</p>
    </div>
    <div class="statement__row">
      <p class="eyebrow" data-reveal>About us</p>
      <div class="statement__img" data-reveal="mask">{poster("gallery", "Garnet rose petals by candlelight", "(min-width: 900px) 40vw, 100vw", parallax=True)}</div>
      <div class="statement__text" data-reveal style="--d:2">
        <p><strong>Garnet Events &amp; Production</strong> is a hands-on studio founded by Amit Agarwal. We plan, design and run weddings, corporate events and private celebrations, from the first idea to the last guest home.</p>
        <p>We don't believe in templates. We believe in detail, in calm on the day, and in décor that looks as good in person as it does in photographs.</p>
        <p><strong>Thoughtful. Personal. Unforgettable.</strong></p>
        <a class="link-line" href="about.html">Meet the founder {ARROW}</a>
      </div>
    </div>
  </div>
</section>

{services_rail()}

<section class="sec sec--rule" aria-labelledby="types-title">
  <div class="wrap">
    <div class="sec-head" data-reveal>
      <p class="script-head">What we do</p>
      <h2 id="types-title" class="caps-l">Four kinds of celebration</h2>
    </div>
    <div class="tiles">
{tile_html}
    </div>
  </div>
</section>

<section class="sec sec--olive texture" aria-labelledby="approach-title">
  <div class="wrap approach">
    <p class="approach__meta tiny">Since 2020<br>Kolkata to Dubai</p>
    <p class="script-head" data-reveal>Our approach</p>
    <div class="approach__img" data-reveal="mask">{img("founder-amit", "Amit Agarwal, founder of Garnet Events & Production", "230px")}</div>
    <h2 id="approach-title" class="caps-m" data-reveal style="max-width:24ch">An experience as careful as the celebration</h2>
    <div class="approach__cols" data-reveal style="--d:1">
      <p>Every event we take on starts with a conversation, not a catalogue. We want to know who is coming, what the day should feel like and what matters most to your family or your team. From there we design one clear plan and one look, and we hold every vendor to it.</p>
      <p>On the day, the people who planned your event are the people who run it. Timings, cues, stage, sound and light are handled quietly in the background, so you can stop managing and start celebrating. The day feels effortless because the hard part was done well in advance.</p>
    </div>
  </div>
</section>

<section class="sec" aria-labelledby="work-title">
  <div class="wrap trip">
    <div class="sec-bar">
      <h2 id="work-title" class="eyebrow">Selected work</h2>
      <p class="eyebrow sec-bar__mid">Rooms, tables &amp; moments</p>
      <a class="eyebrow" href="gallery.html" style="text-decoration:none">● View gallery</a>
    </div>
    <div class="rail" data-rail>
      <div class="rail__track" tabindex="0" role="region" aria-label="Selected work, scroll sideways">
{work_items}
      </div>
      <div class="rail__nav">
        <button class="rail__btn" type="button" data-rail-prev>Previous</button>
        <div class="rail__progress" aria-hidden="true"><span></span></div>
        <button class="rail__btn" type="button" data-rail-next>Next</button>
      </div>
    </div>
  </div>
</section>

{credits()}

{quotes()}

{cities_block()}

{cta()}'''

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Garnet Events & Production",
        "url": f"{SITE}/",
        "logo": f"{SITE}/assets/img/logo-full-light.png",
        "image": f"{SITE}/assets/img/og-image.jpg",
        "description": "Event design and production for weddings, corporate events and private celebrations.",
        "foundingDate": "2020",
        "founder": {"@type": "Person", "name": "Amit Agarwal"},
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "areaServed": [{"@type": "City", "name": c} for c in CITIES],
        "contactPoint": [{"@type": "ContactPoint", "telephone": PHONE_TEL, "contactType": "customer service", "availableLanguage": ["English", "Hindi"]}],
    }
    return page("index", "Garnet Events & Production | Weddings, corporate & social events",
                "Garnet Events & Production plans, designs and runs weddings, corporate events and private celebrations. Founded in 2020 by Amit Agarwal.",
                body, preload_poster="home", jsonld=jsonld)


def about():
    timeline = [
        ("2018", "The start", "Amit Agarwal builds his foundation in event management at NIEM."),
        ("Next", "Big productions", "Hands-on work on large productions, including Star Plus's Dance+ and the Tata Steel Marathon."),
        ("2020", "Garnet is founded", "Garnet Events & Production opens with one aim: thoughtfully planned, smoothly run events."),
        ("Today", "Across eight cities", "Weddings, corporate events and celebrations, from Kolkata to Dubai."),
    ]
    tl = "\n".join(
        f'      <li data-reveal style="--d:{i}"><span class="timeline__when">{w}</span><div><h3>{t}</h3><p>{d}</p></div></li>'
        for i, (w, t, d) in enumerate(timeline))
    values = [
        ("sage", "One team, start to finish", "The people who plan your event are the people who run it on the day. Nothing gets lost in a handover."),
        ("garnet", "Detail is the job", "Timings, cues and contingencies. The unglamorous parts are what make a day feel effortless."),
        ("black", "Calm under pressure", "Large productions taught us to stay steady when plans change. On event days, they usually do."),
    ]
    vals = "\n".join(
        f'      <div class="card card--{tone}" data-reveal style="--d:{i}"><span class="card__num">{ROMAN[i]}</span><h3>{t}</h3><p>{d}</p></div>'
        for i, (tone, t, d) in enumerate(values))
    body = f'''{inner_hero("about", "About", "The studio", "since 2020",
        "One person's love of events, grown into a team that plans, designs and runs them end to end.")}

<section class="sec" id="founder" aria-labelledby="founder-title">
  <div class="wrap founder">
    <div class="founder__img" data-reveal="mask">{img("founder-amit", "Amit Agarwal, founder of Garnet Events & Production", "(min-width: 900px) 42vw, 100vw")}</div>
    <div class="founder__body" data-reveal>
      <p class="script-head">Meet the founder</p>
      <h2 id="founder-title" class="caps-l">Amit Agarwal</h2>
      <p class="founder__quote">“Hi, I'm Amit. I make events unforgettable.”</p>
      <div class="prose">
        <p>Amit's journey began in 2018 at NIEM, where he built a strong foundation in event management. Hands-on experience on renowned productions followed, among them Star Plus's Dance+ and the Tata Steel Marathon, and taught him how large, high-pressure events are actually run.</p>
        <p>After further internships and freelance projects, he founded Garnet Events &amp; Production in 2020 with a clear aim: thoughtfully planned, smoothly executed events.</p>
        <p>Today Garnet plans weddings, corporate events, birthdays, family gatherings and more, each delivered with attention to detail, creativity and professionalism.</p>
      </div>
      <p class="founder__sign"><span class="script">Amit Agarwal</span><span class="tiny muted">Founder, Garnet Events &amp; Production</span></p>
    </div>
  </div>
</section>

<section class="sec sec--garnet texture" aria-labelledby="journey-title">
  <div class="wrap">
    <div class="sec-head sec-head--left" data-reveal>
      <p class="eyebrow">[ The journey ]</p>
      <h2 id="journey-title" class="caps-l">From passion<br>to production</h2>
    </div>
    <ol class="timeline">
{tl}
    </ol>
  </div>
</section>

{credits()}

<section class="sec sec--rule" aria-labelledby="values-title">
  <div class="wrap">
    <div class="sec-head" data-reveal>
      <p class="script-head">How we work</p>
      <h2 id="values-title" class="caps-l">What you can expect</h2>
    </div>
    <div class="cards3">
{vals}
    </div>
  </div>
</section>

{quotes()}

{cities_block()}

{cta()}'''
    return page("about", "About", "Garnet Events & Production was founded in 2020 by Amit Agarwal after years on large productions like Dance+ and the Tata Steel Marathon.",
                body, preload_poster="about")


def services():
    rows = [
        ("weddings", "Weddings", "Weddings &amp; functions", "gallery-03", "Velvet-draped wedding mandap with gold columns and floral urns",
         "From one ceremony to a week of functions, we design the look, book the right people and run the schedule, so your family can be part of the day instead of managing it.",
         "We start with how you want the day to feel, then build every function around it: the mandap, the stage, the flowers, the light and the timings. One team carries it from the first site visit to the last guest leaving.",
         ["Mandap, stage and décor design", "Haldi, mehendi, sangeet and reception", "Vendor booking and coordination", "On-the-day management, start to finish"]),
        ("corporate", "Corporate", "Corporate events", "gallery-05", "Corporate gala stage with a red backdrop and gold-lit runway",
         "Conferences, product launches, annual days and award nights, produced with the polish of a show and the discipline of a schedule.",
         "Our founder learned the trade on televised productions, so we think in cues, run-sheets and rehearsals. Your brand looks right on stage and your guests are looked after off it.",
         ["Stage, set and branding", "Sound, light and AV production", "Run-of-show and cue management", "Guest arrival and logistics"]),
        ("social", "Social", "Social celebrations", "service-social", "Birthday table styled with garnet and gold balloons, roses and candles",
         "Birthdays, anniversaries, baby showers and family get-togethers, styled with the same care we bring to a wedding.",
         "Smaller gatherings deserve the same thought. We can take on the whole event or simply style the room, set the table and bring in the entertainment.",
         ["Theme, décor and table styling", "Entertainment and performers", "Venue search, if you need one", "Full planning or styling only"]),
        ("destination", "Destination", "Destination events", "service-destination", "Marquee reception at sunset with chandeliers and draped velvet",
         "Celebrations in another city: we scout the venue, line up local vendors and manage the logistics, so the move doesn't become your problem.",
         "We have worked across eight cities, from Kolkata and Guwahati to Jaipur, Hyderabad and Dubai. We know how to get people, décor and equipment where they need to be.",
         ["Venue scouting", "Local vendors and on-ground team", "Scheduling and logistics planning", "Experience across eight cities, including Dubai"]),
    ]
    tabs = "".join(
        f'<button class="tabs__tab" type="button" role="tab" id="tab-{a}" aria-controls="{a}" aria-selected="{"true" if n == 0 else "false"}" tabindex="{0 if n == 0 else -1}"><sup>{ROMAN[n]}</sup>{short}</button>'
        for n, (a, short, *_rest) in enumerate(rows))
    panels = "\n".join(
        f'''    <article class="panel" id="{a}" role="tabpanel" aria-labelledby="tab-{a}" tabindex="-1">
      <div class="panel__img">{img(i, alt, "(min-width: 900px) 42vw, 100vw")}</div>
      <div class="panel__body">
        <p class="script-head">{title}</p>
        <div class="panel__cols">
          <p>{p1}</p>
          <p class="italic">{p2}</p>
        </div>
        <ul class="panel__list">{"".join(f"<li>{x}</li>" for x in lst)}</ul>
        <a class="btn btn--ink" href="contact.html" style="justify-self:start">Enquire about {short.lower()}</a>
      </div>
    </article>''' for n, (a, short, title, i, alt, p1, p2, lst) in enumerate(rows))
    steps = [
        ("Conversation", "We learn what you want, who's coming and what matters most to you."),
        ("Design", "Concept, theme, layout and budget, agreed before anything is booked."),
        ("Production", "Vendors, décor, AV and logistics, coordinated by one team."),
        ("The day", "We run everything on site, so you can be a guest at your own event."),
    ]
    step_html = "\n".join(
        f'      <div class="card card--line" data-reveal style="--d:{i}"><span class="card__num">{ROMAN[i]}</span><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(steps))
    body = f'''{inner_hero("services", "Services", "What we do", "start to finish",
        "Four kinds of events, nine services, one team. Take all of it, or only the parts you need.")}

<section class="sec" aria-labelledby="types-title">
  <div class="wrap">
    <h2 id="types-title" class="visually-hidden">Event types</h2>
    <div class="tabs" data-tabs>
      <div class="tabs__list" role="tablist" aria-label="Event types">{tabs}</div>
{panels}
    </div>
  </div>
</section>

<div class="sec--rule"></div>
{services_rail()}

<section class="sec sec--olive texture" aria-labelledby="process-title">
  <div class="wrap">
    <div class="sec-head" data-reveal>
      <p class="script-head">How it works</p>
      <h2 id="process-title" class="caps-l">Four steps, no surprises</h2>
    </div>
    <div class="cards4">
{step_html}
    </div>
  </div>
</section>

{cta()}'''
    return page("services", "Services", "Wedding, corporate, social and destination event planning: design, vendors, décor, AV, logistics and on-site management by Garnet Events & Production.",
                body, preload_poster="services")


def gallery():
    items = [
        ("gallery-01", "weddings", "Ballroom wedding reception with tall floral centrepieces", "Ballroom reception"),
        ("gallery-03", "weddings", "Velvet-draped wedding mandap with gold columns and floral urns", "Mandap design"),
        ("gallery-05", "corporate", "Corporate gala stage with a red backdrop and gold-lit runway", "Gala stage"),
        ("service-social", "social", "Birthday table styled with garnet and gold balloons, roses and candles", "Birthday styling"),
        ("gallery-02", "weddings", "Garnet rose beside gold filigree candle holders", "Table details"),
        ("gallery-06", "destination", "Outdoor marquee dinner lit by lanterns and string lights", "Marquee dinner"),
        ("gallery-08", "corporate", "Guests dancing under falling gold confetti", "Gala night"),
        ("gallery-07", "social", "Tiered garnet cake on a styled dessert table", "Dessert table"),
        ("service-destination", "destination", "Marquee reception at sunset with chandeliers and draped velvet", "Sunset marquee"),
        ("gallery-04", "social", "Place setting with gold charger and garnet napkin", "Place setting"),
    ]
    figs = "\n".join(
        f'''      <figure class="gallery__item" data-cat="{cat}" data-reveal style="--d:{n % 3}">
        <button class="gallery__btn" type="button" aria-label="Open image: {escape(cap)}">{img(nm, alt, "(min-width: 900px) 33vw, 50vw").replace("<img ", f'<img data-full="assets/img/{nm}-{IMAGES[nm][0]}.webp" ', 1)}</button>
        <figcaption>{cap}</figcaption>
      </figure>''' for n, (nm, cat, alt, cap) in enumerate(items))
    chips = [("all", "All"), ("weddings", "Weddings"), ("corporate", "Corporate"), ("social", "Social"), ("destination", "Destination")]
    chip_html = "".join(
        f'<button class="chip" type="button" data-filter="{f}" aria-pressed="{"true" if f == "all" else "false"}"><sup>{ROMAN[i]}</sup>{l}</button>'
        for i, (f, l) in enumerate(chips))
    body = f'''{inner_hero("gallery", "Gallery", "Selected work", "a look inside",
        "Weddings, corporate evenings and private celebrations: the rooms, tables and moments we design.")}

<section class="sec" aria-labelledby="gallery-title">
  <div class="wrap">
    <h2 id="gallery-title" class="visually-hidden">Gallery</h2>
    <div class="filters" role="group" aria-label="Filter by event type">{chip_html}</div>
    <div class="gallery">
{figs}
    </div>
  </div>
</section>

<dialog class="lightbox" id="lightbox" aria-label="Image viewer">
  <div class="lightbox__bar"><span class="lightbox__count"></span><span class="lightbox__caption"></span><button class="icon-btn" type="button" data-lb-close aria-label="Close"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 3l10 10M13 3 3 13" stroke="currentColor" stroke-width="1.3"/></svg></button></div>
  <div class="lightbox__stage"><img src="" alt=""></div>
  <div class="lightbox__nav">
    <button class="icon-btn" type="button" data-lb-prev aria-label="Previous image"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3 5 8l5 5" fill="none" stroke="currentColor" stroke-width="1.3"/></svg></button>
    <button class="icon-btn" type="button" data-lb-next aria-label="Next image"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="m6 3 5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.3"/></svg></button>
  </div>
</dialog>

{cta()}'''
    return page("gallery", "Gallery", "A look at weddings, corporate evenings and private celebrations designed by Garnet Events & Production.",
                body, preload_poster="gallery")


def contact():
    events = ["Wedding", "Corporate event", "Birthday / anniversary", "Family gathering", "Destination event", "Something else"]
    opts = "".join(f"<option>{e}</option>" for e in events)
    body = f'''{inner_hero("contact", "Contact", "Let's plan", "your celebration",
        "Tell us the date, the city and roughly how many guests. We'll come back with ideas and a plan.")}

<section class="sec" aria-labelledby="enquire-title">
  <div class="wrap contact">
    <div class="contact__panel sec--garnet texture" style="position:relative" data-reveal>
      <p class="script-head">Talk to us</p>
      <h2 class="caps-m">Call, message<br>or email</h2>
      <div class="channels">
        <a class="channel" href="tel:{PHONE_TEL}"><span class="channel__label">Call</span><span class="channel__value">{PHONE_DISPLAY}</span>{ARROW}</a>
        <a class="channel" href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener"><span class="channel__label">WhatsApp</span><span class="channel__value">{WA_DISPLAY}</span>{ARROW}</a>
        <a class="channel" href="mailto:{EMAIL}"><span class="channel__label">Email</span><span class="channel__value">{EMAIL}</span>{ARROW}</a>
      </div>
      <p class="tiny" style="opacity:.8">We work across {", ".join(CITIES[:-1])} and {CITIES[-1]}.</p>
    </div>
    <div class="contact__form" data-reveal style="--d:1">
      <p class="eyebrow muted">[ Enquiry form ]</p>
      <h2 id="enquire-title" class="caps-m" style="margin:14px 0 36px">Send us the details</h2>
      <form class="form" id="enquiry-form" data-whatsapp="{WA_NUMBER}" novalidate>
        <div class="form__row">
          <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required></div>
          <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required></div>
        </div>
        <div class="form__row">
          <div class="field"><label for="f-event">Type of event</label><select id="f-event" name="event" required><option value="">Choose one</option>{opts}</select></div>
          <div class="field"><label for="f-date">Date (if known)</label><input id="f-date" name="date" type="date"></div>
        </div>
        <div class="form__row">
          <div class="field"><label for="f-city">City</label><input id="f-city" name="city" autocomplete="address-level2"></div>
          <div class="field"><label for="f-guests">Guests (approx.)</label><input id="f-guests" name="guests" inputmode="numeric"></div>
        </div>
        <div class="field"><label for="f-message">Anything else?</label><textarea id="f-message" name="message" placeholder="Venue, budget, ideas you love…"></textarea></div>
        <button class="btn btn--fill btn--block" type="submit">Send on WhatsApp {ARROW}</button>
        <p class="form__note">This opens WhatsApp with your details filled in. Prefer email? Write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      </form>
    </div>
  </div>
</section>'''
    return page("contact", "Contact", f"Plan your wedding, corporate event or celebration with Garnet Events & Production. Call {PHONE_DISPLAY}, WhatsApp {WA_DISPLAY} or email {EMAIL}.",
                body, preload_poster="contact")


def not_found():
    body = f'''<section class="sec">
  <div class="wrap notfound">
    <p class="eyebrow muted">[ 404 ]</p>
    <h1 class="caps-l">This page<br>doesn't exist</h1>
    <p class="lead italic muted">It may have moved, or the link may be mistyped.</p>
    <a class="btn btn--ink" href="index.html">Back to the homepage</a>
  </div>
</section>'''
    html = page("404", "Page not found", "This page could not be found.", body, noindex=True)
    # Served from any path, so links must be root-relative.
    for rel in ["assets/", "index.html", "about.html", "services.html", "gallery.html", "contact.html"]:
        html = html.replace(f'"{rel}', f'"/{rel}')
    return html


def main():
    pages = {
        "index.html": home(), "about.html": about(), "services.html": services(),
        "gallery.html": gallery(), "contact.html": contact(), "404.html": not_found(),
    }
    for name, html in pages.items():
        (ROOT / name).write_text(html, encoding="utf-8")
        print("wrote", name)
    urls = "".join(
        f"  <url><loc>{SITE}/{'' if h == 'index.html' else h}</loc></url>\n" for h, _ in NAV)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n',
        encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print("wrote sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
