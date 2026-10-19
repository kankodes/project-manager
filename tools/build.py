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

# width x height of the largest WebP for each image (smaller one is always 800w)
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

ARROW = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" stroke="currentColor" stroke-width="1.4"/></svg>'
WA_ICON = ('<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16 3C9 3 3.5 8.5 3.5 15.5c0 2.4.7 4.7 1.9 6.7L3 29l7-1.8c1.9 1 4 1.6 6 1.6 7 0 12.5-5.5 12.5-12.5S23 3 16 3zm0 22.8c-1.8 0-3.6-.5-5.1-1.4l-.4-.2-4.2 1.1 1.1-4.1-.2-.4c-1-1.6-1.5-3.4-1.5-5.3C5.5 9.6 10.2 5 16 5s10.5 4.7 10.5 10.5S21.8 25.8 16 25.8zm5.8-7.9c-.3-.2-1.9-.9-2.1-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.2-1.3-.5-2.5-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-1-2.3c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.1 3.3 5.2 4.6.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.9-.8 2.1-1.5.3-.8.3-1.4.2-1.5-.1-.2-.3-.2-.6-.4z"/></svg>')
PAUSE = '<svg class="icon-pause" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2h3v12H4zM9 2h3v12H9z" fill="currentColor"/></svg>'
PLAY = '<svg class="icon-play" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2l10 6-10 6z" fill="currentColor"/></svg>'


def img(name, alt, sizes, eager=False, cls=""):
    w, h = IMAGES[name]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="assets/img/{name}-800.webp" '
            f'srcset="assets/img/{name}-800.webp 800w, assets/img/{name}-{w}.webp {w}w" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{escape(alt)}" {load} decoding="async">')


def hero_video(page):
    return f'''<div class="hero__media">
      <video muted loop playsinline preload="none" aria-hidden="true"
        poster="assets/img/hero-{page}-poster-960.webp"
        data-poster-lg="assets/img/hero-{page}-poster-1920.webp"
        data-src-sm="assets/videos/hero-{page}-sm.mp4"
        data-src-lg="assets/videos/hero-{page}.mp4"></video>
      <button class="media-toggle" type="button" aria-pressed="false" aria-label="Pause background video">{PAUSE}{PLAY}</button>
    </div>'''


def hero(page, label, title, lead, actions, home=False):
    title_cls = "display" if home else "h1"
    return f'''<section class="hero{'' if home else ' hero--inner'}" aria-labelledby="page-title">
  <div class="wrap">
    <span class="label">{label}</span>
    <div class="hero__grid">
      <h1 id="page-title" class="{title_cls} hero__title">{title}</h1>
      <div class="hero__aside">
        <p class="lead">{lead}</p>
        {f'<div class="hero__actions">{actions}</div>' if actions else ''}
      </div>
    </div>
    {hero_video(page)}
  </div>
</section>'''


def channels():
    return f'''<div class="channels">
        <a class="channel" href="tel:{PHONE_TEL}"><span class="channel__label">Call</span><span class="channel__value">{PHONE_DISPLAY}</span>{ARROW}</a>
        <a class="channel" href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener"><span class="channel__label">WhatsApp</span><span class="channel__value">{WA_DISPLAY}</span>{ARROW}</a>
        <a class="channel" href="mailto:{EMAIL}"><span class="channel__label">Email</span><span class="channel__value">{EMAIL}</span>{ARROW}</a>
      </div>'''


def cta():
    return f'''<section class="section section--rule" aria-labelledby="cta-title">
  <div class="wrap cta">
    <div data-reveal>
      <span class="label">Get in touch</span>
      <h2 id="cta-title" class="h2" style="margin-top:18px">Planning something? Let's talk.</h2>
      <p class="lead muted" style="margin-top:20px;max-width:40ch">Share the date, the city and a rough guest count — we'll take it from there.</p>
    </div>
    <div data-reveal>{channels()}</div>
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
    return f'''<section class="section section--soft" aria-labelledby="credits-title">
  <div class="wrap credits" data-reveal>
    <div>
      <span class="label">Before Garnet</span>
      <h2 id="credits-title" class="h3" style="margin-top:14px;max-width:24ch">Our founder cut his teeth on large productions, including:</h2>
    </div>
    <ul class="credits__logos">
        {imgs}
    </ul>
  </div>
