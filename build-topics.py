#!/usr/bin/env python3
"""
Generate static, indexable topic pages for Many Paths from knowledge-base.js.

Reads  : spiritual-companion/knowledge-base.js
Writes : spiritual-companion/topics/*.html, sitemap.xml, robots.txt

Every page is real prose a search engine can read, in one language, with
canonical + hreflang so English and Tamil versions reinforce rather than
compete. Re-run after editing the knowledge base.
"""
import json, os, re, html, datetime

# Run from anywhere: looks for knowledge-base.js beside this script, then in
# a spiritual-companion/ subfolder, so it works whether the site files are at
# the repo root or nested.
_here = os.path.dirname(os.path.abspath(__file__))
_nested = os.path.join(_here, "spiritual-companion")
ROOT = _nested if os.path.exists(os.path.join(_nested, "knowledge-base.js")) else _here
BASE = "https://psaraj12.github.io/many-paths/"
TODAY = datetime.date.today().isoformat()

LANGS = {
    "en": {
        "code": "en", "suffix": "",
        "site": "Many Paths", "tag": "A spiritual companion",
        "topics": "Topics", "all": "All topics",
        "summary": "In short",
        "perspectives": "How the traditions answer",
        "common": "Where they converge",
        "reflection": "A question to sit with",
        "sources": "Referenced texts",
        "also_asked": "Also asked as",
        "other": "Other questions",
        "ask": "Ask your own question",
        "switch": "தமிழில் படிக்க",
        "disclaimer": "Curated perspectives for reflection—not divine authority, "
                      "medical advice or crisis support.",
        "home_h": "Questions people bring",
        "home_p": "Each page sets the major traditions side by side on one question. "
                  "No tradition is presented as superior, and nothing here is generated "
                  "on the fly—every answer is written and reviewed by hand.",
    },
    "ta": {
        "code": "ta", "suffix": "-ta",
        "site": "பல பாதைகள்", "tag": "ஆன்மிகத் துணை",
        "topics": "தலைப்புகள்", "all": "அனைத்துத் தலைப்புகள்",
        "summary": "சுருக்கமாக",
        "perspectives": "மரபுகள் கூறுவது",
        "common": "பொதுவான தளம்",
        "reflection": "சிந்திக்க ஒரு கேள்வி",
        "sources": "மேற்கோள் நூல்கள்",
        "also_asked": "இவ்வாறும் கேட்கப்படுகிறது",
        "other": "பிற கேள்விகள்",
        "ask": "உங்கள் கேள்வியைக் கேளுங்கள்",
        "switch": "Read in English",
        "disclaimer": "சிந்தனைக்கான தொகுக்கப்பட்ட பார்வைகள்—இறை அதிகாரமோ, "
                      "மருத்துவ ஆலோசனையோ, நெருக்கடி உதவியோ அல்ல.",
        "home_h": "மக்கள் கொண்டுவரும் கேள்விகள்",
        "home_p": "ஒவ்வொரு பக்கமும் ஒரு கேள்வியில் முக்கிய மரபுகளை அருகருகே வைக்கிறது. "
                  "எந்த மரபும் உயர்ந்ததாகக் காட்டப்படவில்லை; இங்குள்ள ஒவ்வொரு பதிலும் "
                  "கையால் எழுதி பரிசீலிக்கப்பட்டது.",
    },
}


def load_kb():
    src = open(os.path.join(ROOT, "knowledge-base.js"), encoding="utf-8").read()
    body = src[src.index("["):src.rindex("]") + 1]
    body = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', body)
    return json.loads(body)


e = html.escape


def page(*, lang, title, desc, canonical, alternate, body, extra_head=""):
    L = LANGS[lang]
    other = "ta" if lang == "en" else "en"
    return f"""<!doctype html>
<html lang="{L['code']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#f6f1e7">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="{L['code']}" href="{canonical}">
<link rel="alternate" hreflang="{LANGS[other]['code']}" href="{alternate}">
<link rel="alternate" hreflang="x-default" href="{BASE}">
<meta property="og:type" content="article">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{'en_US' if lang=='en' else 'ta_IN'}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="../styles.css">
{extra_head}
</head>
<body>
<main class="shell article">
<header class="topbar">
  <a class="brand" href="../">
    <span class="brand-mark" aria-hidden="true">◌</span>
    <span><strong>{e(L['site'])}</strong><small>{e(L['tag'])}</small></span>
  </a>
  <a class="text-button lang-switch" href="{alternate}" hreflang="{LANGS[other]['code']}">{e(L['switch'])}</a>
</header>
{body}
<footer class="article-footer">
  <p class="disclaimer">{e(L['disclaimer'])}</p>
</footer>
</main>
</body>
</html>
"""


