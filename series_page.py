# 商品ごとのまとめページ docs/s/<key>.html を書き出す（build.py から呼ぶ）
import os, html
from datetime import datetime, timedelta, timezone
JST = timezone(timedelta(hours=9))
GAME = {"pokemon": "ポケカ", "onepiece": "ワンピカ", "dragonball": "ドラゴンボール"}
COLOR = {"pokemon": "#e8b100", "onepiece": "#d02b39", "dragonball": "#ec6a12"}
METHOD = {"online": "Web抽選", "app": "アプリ", "store": "店頭", "sns": "SNS", "invite": "招待制", "order": "受注"}
WD = "月火水木金土日"
e = lambda t: html.escape(str(t or ""), quote=True)

def when(iso):
    if not iso: return "未定"
    d = datetime.fromisoformat(iso).astimezone(JST)
    return f"{d.month}/{d.day}（{WD[d.weekday()]}）{d:%H:%M}"

def status(r, now):
    s = datetime.fromisoformat(r["start"]) if r.get("start") else None
    t = datetime.fromisoformat(r["end"]) if r.get("end") else None
    if t and t < now: return "done"
    if (s and s > now) or (not s and r.get("upcoming")): return "soon"
    return "open"

CSS = """:root{--bg:#f5f6f8;--surface:#fff;--ink:#10131c;--muted:#646b7a;--line:#e3e6ec;--accent:#3346d3;--hot:#d23a2f}
@media (prefers-color-scheme:dark){:root{--bg:#0c0e14;--surface:#141822;--ink:#eef0f5;--muted:#a0a7b6;--line:#232836;--accent:#93a2ff;--hot:#ff7a6e;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:"Hiragino Sans","Yu Gothic","Noto Sans JP",sans-serif;line-height:1.7;-webkit-font-smoothing:antialiased}
main{max-width:760px;margin:0 auto;padding:32px 16px 72px}a{color:inherit}
h1{font-size:24px;line-height:1.4;margin:8px 0 8px}h2{font-size:17px;margin:36px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.lead{color:var(--muted);font-size:14.5px;margin:0}
.row{display:flex;gap:12px;align-items:center;background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--c);border-radius:10px;padding:12px 14px;margin:8px 0}
.row .b{flex:1;min-width:0}.shop{font-weight:700}.prod{font-size:13.5px}.meta{font-size:12.5px;color:var(--muted)}
.dl{font-weight:700;color:var(--hot)}
.go{flex:none;font-size:13px;font-weight:700;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:6px 12px;white-space:nowrap}
.go:hover{border-color:var(--accent);color:var(--accent)}.none{color:var(--muted)}
.done{opacity:.6}
.box{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.box p{margin:0 0 8px;font-size:14px;color:var(--muted)}.box a{color:var(--accent);font-weight:700;text-decoration:none}
.box ul{margin:0;padding-left:18px;font-size:14px}
.pr{font-size:10px;font-weight:700;border:1px solid currentColor;border-radius:4px;padding:0 4px;margin-right:6px;color:var(--muted)}
.others{display:flex;flex-wrap:wrap;gap:8px;padding:0;list-style:none}.others a{display:inline-block;font-size:13px;border:1px solid var(--line);border-radius:999px;padding:4px 12px;text-decoration:none}
footer{margin-top:40px;font-size:12px;color:var(--muted)}footer a{margin-right:12px}
@media (max-width:520px){.row{flex-direction:column;align-items:stretch}.go{text-align:center}}"""

def row(r, now, st):
    url = r.get("url")
    res = f"　発表 {e(r['result'])}" if r.get("result") else ""
    dl = f'<span class="dl">締切 {when(r.get("end"))}</span>' if st == "open" else (f"開始 {when(r.get('start'))}" if st == "soon" else f"終了 {when(r.get('end'))}")
    go = f'<a class="go" href="{e(url)}" target="_blank" rel="noopener">公式で応募 ↗</a>' if url and st != "done" else ('<span class="go none">店頭・SNSで</span>' if st != "done" else "")
    return (f'<div class="row{" done" if st == "done" else ""}" style="--c:{COLOR.get(r["game"], "#9aa0ad")}"><div class="b">'
            f'<div class="shop">{e(r.get("shop"))}<span class="meta">　{e(METHOD.get(r.get("method"), r.get("method")))}</span></div>'
            f'<div class="prod">{e(r.get("product"))}</div>'
            f'<div class="meta">{dl}　期間 {when(r.get("start"))} 〜 {when(r.get("end"))}{res}{"　/　" + e(r["note"]) if r.get("note") else ""}</div>'
            f'</div>{go}</div>')