</section>'''


def cities_block(title="Where we've worked"):
    items = "".join(f"<li>{c}</li>" for c in CITIES)
    return f'''<section class="section" aria-labelledby="cities-title">
  <div class="wrap sec-head" style="margin-bottom:0" data-reveal>
    <div><span class="label" id="cities-title">{title}</span></div>
    <ul class="cities">{items}</ul>
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
        f'''      <figure class="quote" data-reveal><blockquote><p>“{escape(q)}”</p></blockquote><figcaption>{escape(n)}</figcaption></figure>'''
        for q, n in QUOTES)
    return f'''<section class="section section--dark" aria-labelledby="quotes-title">
  <div class="wrap">
    <div class="sec-head">
      <span class="label">Kind words</span>
      <h2 id="quotes-title" class="h2">From the families and teams we've worked with.</h2>
    </div>
    <div class="quotes">
{items}
    </div>
  </div>
</section>'''


CAPS = [
    ("Event planning", "Comprehensive planning, from concept to execution."),
    ("Event design", "Theme and design development, built around your vision."),
    ("Venue selection", "Help finding the right location for your event."),
    ("Vendor coordination", "Every vendor managed and coordinated by one team."),
    ("Décor & styling", "Decoration and styling that sets the atmosphere."),
    ("On-site management", "Oversight on the day, so the event runs to plan."),
    ("Logistics", "Detailed scheduling and logistical planning."),
    ("Audio-visual production", "Sound, light and equipment for performances and presentations."),
    ("Entertainment booking", "Artists, performers and entertainment, arranged for you."),
]


def caps():
    items = "\n".join(
        f'      <li class="cap"><span class="cap__num">{i:02d}</span><h3>{t}</h3><p>{d}</p></li>'
        for i, (t, d) in enumerate(CAPS, 1))
    return f'''<ul class="caps" data-reveal>
{items}
    </ul>'''


def page(slug, title, description, body, preload_poster=False, jsonld=None, noindex=False):
    current = f"{slug}.html"
    canonical = f"{SITE}/" if slug == "index" else f"{SITE}/{slug}.html"
    aria = ' aria-current="page"'
    nav_items = "\n".join(
        f'          <li><a href="{href}"{aria if href == current else ""}>{label}</a></li>'
        for href, label in NAV)
    mobile_items = "\n".join(
        f'      <a href="{href}"{aria if href == current else ""}>{label}</a>'
        for href, label in NAV)
    ld = f'\n<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    robots = '\n<meta name="robots" content="noindex">' if noindex else ""
    preload = (f'\n<link rel="preload" as="image" href="assets/img/hero-{preload_poster}-poster-960.webp" media="(max-width: 899px)">'
               if preload_poster else "")
    full_title = title if slug == "index" else f"{title} — Garnet Events & Production"
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
<link rel="preload" href="assets/fonts/instrument-serif-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/geist-latin.woff2" as="font" type="font/woff2" crossorigin>{preload}
<link rel="stylesheet" href="assets/css/site.css?v={CSS_V}">{ld}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="brand" href="index.html" aria-label="Garnet Events &amp; Production — home">
      <img src="assets/img/logo-full-light.png" alt="" width="247" height="220">
    </a>
    <nav class="primary-nav" aria-label="Main">
      <ul>
{nav_items}
      </ul>
    </nav>
    <div class="header-actions">
      <a class="btn btn--solid" href="contact.html">Plan your event</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu"><span class="menu-toggle__bars"></span></button>
    </div>
  </div>
</header>

<div class="mobile-menu" id="mobile-menu">
  <nav aria-label="Mobile">
{mobile_items}
  </nav>
  <div class="mobile-menu__contact">
    <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
    <a href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener">WhatsApp {WA_DISPLAY}</a>
    <a href="mailto:{EMAIL}">{EMAIL}</a>
  </div>
</div>

