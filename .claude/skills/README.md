# Claude スキル（このリポジトリで動く Claude Code 用）

このフォルダのスキルは、fairtoreca リポジトリを開いた Claude Code（クラウドのセッションを含む）で自動的に読み込まれる。

| スキル | 出どころ | ライセンス | 用途 |
| --- | --- | --- | --- |
| `ig-*`（13個） | [Alman-creator-uslog/instagram-agent-skill-ja](https://github.com/Alman-creator-uslog/instagram-agent-skill-ja)（[英語版](https://github.com/Jakeschincariol/instagram-agent-skill)の日本語版） | MIT（`LICENSE-instagram-agent-skill-ja`、英語版は `LICENSE-instagram-agent-skill`） | リール台本、フック、キャプション、カルーセル、ストーリー、プロフィール採点、週の計画、コメント・返信・DM、AIっぽさ消し、使い回し、振り返り |
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Apache 2.0（`impeccable/LICENSE`） | fairtoreca.com などの見た目・UIの改善とレビュー |
| `find-skills` | [vercel-labs/skills](https://github.com/vercel-labs/skills) | MIT（`find-skills/LICENSE`） | 必要なスキルを skills.sh から探す |

## 元からの変更点

- `ig-*` の保存先を `~/.claude/instagram/` から `/mnt/project-files/instagram/` に変えた。クラウドのセッションは毎回消えるので、voice.md・swipe.md・log.md・plan.md をプロジェクトの共有フォルダに残すため。
- 2026-11-02 に `ig-*` を日本語版に入れ替えた。点数の計算が日本語の文字数・読み・言い回しで測るようになっている（jp.py）。

## 2026-10-30 追加

| スキル | 出どころ | ライセンス | 用途 |
| --- | --- | --- | --- |
| Superpowers（brainstorming、writing-plans、systematic-debugging など15個） | [obra/superpowers](https://github.com/obra/superpowers) | MIT（`LICENSE-superpowers`） | 開発作業の進め方（計画→実装→確認） |
| `task-observer` | [rebelytics/one-skill-to-rule-them-all](https://github.com/rebelytics/one-skill-to-rule-them-all) | CC BY 4.0（`task-observer/LICENSE`） | 使っているスキルのつまずきを記録して、改善案を出す |

- Superpowers は元のプラグインにある「毎回の起動時に強制で読み込むフック」は入れていない。スキルとして必要なときだけ使われる。
- Task Observer の起動ルールはリポジトリ直下の `CLAUDE.md`。記録は `/mnt/project-files/task-observer/` に残る。定期ルーティンでは飛ばす。
- Claude Mem はりょうたのPCの Claude Code に入れるもので、ここには入れていない。
