#!/usr/bin/env python3
"""Build docs/index.html from artifacts.json.

Usage: python3 scripts/build.py [--no-dates]
Dates come from `gh api repos/<owner>/<repo>` (pushed_at) when gh is available.
"""
import html
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
M = json.loads((ROOT / "artifacts.json").read_text())
OWNER = M["owner"]
BASE = f"https://{OWNER}.github.io"
e = html.escape


def pushed(repo):
    if "--no-dates" in sys.argv:
        return None
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{OWNER}/{repo}", "--jq", ".pushed_at"],
            capture_output=True, text=True, timeout=20,
        ).stdout.strip()
        return datetime.fromisoformat(out.replace("Z", "+00:00"))
    except Exception:
        return None


def thumb(repo, path):
    p = path.rstrip("/")
    name = repo + ("__" + p.replace(".html", "").replace("/", "__") if p else "")
    if not p or path.endswith("/"):
        name += "__index"
    return f"thumbs/{name}.jpg"


ICON = {
    "Landing": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>',
    "Animated": '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="m10 8.5 4.5 2.5-4.5 2.5z"/><path d="M8 21h8"/>',
    "Guide": '<path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H20v16H5.5A1.5 1.5 0 0 0 4 20.5z"/><path d="M4 20.5A1.5 1.5 0 0 0 5.5 22H20"/><path d="M8 7h8M8 11h6"/>',
    "Checklist": '<path d="m4 7 2 2 4-4"/><path d="m4 16 2 2 4-4"/><path d="M13 7h7M13 16h7"/>',
}
SVG = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{}</svg>'
EXT = SVG.format('<path d="M14 4h6v6"/><path d="M20 4 11 13"/><path d="M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>')
GH = SVG.format('<path d="M9 19c-4 1.5-4-2-6-2.5m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12 12 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/>')
SEARCH = SVG.format('<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>')

tags = sorted({t for c in M["collections"] for t in c["tags"]})
n_pages = sum(len(c["pages"]) for c in M["collections"])

sections = []
toc = []
for c in M["collections"]:
    repo = c["repo"]
    d = pushed(repo)
    date = f'<span class="date">Updated {d:%d %b %Y}</span>' if d else ""
    cards = []
    for p in c["pages"]:
        url = f"{BASE}/{repo}/{p['path']}"
        hay = " ".join([c["title"], p["title"], p["desc"], p["kind"], *c["tags"]]).lower()
        cards.append(f"""
      <a class="card" href="{e(url)}" target="_blank" rel="noopener" data-hay="{e(hay)}">
        <div class="shot"><img loading="lazy" src="{thumb(repo, p['path'])}" alt=""></div>
        <div class="body">
          <span class="kind k-{p['kind'].lower()}">{SVG.format(ICON[p['kind']])}{e(p['kind'])}</span>
          <h3>{e(p['title'])}</h3>
          <p>{e(p['desc'])}</p>
          <span class="url">{e(url.replace('https://', ''))}{EXT}</span>
        </div>
      </a>""")
    chips = "".join(f'<span class="tag">{e(t)}</span>' for t in c["tags"])
    sections.append(f"""
  <section class="coll" id="{repo}" data-tags="{e(' '.join(c['tags']))}">
    <div class="coll-head">
      <div>
        <h2>{e(c['title'])}</h2>
        <p>{e(c['summary'])}</p>
        <div class="meta">{chips}{date}</div>
      </div>
      <div class="links">
        <a class="btn" href="{BASE}/{repo}/" target="_blank" rel="noopener">Open site{EXT}</a>
        <a class="btn ghost" href="https://github.com/{OWNER}/{repo}" target="_blank" rel="noopener">{GH}Source</a>
      </div>
    </div>
    <div class="grid">{''.join(cards)}
    </div>
  </section>""")
    toc.append(f'<a href="#{repo}">{e(c["title"])}<b>{len(c["pages"])}</b></a>')