<main id="main">
{body}
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/img/logo-nav-dark.png" alt="Garnet Events &amp; Production" width="247" height="220" loading="lazy">
        <p>Event design and production for weddings, corporate events and private celebrations. Est. 2020.</p>
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
    actions = (f'<a class="btn btn--solid" href="contact.html">Plan your event {ARROW}</a>'
               f'<a class="btn btn--ghost" href="gallery.html">See our work</a>')
    types = [
        ("weddings", "Weddings", "gallery-03", "Velvet-draped wedding mandap with gold columns and floral urns",
         "Ceremony and reception design, multi-day functions, and the planning that holds them together."),
        ("corporate", "Corporate events", "gallery-05", "Corporate gala stage with a red backdrop and gold-lit runway",
         "Conferences, launches, annual days and award nights — staging, AV and guests handled."),
        ("social", "Social celebrations", "service-social", "Birthday table styled with garnet and gold balloons, roses and candles",
         "Birthdays, anniversaries and family gatherings, styled with the care of a wedding."),
        ("destination", "Destination events", "service-destination", "Marquee reception at sunset with chandeliers and draped velvet",
         "Celebrations away from home, with venues, vendors and logistics sorted on the ground."),
    ]
    type_cards = "\n".join(
        f'''      <a class="type" href="services.html#{a}" data-reveal>
        <div class="type__img">{img(i, alt, "(min-width: 1100px) 25vw, (min-width: 640px) 50vw, 100vw")}</div>
        <span class="type__num">{n:02d}</span>
        <h3 class="h3">{t}</h3>
        <p>{d}</p>
      </a>''' for n, (a, t, i, alt, d) in enumerate(types, 1))
    work = [
        ("gallery-01", "Ballroom wedding reception with tall floral centrepieces", "Reception, ballroom", "(min-width: 900px) 58vw, 100vw"),
        ("gallery-08", "Guests dancing under falling gold confetti", "Gala night", "(min-width: 900px) 42vw, 50vw"),
        ("gallery-07", "Tiered garnet cake on a styled dessert table", "Dessert table", "(min-width: 900px) 42vw, 50vw"),
        ("gallery-02", "Garnet rose beside gold filigree candle holders", "Table details", "(min-width: 900px) 33vw, 50vw"),
        ("gallery-06", "Outdoor marquee dinner lit by lanterns and string lights", "Marquee dinner", "(min-width: 900px) 67vw, 50vw"),
    ]
    work_items = "\n".join(
        f'      <figure class="work__item">{img(n, alt, s)}<figcaption>{cap}</figcaption></figure>'
        for n, alt, cap, s in work)
    facts = [("Founded", "2020"), ("Founder", "Amit Agarwal"), ("Events", "Weddings, corporate, social"), ("Cities", "8, including Dubai")]
    fact_items = "".join(f"<li><span>{k}</span><span>{v}</span></li>" for k, v in facts)

    body = f'''{hero("home", "Event design &amp; production · Est. 2020",
        "Remembered, <em>not just</em> noticed.",
        "Garnet Events &amp; Production plans, designs and runs weddings, corporate events and private celebrations — from the first conversation to the last guest home.",
        actions, home=True)}

<section class="section" aria-labelledby="studio-title">
  <div class="wrap intro">
    <span class="label" id="studio-title">The studio</span>
    <div class="intro__body">
      <div data-reveal>
        <p class="statement">Founded in 2020 by Amit Agarwal, Garnet is a hands-on team that takes care of every part of an event — design, vendors, logistics, sound and light — so you can be present for it.</p>
        <a class="link-arrow" href="about.html#founder">Meet the founder {ARROW}</a>
      </div>
      <ul class="intro__facts" data-reveal>{fact_items}</ul>
    </div>
  </div>
</section>

<section class="section section--rule" aria-labelledby="types-title">
  <div class="wrap">
    <div class="sec-head">
      <span class="label">What we do</span>
      <h2 id="types-title" class="h2">Four kinds of events. One team for all of it.</h2>
    </div>
    <div class="types">
{type_cards}
    </div>
  </div>
</section>

<section class="section section--soft" aria-labelledby="caps-title">
  <div class="wrap">
    <div class="sec-head">
      <span class="label">Under one roof</span>
      <h2 id="caps-title" class="h2">Everything an event needs, handled.</h2>
    </div>
    {caps()}
  </div>
</section>

<section class="section" aria-labelledby="work-title">
  <div class="wrap">
    <div class="sec-head">
      <span class="label">Selected work</span>
      <h2 id="work-title" class="h2">Rooms, tables and moments we've designed.</h2>
    </div>
    <div class="work" data-reveal>
{work_items}
    </div>
    <div class="work-foot"><a class="link-arrow" href="gallery.html">View the gallery {ARROW}</a></div>
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
    return page("index", "Garnet Events & Production — Weddings, corporate & social events",
                "Garnet Events & Production plans, designs and runs weddings, corporate events and private celebrations. Founded in 2020 by Amit Agarwal.",
                body, preload_poster="home", jsonld=jsonld)


def about():
    timeline = [
        ("2018", "The start", "Amit Agarwal builds his foundation in event management at NIEM."),
        ("Next", "Big productions", "Hands-on work on large productions, including Star Plus's Dance+ and the Tata Steel Marathon."),
        ("2020", "Garnet is founded", "Garnet Events & Production opens with one aim: thoughtfully planned, smoothly run events."),
        ("Today", "Weddings, corporate & social", "A team working across eight cities, from Kolkata to Dubai."),
    ]
    tl = "\n".join(
        f'      <li><span class="timeline__when">{w}</span><div><h3>{t}</h3><p>{d}</p></div></li>'
        for w, t, d in timeline)
    values = [
        ("One team, start to finish", "The people who plan your event are the people who run it on the day. Nothing gets lost in a handover."),
        ("Detail is the job", "Timings, cues, contingencies — the unglamorous parts are what make a day feel effortless."),
        ("Calm under pressure", "Large productions taught us to stay steady when plans change. On event days, they usually do."),
    ]
    vals = "\n".join(
        f'      <div class="step" data-reveal><span class="step__num">{i:02d}</span><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(values, 1))
    body = f'''{hero("about", "About",
        "A hands-on studio, founded in 2020.",
        "Garnet started with one person's love of events and grew into a team that plans, designs and runs them end to end.",
        f'<a class="link-arrow" href="#founder">Meet the founder {ARROW}</a>')}

