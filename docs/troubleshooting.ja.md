# トラブルシューティング

## 端末が見つからない

- Android：`adb devices` で接続と USB デバッグの許可を確認し、`uv run enma setup` を実行する。
- iOS：ペアリング、USB 接続、frida-server の稼働を確認する。`setup` は Android 専用。
- 共通：`uv run frida-ps -Uai` で接続を確認し、ホストとサーバーの Frida バージョンを合わせる。
- TCP：`--host HOST:PORT` を使う。端末 ID の `-s` と同時には指定できない。

## アプリにアタッチできない

`uv run enma list` で識別子を確認してからアプリを起動します。
停止中なら `--spawn`、手動起動を待つなら `--watch` を使ってください。
数字のターゲットは PID として扱います。Gadget では一覧に表示されたプロセス名を指定します。

## OS を判定できない／エージェントが非対応と言われる

Gadget 等で OS 情報が取得できない場合だけ `--platform android` または `--platform ios` を指定します。
`dex`、`jni`、`http` 等の Android エージェントは iOS では実行できません。
iOS の通信には `ios_http` を指定してください。全体は [対応範囲](platforms.md) を参照してください。

## 出力が少ない／JSON が生成されない

エージェントを読み込んだ後、対象アプリで通信やファイルアクセス等の操作を行ってください。
イベントがない種類の JSON は生成されない場合があります。
多くのエージェントは定期保存を行います。Ctrl+C／`--timeout` は終了前に保存を試みますが、
クラッシュやプロセス強制終了では未保存の内容を回収できません。
iOS の `ios_http` は NSURLSession のタスク作成を観測します。通信本文やレスポンスは取得しません。

## report.json が見つからない

同じディレクトリに対して、先に解析を実行します。

```bash
uv run enma analyze ./dump
uv run enma report ./dump
```

`jadx` 等がない場合、該当の解析だけがスキップされます。
空の収集ディレクトリでも HTML は生成できますが、収集済みのセクションは表示されません。

## 公開ドキュメントが404になる

現在のURLは [https://qusamulab.github.io/enma/](https://qusamulab.github.io/enma/) です。
旧 `ykus4.github.io` のブックマークは更新してください。

管理者は GitHub の **Actions → Deploy documentation** と **Settings → Pages** を確認します。
公開元は GitHub Actions です。ビルドの成功だけではサイトは公開されず、Pages のデプロイ成功が必要です。
ローカルでは `uv sync --group docs` と `uv run mkdocs serve` で閲覧できます。

## ドキュメントの言語を切り替える

ヘッダーの言語メニューで English／日本語を選択します。
英語はサイトのルート、日本語は `/ja/` で表示します。
切り替え先でも同じページを開きます。ローカルの `mkdocs serve` でも両言語を確認できます。
