# Usage: python3 build.py
#  -> toreka-chusen.html  (claude.ai artifact version)
#  -> docs/  (fairtoreca.com。GitHub Pages が main ブランチの docs/ を公開する)
import json, os, shutil
here = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(here, *a)
data = json.load(open(P("lotteries.json")))
aff = json.load(open(P("affiliate.json")))
data["partners"] = aff.get("partners", [])
data["ads"] = aff.get("ads", False)
data["amazon"] = aff.get("amazon", False)
perks = aff.get("perks", {})
for r in data["lotteries"]:
    if r.get("id") in perks: r["perk"] = perks[r["id"]]

# 商品ごとのまとめ（series.json）と「外れたらシングルで」リンク
from urllib.parse import quote
RAKUTEN_ID = "58588721.c41e33b2.58588722.02a243f1"
def rakuten_search(kw):
    return f"https://hb.afl.rakuten.co.jp/ichiba/{RAKUTEN_ID}/?pc=" + quote(f"https://search.rakuten.co.jp/search/mall/{quote(kw)}/", safe="")
SERIES = json.load(open(P("series.json")))["series"] if os.path.exists(P("series.json")) else []
for sr in SERIES:
    sr["rows"] = [r for r in data["lotteries"] if r.get("game") == sr["game"] and any(m in r.get("product", "") for m in sr["match"])]
    sr["single_url"] = rakuten_search(sr["single"])
for r in data["lotteries"]:
    sr = next((sr for sr in SERIES if r in sr["rows"]), None)
    if sr:
        r["single"] = {"name": sr["name"], "url": sr["single_url"], "page": f"https://fairtoreca.com/s/{sr['key']}.html"}
payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
tpl = open(P("template.html")).read().replace("__DATA__", payload)
NAV = [sr for sr in SERIES if sr["rows"]]
if NAV:
    nav = '<nav class="series" aria-labelledby="series-h"><div class="gh"><h2 id="series-h">商品別の抽選まとめ</h2><span class="sub">同じ商品の抽選をショップ横断で</span></div><div class="slist">' + "".join(
        f'<a href="https://fairtoreca.com/s/{sr["key"]}.html" style="--c:var(--{ {"pokemon":"pk","onepiece":"op","dragonball":"db"}[sr["game"]] })"><b>{sr["name"]}</b><span>{len(sr["rows"])}件</span></a>' for sr in NAV) + '</div></nav>\n\n  '
    tpl = tpl.replace('<section class="follow"', nav + '<section class="follow"', 1)

open(P("toreka-chusen.html"), "w").write(tpl.replace("<!--SITE_LINKS-->", ""))

site_url = open(P("docs", "CNAME")).read().strip() if os.path.exists(P("docs", "CNAME")) else ""
head, body = tpl.split('<div class="wrap">', 1)
ICONS = '<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><meta name="theme-color" content="#10131c">'
og = f'<meta property="og:title" content="フェアトレカ"><meta property="og:description" content="ポケカ・ワンピースカード・ドラゴンボールの抽選を締切順にまとめて毎朝更新。"><meta property="og:type" content="website">' + (f'<meta property="og:url" content="https://{site_url}/"><link rel="canonical" href="https://{site_url}/">' if site_url else "")
html = ('<!doctype html>\n<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        + ICONS + og + head + '</head><body style="margin:0">\n<div class="wrap">' + body
        .replace("<!--SITE_LINKS-->", '<span class="links"><a href="about.html">運営者情報・プライバシーポリシー</a><a href="https://calendar.google.com/calendar/r?cid=webcal://fairtoreca.com/calendar.ics" target="_blank" rel="noopener">締切をGoogleカレンダーに追加</a><a href="calendar.ics">カレンダー（iPhoneなど）</a><a href="oripa.html">オリパについて（18歳以上）</a></span>') + "\n</body></html>\n")
os.makedirs(P("docs"), exist_ok=True)
open(P("docs", "index.html"), "w").write(html)
for page in ("about.html", "oripa.html", "links.html"):
    open(P("docs", page), "w").write(open(P(page)).read().replace('<meta charset="utf-8">', '<meta charset="utf-8">' + ICONS, 1))
# ファビコン（assets/ の原本を docs/ 直下へ）
for f in os.listdir(P("assets")):
    shutil.copy(P("assets", f), P("docs", f))
open(P("docs", "robots.txt"), "w").write("User-agent: *\nAllow: /\n" + (f"Sitemap: https://{site_url}/sitemap.xml\n" if site_url else ""))
if site_url:
    smap = "".join(f'<url><loc>https://{site_url}/s/{sr["key"]}.html</loc><lastmod>{data.get("updatedAt","")[:10]}</lastmod></url>' for sr in SERIES)
    open(P("docs", "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://{site_url}/</loc><lastmod>{data.get("updatedAt","")[:10]}</lastmod></url>{smap}<url><loc>https://{site_url}/about.html</loc></url><url><loc>https://{site_url}/oripa.html</loc></url><url><loc>https://{site_url}/links.html</loc></url></urlset>\n')
import series_page
series_page.write_all(SERIES, data, aff.get("partners", []), P("docs", "s"), ICONS)
print("built", len(data["lotteries"]), "lotteries;", len(SERIES), "series pages;", "site:", site_url or "(no domain yet)")

# docs/calendar.ics : 締切の購読用カレンダー（Googleカレンダー等で「URLで追加」）
from datetime import datetime, timedelta, timezone
JST = timezone(timedelta(hours=9))
def ics_esc(t): return str(t).replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")
now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
ev = []
for r in data["lotteries"]:
    if not r.get("end"): continue
    e = datetime.fromisoformat(r["end"]).astimezone(timezone.utc)
    s = e - timedelta(minutes=30)
    desc = f"{r.get('shop','')}／{r.get('product','')}\n応募: {r.get('url') or '店頭・SNS'}\n一覧: https://fairtoreca.com"
    ev.append("\r\n".join(["BEGIN:VEVENT", f"UID:{r['id']}-end@fairtoreca.com", f"DTSTAMP:{now}",
        f"DTSTART:{s.strftime('%Y%m%dT%H%M%SZ')}", f"DTEND:{e.strftime('%Y%m%dT%H%M%SZ')}",
        f"SUMMARY:{ics_esc('締切 ' + r.get('shop','') + ' ' + r.get('product',''))}", f"DESCRIPTION:{ics_esc(desc).replace(chr(92)+chr(92)+'n', chr(92)+'n')}",
        *( [f"URL:{r['url']}"] if r.get('url') else [] ),
        "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-PT3H", "DESCRIPTION:抽選の締切が近いです", "END:VALARM", "END:VEVENT"]))
cal = "\r\n".join(["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//fairtoreca//lottery//JA","CALSCALE:GREGORIAN","X-WR-CALNAME:フェアトレカ 抽選締切","X-WR-TIMEZONE:Asia/Tokyo", *ev, "END:VCALENDAR"]) + "\r\n"
open(P("docs","calendar.ics"),"w",newline="").write(cal)
print("calendar.ics:", len(ev), "events")