<section class="section" id="founder" aria-labelledby="founder-title">
  <div class="wrap founder">
    <div class="founder__img" data-reveal>{img("founder-amit", "Amit Agarwal, founder of Garnet Events & Production", "(min-width: 900px) 40vw, 100vw")}</div>
    <div class="founder__body" data-reveal>
      <span class="label">The founder</span>
      <h2 id="founder-title" class="h2">“Hi, I'm Amit. I make events unforgettable.”</h2>
      <div class="prose lead">
        <p>Amit Agarwal's journey began in 2018 at NIEM, where he built a strong foundation in event management. Hands-on experience on renowned productions followed — among them Star Plus's Dance+ and the Tata Steel Marathon — and taught him how large, high-pressure events are actually run.</p>
        <p>After further internships and freelance projects, he founded Garnet Events &amp; Production in 2020 with a clear aim: thoughtfully planned, smoothly executed events.</p>
        <p>Today Garnet plans weddings, corporate events, birthdays, family gatherings and more — each delivered with attention to detail, creativity and professionalism.</p>
      </div>
      <p class="founder__sign">Amit Agarwal<small>Founder, Garnet Events &amp; Production</small></p>
    </div>
  </div>
</section>

<section class="section section--rule" aria-labelledby="journey-title">
  <div class="wrap sec-head" style="margin-bottom:0">
    <div><span class="label">The journey</span><h2 id="journey-title" class="h2" style="margin-top:18px">From passion to production.</h2></div>
    <ol class="timeline" data-reveal>
{tl}
    </ol>
  </div>
</section>

{credits()}

<section class="section" aria-labelledby="values-title">
  <div class="wrap">
    <div class="sec-head">
      <span class="label">How we work</span>
      <h2 id="values-title" class="h2">What you can expect from us.</h2>
    </div>
    <div class="cols3">
{vals}
    </div>
  </div>
</section>

{quotes()}

{cities_block()}