def page(sr, all_series, data, partners, icons, now):
    groups = {"open": [], "soon": [], "done": []}
    for r in sr["rows"]: groups[status(r, now)].append(r)
    far = datetime(2100, 1, 1, tzinfo=JST)
    groups["open"].sort(key=lambda r: datetime.fromisoformat(r["end"]) if r.get("end") else far)
    groups["soon"].sort(key=lambda r: datetime.fromisoformat(r["start"]) if r.get("start") else far)
    groups["done"].sort(key=lambda r: r.get("end") or "", reverse=True)
    upd = datetime.fromisoformat(data["updatedAt"]).astimezone(JST) if data.get("updatedAt") else now
    n_open = len(groups["open"])
    title = f'{sr["name"]}の抽選・予約まとめ（締切順・毎朝更新） | フェアトレカ'
    desc = f'{sr["full"]}の抽選販売を締切順にまとめています。受付中{n_open}件。{upd.month}/{upd.day}更新。応募は各ショップの公式ページから。'
    canon = f'https://fairtoreca.com/s/{sr["key"]}.html'
    sec = ""
    for key, h in (("open", "受付中の抽選"), ("soon", "これから始まる抽選"), ("done", "締切済み（直近7日）")):
        if groups[key]:
            sec += f'<h2>{h}（{len(groups[key])}件）</h2>' + "".join(row(r, now, key) for r in groups[key])
    if not (groups["open"] or groups["soon"]):
        sec = '<p class="lead">いま受付中の抽選はありません。新しい抽選が出たら毎朝ここに追加します。</p>' + sec
    shops = [p for p in partners if "通販" in p.get("name", "") and p.get("url")]
    plinks = "".join(f'<li><a href="{e(p["url"])}" target="_blank" rel="noopener sponsored">{e(p["name"])} ↗</a>　{e(p.get("why", ""))}</li>' for p in shops)
    single = (f'<h2>外れたら：シングルで必要なカードだけ</h2><div class="box"><p>抽選に外れても、欲しいカードは1枚ずつそろえられます。BOXを高い値段で買うより、使うカードだけ探すのがおすすめ。</p>'
              f'<p><span class="pr">PR</span><a href="{e(sr["single_url"])}" target="_blank" rel="noopener sponsored">楽天で「{e(sr["name"])}」のシングルを探す ↗</a></p>'
              + (f'<ul>{plinks}</ul>' if plinks else "") + '</div>')
    others = "".join(f'<li><a href="{o["key"]}.html">{e(o["name"])}（{len(o["rows"])}件）</a></li>' for o in all_series if o is not sr)
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{icons}
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}"><meta property="og:title" content="{e(sr['name'])}の抽選まとめ | フェアトレカ"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="article"><meta property="og:url" content="{canon}">
<style>{CSS}</style></head><body><main>
<p><a href="/">← フェアトレカ（全部の抽選）</a></p>
<h1>{e(sr['name'])}の抽選・予約まとめ</h1>
<p class="lead">{e(sr['full'])}の抽選販売を、ショップ横断で締切順に並べています。受付中 {n_open}件／{upd.month}/{upd.day} {upd:%H:%M} 更新。応募は必ず各ショップの公式ページから、1人1口で。</p>
{sec}
{single}
<h2>ほかの商品の抽選まとめ</h2><ul class="others"><li><a href="/">すべての抽選</a></li>{others}</ul>
<footer><p>当サイトはアフィリエイト広告（PR）を利用しています。非公式のまとめなので、応募前に必ず各ショップの公式ページで条件と期間を確認してください。</p>
<a href="/about.html">運営者情報・プライバシーポリシー</a><a href="https://x.com/popoTCG" target="_blank" rel="noopener">X @popoTCG</a><a href="https://www.threads.net/@popo.hreads" target="_blank" rel="noopener">Threads</a></footer>
</main></body></html>
"""

def write_all(series, data, partners, outdir, icons):
    os.makedirs(outdir, exist_ok=True)
    now = datetime.now(JST)
    keep = set()
    for sr in series:
        fn = f'{sr["key"]}.html'; keep.add(fn)
        open(os.path.join(outdir, fn), "w").write(page(sr, series, data, partners, icons, now))
    for fn in os.listdir(outdir):  # 抽選がなくなった商品のページは消す
        if fn.endswith(".html") and fn not in keep: os.remove(os.path.join(outdir, fn))
