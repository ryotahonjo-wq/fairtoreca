# フェアトレカ

ポケカ・ワンピースカード・ドラゴンボールのトレカ抽選を締切順にまとめるサイト（https://fairtoreca.com）。

- `lotteries.json` 抽選データ（毎朝更新）
- `affiliate.json` PR枠と抽選ごとのPRリンク
- `template.html` トップページのデザイン、`about.html` 運営者情報、`oripa.html` オリパの注意ページ（18歳以上）
- `python3 build.py` で `docs/` を生成。GitHub Pages が `main` の `docs/` を公開する