{cta()}'''
    return page("about", "About", "Garnet Events & Production was founded in 2020 by Amit Agarwal after years on large productions like Dance+ and the Tata Steel Marathon.", body)


def services():
    rows = [
        ("weddings", "Weddings", "gallery-03", "Velvet-draped wedding mandap with gold columns and floral urns",
         "From one ceremony to a week of functions, we design the look, book the right people and run the schedule, so your family can be part of the day instead of managing it.",
         ["Mandap, stage and décor design", "Haldi, mehendi, sangeet and reception", "Vendor booking and coordination", "On-the-day management, start to finish"]),
        ("corporate", "Corporate events", "gallery-05", "Corporate gala stage with a red backdrop and gold-lit runway",
         "Conferences, product launches, annual days and award nights — produced with the polish of a show and the discipline of a schedule.",
         ["Stage, set and branding", "Sound, light and AV production", "Run-of-show and cue management", "Guest arrival and logistics"]),
        ("social", "Social celebrations", "service-social", "Birthday table styled with garnet and gold balloons, roses and candles",
         "Birthdays, anniversaries, baby showers and family get-togethers, styled with the same care we bring to a wedding.",
         ["Theme, décor and table styling", "Entertainment and performers", "Venue search, if you need one", "Full planning or styling only"]),
        ("destination", "Destination events", "service-destination", "Marquee reception at sunset with chandeliers and draped velvet",
         "Celebrations in another city: we scout the venue, line up local vendors and manage the logistics, so the move doesn't become your problem.",
         ["Venue scouting", "Local vendors and on-ground team", "Scheduling and logistics planning", "Experience across eight cities, including Dubai"]),
    ]
    row_html = "\n".join(
        f'''    <article class="svc" id="{a}" data-reveal>
      <div class="svc__img">{img(i, alt, "(min-width: 900px) 50vw, 100vw")}</div>
      <div class="svc__body">
        <span class="label">{n:02d}</span>
        <h2 class="h2">{t}</h2>
        <p class="lead">{d}</p>
        <ul class="svc__list">{"".join(f"<li>{x}</li>" for x in lst)}</ul>
      </div>
    </article>''' for n, (a, t, i, alt, d, lst) in enumerate(rows, 1))
    steps = [
        ("Conversation", "We learn what you want, who's coming and what matters most to you."),
        ("Design", "Concept, theme, layout and budget — agreed before anything is booked."),
        ("Production", "Vendors, décor, AV and logistics, coordinated by one team."),
        ("The day", "We run everything on site, so you can be a guest at your own event."),
    ]
    step_html = "\n".join(
        f'      <div class="step" data-reveal><span class="step__num">{i:02d}</span><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(steps, 1))
    body = f'''{hero("services", "Services",
        "From the first idea to the last guest home.",
        "Four kinds of events, one team. We can plan and produce every part of it, or just the parts you need help with.",
        f'<a class="btn btn--solid" href="contact.html">Plan your event {ARROW}</a>')}

<section class="section" aria-label="Event types">
  <div class="wrap">
{row_html}
  </div>
</section>

<section class="section section--soft" aria-labelledby="caps-title">
  <div class="wrap">
    <div class="sec-head">
      <span class="label">Under one roof</span>
      <h2 id="caps-title" class="h2">What's included.</h2>
    </div>
    {caps()}
  </div>
</section>

<section class="section section--dark" aria-labelledby="process-title">
  <div class="wrap">
    <div class="sec-head">
      <span class="label">How it works</span>
      <h2 id="process-title" class="h2">Four steps, no surprises.</h2>
    </div>
    <div class="cols4">
{step_html}
    </div>
  </div>
</section>

{cta()}'''
    return page("services", "Services", "Wedding, corporate, social and destination event planning — design, vendors, décor, AV, logistics and on-site management by Garnet Events & Production.", body)


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
        f'''      <figure class="gallery__item" data-cat="{cat}">
        <button class="gallery__btn" type="button" aria-label="Open image: {escape(cap)}">{img(n, alt, "(min-width: 900px) 33vw, 50vw").replace("<img ", f'<img data-full="assets/img/{n}-{IMAGES[n][0]}.webp" ', 1)}</button>
        <figcaption>{cap}</figcaption>
      </figure>''' for n, cat, alt, cap in items)
    chips = [("all", "All"), ("weddings", "Weddings"), ("corporate", "Corporate"), ("social", "Social"), ("destination", "Destination")]
    chip_html = "".join(
        f'<button class="chip" type="button" data-filter="{f}" aria-pressed="{"true" if f == "all" else "false"}">{l}</button>'
        for f, l in chips)
    body = f'''{hero("gallery", "Gallery",
        "Selected work.",
        "Weddings, corporate evenings and private celebrations — a look at the settings we design.",
        "")}

