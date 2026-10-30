# Claude スキル（このリポジトリで動く Claude Code 用）

このフォルダのスキルは、fairtoreca リポジトリを開いた Claude Code（クラウドのセッションを含む）で自動的に読み込まれる。

| スキル | 出どころ | ライセンス | 用途 |
| --- | --- | --- | --- |
| `ig-*`（13個） | [Jakeschincariol/instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill) | MIT（`LICENSE-instagram-agent-skill`） | リール台本、フック、キャプション、カルーセル、ストーリー、プロフィール採点、週の計画、コメント・返信・DM、AIっぽさ消し、使い回し、振り返り |
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Apache 2.0（`impeccable/LICENSE`） | fairtoreca.com などの見た目・UIの改善とレビュー |
| `find-skills` | [vercel-labs/skills](https://github.com/vercel-labs/skills) | MIT（`find-skills/LICENSE`） | 必要なスキルを skills.sh から探す |

## 元からの変更点

- `ig-*` の保存先を `~/.claude/instagram/` から `/mnt/project-files/instagram/` に変えた。クラウドのセッションは毎回消えるので、voice.md・swipe.md・log.md・plan.md をプロジェクトの共有フォルダに残すため。
- `ig-*` の Python ツール（hookscore.py、humanize.py など）は英語の文章向けに作られている。日本語の台本では点数があてにならないので、フック26種やプロフィール採点表などの「型」として使う。
