# 構成とデータの流れ

enma は、ホスト上の Python と対象アプリ内の JavaScript エージェントに分かれます。
CLI は引数の解釈と処理の振り分けを行い、端末接続とオフライン解析を分離しています。

```text
CLI
 ├─ dump / mem / ue4 → core/session → Frida → 対象アプリの JS エージェント
 │                                 ↓ メッセージ
 │                              収集ディレクトリ
 ├─ analyze → binaries / events / ue4 → report.json
 └─ report → sections / components / assets → report.html
```

## 責務の分け方

| 場所 | 責務 |
|---|---|
| `cli.py` | 引数と遅延インポート。Frida 接続や解析処理を置かない |
| `core/platforms.py` | Android／iOS の判定。Gadget 用の明示指定 |
| `core/agents.py` | エージェント名・カテゴリ・対応 OS の唯一の登録表 |
| `core/scripts.py` | Frida 17 用の Java／Objective-C ブリッジと共通 JS の組み込み |
| `core/session.py` | USB／TCP 接続、アタッチ、スクリプト読み込み、終了時の保存 |
| `dump.py` / `mem.py` / `ue4.py` | ランタイム操作の実行 |
| `frida_server.py` / `repack.py` | Android 専用のサーバー配置・APK 処理 |
| `analyze/` | ファイルから解析結果を作る。端末・Frida に依存しない |
| `report/` | 解析結果を HTML 化。CSS・JS は `assets/` に分離 |
| `agents/` | 対象プロセス内で動く JS。Python のファイルとは別の実行環境 |

依存方向は `CLI → 機能 → core` です。`core` は CLI や機能をインポートしません。
`--help`、`analyze`、`report` で Frida や UnityPy を読み込む必要はありません。

## OS の選択

1. Frida の device ID、USB、または `--host` で接続先を決める。
2. `query_system_parameters().os.id` から OS を判定する。
3. `dump` の既定エージェントを対応 OS で絞る。
4. 明示指定が OS に対応しない場合は、アタッチ前に終了する。

`--platform` は自動判定できない Gadget 等のための上書きです。
`ue4` は Android 専用です。全コマンドが両 OS で同じ機能を持つわけではありません。
詳細は [対応範囲](platforms.md) を参照してください。

## エージェントの出力

```javascript
send({ event: "log", message: "status" });
send({ event: "file", name: "output.bin" }, arrayBuffer);
send({ event: "json", name: "result.json", data: { key: "value" } });
```

ホストはログを表示し、ファイルを収集ディレクトリに保存します。
`flush()` があるエージェントは Ctrl+C／タイムアウト時にも保存を試みます。
プロセスの強制終了やクラッシュでは、未保存のイベントが失われる場合があります。

`memscan` と `mempatch` は `rpc.exports` を使い、Python から検索や読み書きを呼び出します。
この2つは `dump` の既定エージェントには含まれません。

## オフライン解析

`analyze_dump()` は解析関数を順番に実行し、存在するファイルの結果だけを `report.json` にまとめます。
UE4 の解析も `analyze/ue4.py` に分離されているため、解析のために端末へ接続しません。
任意の外部ツールが未導入の場合は、その処理をスキップします。

`generate_html()` は結果のキーに対応するセクションを描画します。
未知のキーは汎用 JSON 表示になり、CSS・JS を埋め込んだ単一の HTML ファイルを出力します。
