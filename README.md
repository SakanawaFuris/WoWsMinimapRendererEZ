# WoWs Minimap Renderer EZ

World of Warshipsのリプレイファイルからミニマップ動画を生成するツールです。

## 必要要件

- Windows 10/11 (64bit)
- インターネット接続（自動更新チェックのため）

## 使い方

### インストール

1. [Releases](../../releases) から最新の `WoWsMinimapRenderer-vX.X.X-windows.zip` をダウンロード
2. 任意のフォルダに展開
3. `WoWsMinimapRenderer.exe` をダブルクリックで起動

### 動画の生成

1. アプリケーションが起動すると、自動的にブラウザが開きます
2. 「ファイルを選択」ボタンをクリック
3. `.wowsreplay` ファイルを選択
4. 「動画生成を開始」ボタンをクリック
5. 処理が完了すると動画プレイヤーが表示されます
6. 「ダウンロード」ボタンで動画を保存できます

### リプレイファイルの場所

World of Warshipsのリプレイファイルは通常、以下の場所に保存されています：

```
C:\Games\World_of_Warships\replays\
```

## 機能

- リプレイファイルから動画を自動生成
- リアルタイム進捗表示
- Wargaming風のダークテーマUI
- ブラウザベースのインターフェース
- 生成した動画のダウンロード機能
- ゲームバージョン対応状況をステータスバーで常時表示・新バージョン対応があれば通知して手動更新

## 生成される動画

- **フォーマット**: MP4
- **保存場所**: `videos/` フォルダ（exeと同じ場所）
- **ファイル名**: `replay_[タイムスタンプ].mp4`

## Linux運用（上級者向け）

`requirements_linux.txt` を使用してPythonから直接実行できます。
リバースプロキシ経由で運用する場合は `MINIMAP_SUBPATH` 環境変数でサブパスを設定してください。

```bash
MINIMAP_SUBPATH=/apps/minimap python app.py
```

systemdサービスファイルのサンプルとして `minimap-renderer.service` を同梱しています。

## トラブルシューティング

### ブラウザが自動で開かない

手動で以下のURLにアクセスしてください：
```
http://localhost:5000
```

### ポート5000が使用中のエラー

他のアプリケーションがポート5000を使用している可能性があります。
該当アプリケーションを終了してから再度実行してください。

### 動画生成に失敗する

- リプレイファイルが破損していないか確認してください
- 対応しているのは現行バージョンのリプレイです。古いバージョンのリプレイは互換性がない場合があります

## 注意事項

- 初回起動時は依存ファイルの読み込みに時間がかかる場合があります
- リプレイファイルの長さによって、処理時間は数分かかる場合があります
- アプリケーション実行中はコンソールウィンドウを閉じないでください

## ライセンス

本ソフトウェアには [WoWs-Builder-Team/minimap_renderer](https://github.com/WoWs-Builder-Team/minimap_renderer)（GNU Affero General Public License v3.0）のコードが含まれています。
そのため、本ソフトウェア全体も **GNU Affero General Public License v3.0 (AGPL-3.0)** の下で配布されます。

ライセンス全文: https://www.gnu.org/licenses/agpl-3.0.html

## クレジット

- [minimap_renderer](https://github.com/WoWs-Builder-Team/minimap_renderer) (AGPL-3.0): リプレイ解析・動画生成エンジン
- [Flask](https://flask.palletsprojects.com/): Webフレームワーク
- [Socket.IO](https://socket.io/): リアルタイム通信

---

**World of Warships** は Wargaming の登録商標です。
このツールは非公式ツールであり、Wargaming との関連はありません。
