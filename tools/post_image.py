#!/usr/bin/env python3
"""SNSまとめ投稿用の画像（1080x1350）を lotteries.json から作る。
使い方: python3 tools/post_image.py [YYYY-MM-DD] [出力.png]
  日付（JST、省略時は今日）の「今日締切」「明日締切」と、その日に追加された新着を載せる。
  対象がゼロなら何も作らず終了コード 2。標準出力に載せた抽選を JSON で出す（投稿文づくり用）。
"""
import html, json, os, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
WD = "月火水木金土日"
GAME = {"pokemon": ("ポケカ", "#ffd23f"), "onepiece": ("ワンピカ", "#ff6672"), "dragonball": ("DB", "#ff9447")}
METHOD = {"online": "ネット", "app": "アプリ", "store": "店頭", "sns": "SNS", "invite": "招待", "order": "受注"}

day = datetime.strptime(sys.argv[1], "%Y-%m-%d").date() if len(sys.argv) > 1 else datetime.now(JST).date()
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, f"post-{day}.png")
data = json.load(open(os.path.join(ROOT, "lotteries.json")))
perks = json.load(open(os.path.join(ROOT, "affiliate.json"))).get("perks", {})

def dt(s): return datetime.fromisoformat(s).astimezone(JST) if s else None

groups = {"今日締切": [], "明日締切": [], "新着": []}
for l in data["lotteries"]:
    end, added = dt(l.get("end")), dt(l.get("addedAt"))
    if end and end.date() == day: groups["今日締切"].append(l)
    elif end and end.date() == day + timedelta(days=1): groups["明日締切"].append(l)
    elif added and added.date() == day and not (end and end.date() < day): groups["新着"].append(l)
for g in groups.values(): g.sort(key=lambda l: l.get("end") or "9")
picked = [(k, l) for k, v in groups.items() for l in v]
if not picked:
    print("[]"); sys.exit(2)

MAX = 7
rows, n = [], 0
for k, v in groups.items():
    if not v or n >= MAX: continue
    rows.append(f'<div class="h">{k}<span>{len(v)}件</span></div>')
    for l in v:
        if n >= MAX: break
        g, c = GAME.get(l["game"], ("", "#aaa"))
        end = dt(l.get("end"))
        t = end.strftime("%-m/%-d %H:%M") if end and k == "新着" else (end.strftime("%H:%M") if end else "未定")
        rows.append(f'<div class="r"><b class="t">{t}</b><i style="background:{c}">{g}</i>'
                    f'<div class="s"><div class="shop">{html.escape(l["shop"])}<em>{METHOD.get(l["method"], "")}</em></div>'
                    f'<div class="p">{html.escape(l["product"])}</div></div></div>')
        n += 1
rest = len(picked) - n
doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}
body{{width:1080px;height:1350px;background:#10131c;color:#eef0f5;font-family:"IPAPGothic","WenQuanYi Zen Hei",sans-serif;padding:72px 72px 0;position:relative;overflow:hidden}}
.ey{{font-size:26px;letter-spacing:.2em;color:#a0a7b6}}
h1{{font-size:76px;font-weight:700;margin-top:14px;letter-spacing:.02em}}
.foil{{height:10px;width:220px;border-radius:5px;margin:26px 0 30px;background:linear-gradient(100deg,#7fd6ff,#b59cff 28%,#ff9fd2 52%,#ffe08a 76%,#8ef0c4)}}
.h{{font-size:32px;font-weight:700;margin:26px 0 12px;color:#ff7a6e;display:flex;gap:14px;align-items:baseline}}
.h span{{font-size:24px;color:#a0a7b6}}
.r{{display:flex;gap:20px;align-items:center;background:#141822;border:1px solid #232836;border-radius:18px;padding:16px 22px;margin-bottom:10px}}
.t{{font-size:34px;min-width:120px;font-variant-numeric:tabular-nums}}
i{{font-style:normal;font-size:22px;font-weight:700;color:#10131c;border-radius:8px;padding:4px 10px;white-space:nowrap}}
.s{{min-width:0;flex:1}}
.shop{{font-size:30px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.shop em{{font-style:normal;font-size:20px;color:#a0a7b6;border:1px solid #3a4152;border-radius:6px;padding:1px 8px;margin-left:12px;vertical-align:4px}}
.p{{font-size:23px;color:#a0a7b6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}}
.more{{font-size:28px;color:#a0a7b6;margin-top:14px}}
.ft{{position:absolute;left:0;right:0;bottom:0;padding:34px 72px;background:#0b0d13;display:flex;justify-content:space-between;align-items:center}}
.ft b{{font-size:40px}} .ft span{{font-size:24px;color:#a0a7b6}}
</style></head><body>
<div class="ey">FAIR TORECA ・ 抽選締切まとめ</div>
<h1>{day.month}/{day.day}（{WD[day.weekday()]}）の抽選</h1>
<div class="foil"></div>
{''.join(rows)}
{f'<div class="more">ほか {rest} 件はサイトで</div>' if rest > 0 else ''}
<div class="ft"><div><b>fairtoreca.com</b><br><span>公式から、定価で。ほしい人みんなに、買えるチャンスを。</span></div></div>
</body></html>"""
with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, "p.html"); open(p, "w").write(doc)
    shot = os.path.join(td, "s.png")
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=1080,1600", f"--screenshot={shot}", "file://" + p],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from PIL import Image
    Image.open(shot).convert("RGB").crop((0, 0, 1080, 1350)).save(out)
print(json.dumps([{"group": k, "id": l["id"], "shop": l["shop"], "product": l["product"], "method": l["method"],
                   "end": l.get("end"), "url": l.get("url"), "perk": perks.get(l["id"], {}).get("url")} for k, l in picked],
                 ensure_ascii=False, indent=1))
print("image:", out, file=sys.stderr)