<section class="section" aria-label="Gallery">
  <div class="wrap">
    <div class="filters" role="group" aria-label="Filter by event type">{chip_html}</div>
    <div class="gallery">
{figs}
    </div>
  </div>
</section>

<dialog class="lightbox" id="lightbox" aria-label="Image viewer">
  <div class="lightbox__bar"><span class="lightbox__count"></span><span class="lightbox__caption"></span><button class="icon-btn" type="button" data-lb-close aria-label="Close"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 3l10 10M13 3 3 13" stroke="currentColor" stroke-width="1.5"/></svg></button></div>
  <div class="lightbox__stage"><img src="" alt=""></div>
  <div class="lightbox__nav">
    <button class="icon-btn" type="button" data-lb-prev aria-label="Previous image"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3 5 8l5 5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></button>
    <button class="icon-btn" type="button" data-lb-next aria-label="Next image"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="m6 3 5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></button>
  </div>
</dialog>

{cta()}'''
    return page("gallery", "Gallery", "A look at weddings, corporate evenings and private celebrations designed by Garnet Events & Production.", body)


def contact():
    events = ["Wedding", "Corporate event", "Birthday / anniversary", "Family gathering", "Destination event", "Something else"]
    opts = "".join(f"<option>{e}</option>" for e in events)
    body = f'''{hero("contact", "Contact",
        "Let's plan your event.",
        "Tell us the date, the city and roughly how many guests. We'll come back with ideas and a plan.",
        "")}

<section class="section" aria-labelledby="enquire-title">
  <div class="wrap contact">
    <div data-reveal>
      <span class="label">Talk to us directly</span>
      <h2 class="h2" style="margin:18px 0 32px">Call, message or email.</h2>
      {channels()}
      <p class="muted" style="margin-top:28px">We work across {", ".join(CITIES[:-1])} and {CITIES[-1]}.</p>
    </div>
    <div data-reveal>
      <span class="label">Enquiry form</span>
      <h2 id="enquire-title" class="h2" style="margin:18px 0 32px">Send us the details.</h2>
      <form class="form" id="enquiry-form" data-whatsapp="{WA_NUMBER}" novalidate>
        <div class="form__row">
          <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required></div>
          <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required></div>
        </div>
        <div class="form__row">
          <div class="field"><label for="f-event">Type of event</label><select id="f-event" name="event" required><option value="">Choose one</option>{opts}</select></div>
          <div class="field"><label for="f-date">Date <span class="muted">(if known)</span></label><input id="f-date" name="date" type="date"></div>
        </div>
        <div class="form__row">
          <div class="field"><label for="f-city">City</label><input id="f-city" name="city" autocomplete="address-level2"></div>
          <div class="field"><label for="f-guests">Guests <span class="muted">(approx.)</span></label><input id="f-guests" name="guests" inputmode="numeric"></div>
        </div>
        <div class="field"><label for="f-message">Anything else?</label><textarea id="f-message" name="message" placeholder="Venue, budget, ideas you love…"></textarea></div>
        <button class="btn btn--solid btn--block" type="submit">Send on WhatsApp {ARROW}</button>
        <p class="form__note">This opens WhatsApp with your details filled in. Prefer email? Write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      </form>
    </div>
  </div>
</section>'''
    return page("contact", "Contact", f"Plan your wedding, corporate event or celebration with Garnet Events & Production. Call {PHONE_DISPLAY}, WhatsApp {WA_DISPLAY} or email {EMAIL}.", body)


def not_found():
    body = f'''<section class="section">
  <div class="wrap notfound">
    <span class="label">404</span>
    <h1 class="h1">This page doesn't exist.</h1>
    <p class="lead muted">It may have moved, or the link may be mistyped.</p>
    <div><a class="btn btn--solid" href="index.html">Back to the homepage {ARROW}</a></div>
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
