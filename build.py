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
payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
tpl = open(P("template.html")).read().replace("__DATA__", payload)

open(P("toreka-chusen.html"), "w").write(tpl.replace("<!--SITE_LINKS-->", ""))

site_url = open(P("docs", "CNAME")).read().strip() if os.path.exists(P("docs", "CNAME")) else ""
head, body = tpl.split('<div class="wrap">', 1)
og = f'<meta property="og:title" content="フェアトレカ"><meta property="og:description" content="ポケカ・ワンピースカード・ドラゴンボールの抽選を締切順にまとめて毎朝更新。"><meta property="og:type" content="website">' + (f'<meta property="og:url" content="https://{site_url}/"><link rel="canonical" href="https://{site_url}/">' if site_url else "")
html = ('<!doctype html>\n<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        + og + head + '</head><body style="margin:0">\n<div class="wrap">' + body
        .replace("<!--SITE_LINKS-->", '<span class="links"><a href="about.html">運営者情報・プライバシーポリシー</a><a href="https://calendar.google.com/calendar/r?cid=webcal://fairtoreca.com/calendar.ics" target="_blank" rel="noopener">締切をGoogleカレンダーに追加</a><a href="calendar.ics">カレンダー（iPhoneなど）</a><a href="oripa.html">オリパについて（18歳以上）</a></span>') + "\n</body></html>\n")
os.makedirs(P("docs"), exist_ok=True)
open(P("docs", "index.html"), "w").write(html)
shutil.copy(P("about.html"), P("docs", "about.html"))
shutil.copy(P("oripa.html"), P("docs", "oripa.html"))
open(P("docs", "robots.txt"), "w").write("User-agent: *\nAllow: /\n" + (f"Sitemap: https://{site_url}/sitemap.xml\n" if site_url else ""))
if site_url:
    open(P("docs", "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://{site_url}/</loc><lastmod>{data.get("updatedAt","")[:10]}</lastmod></url><url><loc>https://{site_url}/about.html</loc></url><url><loc>https://{site_url}/oripa.html</loc></url></urlset>\n')
print("built", len(data["lotteries"]), "lotteries;", "site:", site_url or "(no domain yet)")

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