def topic_page(entry, lang, kb):
    L = LANGS[lang]
    other = "ta" if lang == "en" else "en"
    slug = entry["id"] + L["suffix"]
    canonical = f"{BASE}topics/{slug}.html"
    alternate = f"{BASE}topics/{entry['id']}{LANGS[other]['suffix']}.html"

    qs = entry["questions"].get(lang) or entry["questions"]["en"]
    headline = qs[0]
    title_txt = entry["title"].get(lang) or entry["title"]["en"]
    summary = entry["summary"].get(lang) or entry["summary"]["en"]

    persp = "".join(
        f"""<section class="tradition">
<h3>{e(p['tradition'].get(lang) or p['tradition']['en'])}</h3>
<p>{e(p['text'].get(lang) or p['text']['en'])}</p>
</section>"""
        for p in entry.get("perspectives", []))

    others = [k for k in kb if k["id"] != entry["id"]]
    links = "".join(
        f'<li><a href="{k["id"]}{L["suffix"]}.html">'
        f'{e((k["questions"].get(lang) or k["questions"]["en"])[0])}</a></li>'
        for k in others)

    alt_qs = qs[1:]
    alt_block = (f'<p class="alt-questions"><span>{e(L["also_asked"])}:</span> '
                 + " · ".join(e(q) for q in alt_qs) + "</p>") if alt_qs else ""

    sources = "".join(f"<li>{e(s)}</li>" for s in entry.get("sources", []))

    # FAQPage structured data — the answer is the real page text
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": L["code"],
        "mainEntity": [{
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": summary},
        } for q in qs],
    }
    ld = ('<script type="application/ld+json">'
          + json.dumps(faq, ensure_ascii=False) + "</script>")

    body = f"""<article>
<p class="eyebrow">{e(title_txt)}</p>
<h1>{e(headline)}</h1>
{alt_block}
<p class="lede">{e(summary)}</p>

<h2>{e(L['perspectives'])}</h2>
{persp}

<h2>{e(L['common'])}</h2>
<p>{e(entry['common'].get(lang) or entry['common']['en'])}</p>

<h2>{e(L['reflection'])}</h2>
<blockquote>{e(entry['reflection'].get(lang) or entry['reflection']['en'])}</blockquote>

<h2>{e(L['sources'])}</h2>
<ul class="sources">{sources}</ul>

<p class="cta-line"><a class="cta" href="../">{e(L['ask'])} ↗</a></p>

<nav class="related" aria-label="{e(L['other'])}">
<h2>{e(L['other'])}</h2>
<ul>{links}</ul>
</nav>
</article>"""

    return slug, page(lang=lang, title=f"{headline} — {L['site']}",
                      desc=summary[:155], canonical=canonical,
                      alternate=alternate, body=body, extra_head=ld)


def index_page(kb, lang):
    L = LANGS[lang]
    other = "ta" if lang == "en" else "en"
    slug = "index" + L["suffix"]
    canonical = f"{BASE}topics/{slug}.html"
    alternate = f"{BASE}topics/index{LANGS[other]['suffix']}.html"

    items = "".join(
        f"""<li><a href="{k['id']}{L['suffix']}.html">
<strong>{e((k['questions'].get(lang) or k['questions']['en'])[0])}</strong>
<span>{e((k['summary'].get(lang) or k['summary']['en'])[:120])}…</span></a></li>"""
        for k in kb)

    body = f"""<article>
<h1>{e(L['home_h'])}</h1>
<p class="lede">{e(L['home_p'])}</p>
<ul class="topic-list">{items}</ul>
<p class="cta-line"><a class="cta" href="../">{e(L['ask'])} ↗</a></p>
</article>"""

    return slug, page(lang=lang, title=f"{L['topics']} — {L['site']}",
                      desc=L["home_p"][:155], canonical=canonical,
                      alternate=alternate, body=body)


def main():
    kb = load_kb()
    out = os.path.join(ROOT, "topics")
    os.makedirs(out, exist_ok=True)
    urls = []

    for lang in ("en", "ta"):
        slug, h = index_page(kb, lang)
        open(os.path.join(out, slug + ".html"), "w", encoding="utf-8").write(h)
        urls.append(f"topics/{slug}.html")
        for entry in kb:
            slug, h = topic_page(entry, lang, kb)
            open(os.path.join(out, slug + ".html"), "w", encoding="utf-8").write(h)
            urls.append(f"topics/{slug}.html")

    # sitemap with hreflang pairs
    def alt_of(u):
        n = os.path.basename(u)[:-5]
        return f"topics/{n[:-3]}.html" if n.endswith("-ta") else f"topics/{n}-ta.html"

    entries = [f"""  <url>
    <loc>{BASE}</loc><lastmod>{TODAY}</lastmod><priority>1.0</priority>
  </url>"""]
    for u in urls:
        entries.append(f"""  <url>
    <loc>{BASE}{u}</loc>
    <lastmod>{TODAY}</lastmod>
    <xhtml:link rel="alternate" hreflang="{'ta' if u.endswith('-ta.html') else 'en'}" href="{BASE}{u}"/>
    <xhtml:link rel="alternate" hreflang="{'en' if u.endswith('-ta.html') else 'ta'}" href="{BASE}{alt_of(u)}"/>
    <priority>0.8</priority>
  </url>""")

    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
               + "\n".join(entries) + "\n</urlset>\n")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)

    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")

    print(f"{len(urls)} pages written to topics/")
    print("sitemap.xml and robots.txt written")


if __name__ == "__main__":
    main()
