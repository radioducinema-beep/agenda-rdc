from __future__ import annotations

import json, html, hashlib
from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime
from dateutil.parser import isoparse

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "events.json"
OUT = ROOT / "dist"
BASE_URL = "https://agenda.radioducinema.com"
SITE_NAME = "Agenda cinéma — La Radio du Cinéma"

def load_events():
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    required = {"title","start","end","city","country","summary","source_url","image_url"}
    seen = set()
    events = []
    for e in raw:
        missing = required - e.keys()
        if missing:
            raise ValueError(f"Event missing fields {sorted(missing)}: {e}")
        key = (e["title"].strip().lower(), e["start"][:10], e["city"].strip().lower())
        if key in seen:
            raise ValueError(f"Duplicate event: {e['title']} / {e['start']} / {e['city']}")
        seen.add(key)
        e["id"] = e.get("id") or hashlib.sha1("|".join(key).encode()).hexdigest()[:12]
        events.append(e)
    return sorted(events, key=lambda x: isoparse(x["start"]))

def esc(v): return html.escape(str(v), quote=True)

def event_card(e):
    start = isoparse(e["start"]).strftime("%d/%m/%Y")
    end = isoparse(e["end"]).strftime("%d/%m/%Y")
    dates = start if start == end else f"{start} → {end}"
    return f"""<article class="card" id="{esc(e['id'])}">
<a class="image" href="{esc(e['source_url'])}" target="_blank" rel="noopener"><img src="{esc(e['image_url'])}" alt="{esc(e['title'])}" loading="lazy"></a>
<div class="body"><p class="meta">{dates} · {esc(e['city'])}, {esc(e['country'])}</p>
<h2>{esc(e['title'])}</h2><p>{esc(e['summary'])}</p>
<p><a href="{esc(e['source_url'])}" target="_blank" rel="noopener">Source officielle ↗</a></p></div></article>"""

def build_html(events):
    now = datetime.now(timezone.utc)
    cards = "\n".join(event_card(e) for e in events) or '<p class="empty">Aucun événement publié pour le moment.</p>'
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_NAME}</title>
<meta name="description" content="Festivals et événements cinéma et séries sélectionnés et vérifiés par La Radio du Cinéma.">
<link rel="alternate" type="application/rss+xml" title="Agenda RDC" href="/rss.xml">
<style>
:root{{--bg:#090909;--fg:#f5f5f5;--muted:#aaa;--line:#252525;--accent:#fff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font-family:Arial,Helvetica,sans-serif}}
main{{max-width:1100px;margin:auto;padding:32px 20px}}header{{padding:28px 0;border-bottom:1px solid var(--line);margin-bottom:28px}}
h1{{font-size:clamp(2rem,5vw,4rem);margin:0 0 8px}}.sub,.meta{{color:var(--muted)}}.grid{{display:grid;gap:22px}}
.card{{display:grid;grid-template-columns:minmax(220px,320px) 1fr;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#111}}
.image{{min-height:200px;background:#181818}}.image img{{width:100%;height:100%;object-fit:cover;display:block}}
.body{{padding:22px}}h2{{margin:6px 0 14px;font-size:1.5rem}}a{{color:var(--accent)}}footer{{margin-top:36px;color:var(--muted);font-size:.9rem}}
@media(max-width:700px){{.card{{grid-template-columns:1fr}}}}
</style></head><body><main><header><h1>Agenda cinéma</h1>
<p class="sub">Festivals et événements cinéma & séries — La Radio du Cinéma</p></header>
<section class="grid">{cards}</section>
<footer>Dernière génération : {now.astimezone().strftime('%d/%m/%Y %H:%M UTC')} · <a href="/rss.xml">Flux RSS</a></footer>
</main></body></html>"""

def build_rss(events):
    now = format_datetime(datetime.now(timezone.utc))
    items = []
    for e in events:
        guid = f"{BASE_URL}/#{e['id']}"
        items.append(f"""<item><title>{esc(e['title'])}</title><link>{esc(e['source_url'])}</link>
<guid isPermaLink="false">{esc(guid)}</guid><description>{esc(e['summary'])}</description>
<pubDate>{format_datetime(isoparse(e['start']).astimezone(timezone.utc))}</pubDate></item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>
<title>{SITE_NAME}</title><link>{BASE_URL}</link><description>Agenda cinéma et séries de La Radio du Cinéma</description>
<language>fr-fr</language><lastBuildDate>{now}</lastBuildDate>{''.join(items)}</channel></rss>"""

def build_sitemap(events):
    urls = [BASE_URL + "/"] + [f"{BASE_URL}/#{e['id']}" for e in events]
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{esc(u)}</loc></url>" for u in urls) + "</urlset>"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events = load_events()
    (OUT/"index.html").write_text(build_html(events), encoding="utf-8")
    (OUT/"rss.xml").write_text(build_rss(events), encoding="utf-8")
    (OUT/"sitemap.xml").write_text(build_sitemap(events), encoding="utf-8")
    (OUT/"CNAME").write_text("agenda.radioducinema.com\n", encoding="utf-8")
    print(f"Generated {len(events)} events")

if __name__ == "__main__":
    main()
