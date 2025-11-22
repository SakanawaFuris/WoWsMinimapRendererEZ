# WoWs Minimap Renderer - ポータブルGUIアプリ化プロジェクト

## プロジェクト概要
World of Warshipsのリプレイファイルから、ミニマップの動画を生成するツールを、一般ユーザー向けのWindows用ポータブルアプリケーションとして実装する。

## 要件定義（確定版）

### 対象環境
- **対象OS**: Windows 10/11
- **対象ユーザー**: プログラミング経験のない一般ゲームプレイヤー
- **配布形式**: ポータブル版（zip解凍→exe実行）

### 機能要件

#### 必須機能
1. **ファイル選択**: ブラウザUI上でリプレイファイル（.wowsreplay）を選択
2. **動画生成**: 選択したファイルから動画を生成
3. **進捗表示**: 処理中の進捗をゲージ（プログレスバー）で表示
4. **動画再生**: 生成した動画をブラウザ上で再生
5. **ダウンロード**: 生成した動画をダウンロード
6. **連続処理**: 終了後も画面を閉じず、別ファイルを選択して再度生成可能

#### 非機能要件
- 複数ファイルの一括処理: 不要
- 解像度/フレームレート設定: 不要
- 過去の生成履歴表示: 不要

### ユーザーフロー

```
1. minimap_renderer.exeをダブルクリック
   ↓
2. 自動的にブラウザが開く (http://localhost:5000)
   ↓
3. 「ファイルを選択」ボタンでリプレイファイルを選択
   ↓
4. 「動画生成」ボタンをクリック
   ↓
5. 進捗ゲージで処理状況を確認
   ↓
6. 生成完了
   ├─ 「再生」ボタンでブラウザ上で視聴
   └─ 「ダウンロード」ボタンでローカルに保存
   ↓
7. 「別のファイルを処理」ボタンで手順3に戻る
```

## 技術スタック

### バックエンド
- **Python 3.10**: 元のminimap_rendererの要件に合わせる
- **Flask 3.x**: 軽量Webフレームワーク
- **Flask-SocketIO**: リアルタイム進捗通知用
- **minimap_renderer**: 既存のレンダリングエンジン（そのまま活用）

### フロントエンド
- **HTML5/CSS3**: シンプルなUI
- **JavaScript (Vanilla)**: 軽量化のためフレームワークなし
- **Socket.IO Client**: リアルタイム進捗受信用

### パッケージング
- **PyInstaller**: exe化ツール
- **--onefile**: 単一exe生成（または --onedir）
- **--noconsole**: コンソールウィンドウ非表示

## アーキテクチャ

### ディレクトリ構成

```
minimap_renderer_gui/
├── app.py                    # Flaskアプリケーションのメインファイル
├── requirements.txt          # Python依存パッケージリスト
├── build_exe.bat            # PyInstallerビルドスクリプト
├── README.md                # ユーザー向けマニュアル
├── static/                  # 静的ファイル
│   ├── css/
│   │   └── style.css        # スタイルシート
│   ├── js/
│   │   └── app.js           # フロントエンドロジック
│   └── videos/              # 生成された動画の一時保存先
└── templates/               # HTMLテンプレート
    └── index.html           # メインUI画面
```

### データフロー

```
ユーザー → ブラウザUI → Flask (app.py) → minimap_renderer → 動画生成
                ↑                ↓
                └── SocketIO (進捗通知)
```

## 開発フェーズ

### Phase 1: 基本機能実装（1-2日）
- [ ] Flaskプロジェクトのセットアップ
- [ ] 基本的なUI（HTML/CSS）作成
- [ ] ファイルアップロード機能
- [ ] minimap_rendererとの連携
- [ ] 動画生成機能
- [ ] ダウンロード機能

### Phase 2: UI改善（1日）
- [ ] SocketIOでリアルタイム進捗表示
- [ ] 動画プレビュー（HTML5 video）
- [ ] エラーハンドリング（ユーザーフレンドリーなメッセージ）
- [ ] 連続処理機能（リセット機能）

### Phase 3: パッケージング＆テスト（1日）
- [ ] PyInstallerスペックファイル作成
- [ ] exe化テスト
- [ ] 複数のWindows環境でテスト
- [ ] ユーザーマニュアル作成
- [ ] zip配布パッケージ作成

## Git管理方針

### リポジトリ構造
- **メインブランチ**: `main` - 安定版
- **開発ブランチ**: `develop` - 開発中のコード
- **機能ブランチ**: `feature/機能名` - 各機能の開発

### コミットルール
- コミットメッセージは日本語でOK
- プレフィックスを使用:
  - `feat:` 新機能
  - `fix:` バグ修正
  - `docs:` ドキュメント
  - `refactor:` リファクタリング
  - `test:` テスト

### 推奨ワークフロー
1. 機能ごとにブランチを作成
2. 開発・コミット
3. developにマージ
4. 動作確認後、mainにマージ

## 開発環境セットアップ

### 必要なもの
- Windows 10/11
- Python 3.10（公式サイトからインストール）
- Git for Windows
- テキストエディタ（VS Code推奨）
- Claude Code（オプション）

### セットアップ手順
```bash
# 1. プロジェクトディレクトリ作成
mkdir minimap_renderer_gui
cd minimap_renderer_gui

# 2. Git初期化
git init
git branch -M main

# 3. Python仮想環境作成
python -m venv venv
venv\Scripts\activate

# 4. 依存パッケージインストール
pip install flask flask-socketio python-socketio
pip install --upgrade --force-reinstall git+https://github.com/WoWs-Builder-Team/minimap_renderer.git
pip install pyinstaller

# 5. requirements.txt生成
pip freeze > requirements.txt
```

## テスト計画

### 機能テスト
- [ ] ファイル選択が正常に動作する
- [ ] 動画生成が完了する
- [ ] 進捗表示がリアルタイムで更新される
- [ ] 生成した動画が再生できる
- [ ] ダウンロードが正常に動作する
- [ ] 連続処理が可能

### 互換性テスト
- [ ] Windows 10で動作
- [ ] Windows 11で動作
- [ ] Chrome/Edge/Firefoxで動作

### エラーハンドリングテスト
- [ ] 不正なファイルを選択した場合
- [ ] ディスク容量不足の場合
- [ ] 処理中にキャンセルした場合

## 既知の技術的課題と解決策

### 課題1: PyInstallerでのパッケージング
- **問題**: minimap_rendererの依存関係が複雑
- **解決策**: `--hidden-import`オプションで必要なモジュールを明示的に含める

### 課題2: ポート競合
- **問題**: 5000ポートが既に使用されている場合がある
- **解決策**: 空きポートを自動検索する機能を実装

### 課題3: ブラウザの自動起動
- **問題**: デフォルトブラウザがない環境
- **解決策**: `webbrowser`モジュールでフォールバック処理

## 参考リソース

- 元のリポジトリ: https://github.com/WoWs-Builder-Team/minimap_renderer
- Flask公式ドキュメント: https://flask.palletsprojects.com/
- PyInstaller公式ドキュメント: https://pyinstaller.org/
- Socket.IO公式ドキュメント: https://socket.io/

## 更新履歴

- 2025-11-22: プロジェクト要件定義完了