filters = '<button class="on" data-tag="">All</button>' + "".join(
    f'<button data-tag="{e(t)}">{e(t)}</button>' for t in tags)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Denada Korita: published artifacts</title>
<meta name="description" content="All published guides, architectures and presentations in one place.">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect x='2' y='2' width='20' height='20' rx='5' fill='%23FF3621'/%3E%3Cpath d='M7 8h10M7 12h10M7 16h6' stroke='white' stroke-width='2.2' stroke-linecap='round'/%3E%3C/svg%3E">
<style>
:root{{--navy:#0B2026;--ink:#1B3139;--ink2:#4A5F67;--muted:#6B7F86;--line:#DCE4E8;--bg:#F5F7F8;--card:#fff;--blue:#2272B4;--green:#00A972;--orange:#FFAB00;--lava:#FF3621}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;color:var(--ink);background:var(--bg)}}
a{{color:inherit;text-decoration:none}}
svg.ic{{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;flex:none}}
.wrap{{max-width:1240px;margin:0 auto;padding:0 28px}}
header{{background:var(--navy);color:#fff;border-bottom:4px solid var(--lava)}}
header .wrap{{padding-top:40px;padding-bottom:34px}}
.eyebrow{{margin:0;text-transform:uppercase;letter-spacing:.14em;font-size:12px;font-weight:700;color:var(--orange)}}
h1{{margin:6px 0 8px;font-size:36px;line-height:1.15;letter-spacing:-.01em}}
.lede{{margin:0 0 22px;color:#C9D6DB;font-size:17px;max-width:720px}}
.toc{{display:flex;flex-wrap:wrap;gap:8px}}
.toc a{{display:inline-flex;align-items:center;gap:8px;padding:7px 12px;border:1px solid rgba(255,255,255,.25);border-radius:999px;font-size:13px;font-weight:600;color:#E6EEF1}}
.toc a:hover{{border-color:#fff;color:#fff}}
.toc b{{background:rgba(255,255,255,.14);border-radius:999px;padding:0 7px;font-size:11px}}
.bar{{position:sticky;top:0;z-index:5;background:rgba(245,247,248,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}}
.bar .wrap{{display:flex;gap:14px;align-items:center;padding-top:10px;padding-bottom:10px;flex-wrap:wrap}}
.search{{display:flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);border-radius:9px;padding:6px 10px;color:var(--muted);flex:1;min-width:220px;max-width:380px}}
.search input{{all:unset;flex:1;color:var(--ink);font-size:14px}}
.seg{{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:#fff}}
.seg button{{all:unset;cursor:pointer;padding:6px 12px;font-size:13px;font-weight:600;color:var(--ink2)}}
.seg button.on{{background:var(--navy);color:#fff}}
.count{{margin-left:auto;font-size:13px;color:var(--muted)}}
main{{padding:10px 0 60px}}
.coll{{padding-top:30px;scroll-margin-top:60px}}
.coll-head{{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:14px;flex-wrap:wrap}}
.coll h2{{margin:0;font-size:22px}}
.coll-head p{{margin:2px 0 8px;color:var(--ink2)}}
.meta{{display:flex;gap:6px;align-items:center;flex-wrap:wrap}}
.tag{{font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--blue);background:#E8F1F9;border-radius:5px;padding:2px 7px}}
.date{{font-size:12px;color:var(--muted);margin-left:4px}}
.links{{display:flex;gap:8px}}
.btn{{display:inline-flex;align-items:center;gap:7px;padding:8px 13px;border-radius:9px;font-size:13px;font-weight:600;background:var(--lava);color:#fff;border:1px solid var(--lava)}}
.btn:hover{{background:#E62E1A}}
.btn.ghost{{background:#fff;color:var(--ink);border-color:var(--line)}}
.btn.ghost:hover{{border-color:var(--ink2)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:16px}}
.card{{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;transition:transform .15s,box-shadow .15s,border-color .15s}}
.card:hover{{transform:translateY(-2px);box-shadow:0 10px 24px rgba(11,32,38,.10);border-color:#B8C7CD}}
.shot{{aspect-ratio:16/10;background:#EEF2F4;border-bottom:1px solid var(--line);overflow:hidden}}
.shot img{{width:100%;height:100%;object-fit:cover;object-position:top;display:block}}
.body{{padding:12px 14px 14px;display:flex;flex-direction:column;gap:4px;flex:1}}
.kind{{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;width:max-content}}
.kind svg.ic{{width:14px;height:14px}}
.k-landing{{color:var(--ink2)}} .k-animated{{color:var(--lava)}} .k-guide{{color:var(--blue)}} .k-checklist{{color:var(--green)}}
.card h3{{margin:2px 0 0;font-size:16px;line-height:1.3}}
.card p{{margin:0;color:var(--ink2);font-size:13.5px;flex:1}}
.url{{display:flex;align-items:center;gap:5px;margin-top:8px;font-size:12px;color:var(--muted);overflow:hidden;white-space:nowrap}}
.url svg.ic{{width:13px;height:13px}}
.card:hover .url{{color:var(--blue)}}
.hide{{display:none!important}}
.empty{{padding:60px 0;text-align:center;color:var(--muted)}}
footer{{border-top:1px solid var(--line);padding:18px 0 30px;color:var(--muted);font-size:13px}}
@media (max-width:640px){{h1{{font-size:28px}}.count{{margin-left:0}}}}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <p class="eyebrow">Artifacts</p>
    <h1>Published guides, architectures and presentations</h1>
    <p class="lede">Everything published on GitHub Pages, grouped by site: {len(M['collections'])} sites, {n_pages} pages. Every card opens in a new tab.</p>
    <nav class="toc">{''.join(toc)}</nav>
  </div>
</header>
<div class="bar">
  <div class="wrap">
    <label class="search">{SEARCH}<input id="q" type="search" placeholder="Search titles and descriptions" autocomplete="off"></label>
    <div class="seg" id="tags">{filters}</div>
    <span class="count" id="count"></span>
  </div>
</div>
<main class="wrap">{''.join(sections)}
  <p class="empty hide" id="empty">No artifacts match.</p>
</main>
<footer><div class="wrap">Built from <a href="https://github.com/{OWNER}/korita-artifacts">artifacts.json</a> with scripts/build.py.</div></footer>
<script>
const q=document.getElementById('q'),cnt=document.getElementById('count'),empty=document.getElementById('empty');
let tag='';
function apply(){{
  const s=q.value.trim().toLowerCase();let n=0;
  document.querySelectorAll('.coll').forEach(c=>{{
    const tagOk=!tag||c.dataset.tags.split(' ').includes(tag);let k=0;
    c.querySelectorAll('.card').forEach(a=>{{const ok=tagOk&&(!s||a.dataset.hay.includes(s));a.classList.toggle('hide',!ok);if(ok)k++;}});
    c.classList.toggle('hide',!k);n+=k;
  }});
  cnt.textContent=n+' of {n_pages} pages';empty.classList.toggle('hide',n>0);
}}
q.addEventListener('input',apply);
document.getElementById('tags').addEventListener('click',ev=>{{
  const b=ev.target.closest('button');if(!b)return;
  document.querySelectorAll('#tags button').forEach(x=>x.classList.toggle('on',x===b));
  tag=b.dataset.tag;apply();
}});
document.addEventListener('keydown',ev=>{{if(ev.key==='/'&&document.activeElement!==q){{ev.preventDefault();q.focus();}}}});
apply();
</script>
</body>
</html>
"""
(DOCS / "index.html").write_text(page)
(DOCS / ".nojekyll").write_text("")
print(f"Wrote docs/index.html: {len(M['collections'])} collections, {n_pages} pages")
