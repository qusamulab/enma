# 開発ガイド

## ファイル配置

```text
src/enma/
├── cli.py                 # 引数と処理の振り分け
├── core/                  # 接続、OS判定、登録表、スクリプト準備
├── dump.py / mem.py       # 共通のランタイム操作
├── ue4.py                 # Android向けUE4実行処理
├── frida_server.py        # Android向けsetup
├── repack.py              # Android APKへのGadget組み込み
├── unity.py               # オフラインAssetBundle展開
├── analyze/
│   ├── __init__.py        # analyze_dump() と解析順序
│   ├── helpers.py         # JSON・集計・外部ツール
│   ├── binaries.py        # DEX、IL2CPP、DLL、ネイティブ文字列
│   ├── events.py          # 通信・ストレージ・アプリ情報
│   └── ue4.py             # UE4のオフライン解析
├── report/
│   ├── __init__.py        # generate_html() / render_report()
│   ├── components.py      # 共通HTML部品
│   ├── sections.py        # セクション描画と登録表
│   └── assets/            # レポート用CSS・JS
└── agents/                # 対象アプリ内で実行するJS
    ├── _runtime.js        # 共通Frida API互換処理
    └── ios/               # iOS固有エージェント
```

公開エントリーポイントは `enma.analyze.analyze_dump` と
`enma.report.generate_html` / `render_report` のままです。
配置変更の理由と依存方向は [構成とデータの流れ](architecture.md) を参照してください。

## 検証

```bash
uv sync --group docs
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest
node --test tests/agents.test.cjs
uv run mkdocs build --strict
```

Python テストは実機不要です。外部ツール検索、ネットワーク、ホームディレクトリを
fixture で差し替え、ローカルの Frida キャッシュや端末へアクセスしません。
JavaScript テストは Node.js 22 以降で、Frida API を模擬してフック処理を検証します。
実機での API・OS バージョンごとの差は、別途確認が必要です。

## エージェントを追加する

1. `agents/{category}/{name}_agent.js` を作る。
2. `core/agents.py` の `_AGENTS` に名前、カテゴリ、タグ、対応 OS を登録する。
3. 出力を解析する関数を `analyze/` の該当モジュールに追加し、`_ANALYZERS` に登録する。
4. `report/sections.py` に描画処理を追加し、`_RENDERERS` に登録する。
5. [エージェント一覧](agents.md) と [対応範囲](platforms.md) の英語・日本語を更新する。
6. 模擬 API と出力を使って処理・非対応 OS の拒否・解析結果を検証する。

```python
_a("example", "ios", TAG_DUMP, platforms=(Platform.IOS,)),
```

`TAG_DUMP` は `dump` 用、`TAG_UE4` は `ue4` 用、`TAG_MEM` はメモリ操作用です。
登録表と JS ファイル、英語・日本語それぞれのドキュメントの見出しが一致することをテストで確認します。
Java／Objective-C ブリッジをエージェントへコピーせず、`core/scripts.py` に任せてください。

## ドキュメントの編集と公開

```bash
uv sync --group docs
uv run mkdocs serve
uv run mkdocs build --strict
```

設定は `mkdocs.yml`、本文は `docs/` にあります。
README は入口として短く保ち、手順は各ガイドへ集約します。
標準言語は英語です。各ページを次の2ファイルで管理します。

| ソース | 公開パス |
|---|---|
| `docs/index.md` | `/enma/` |
| `docs/index.ja.md` | `/enma/ja/` |
| `docs/platforms.md` | `/enma/platforms/` |
| `docs/platforms.ja.md` | `/enma/ja/platforms/` |

`mkdocs-static-i18n` が両言語をビルドし、Material の言語メニューを提供します。
切り替えると同じページへ移動します。ナビゲーションの翻訳は `mkdocs.yml` にあります。
ページの更新時は両言語を更新してください。
ページ間のリンクには両言語とも `platforms.md` のような相対パスを使い、`.ja` は付けません。
プラグインが表示中の言語に合わせて解決します。

`main` のドキュメント・設定変更を GitHub Actions がビルドし、GitHub Pages へ公開します。
初回はリポジトリの Pages の公開元を **GitHub Actions** に設定します。
公開先は [qusamulab.github.io/enma](https://qusamulab.github.io/enma/) です。
