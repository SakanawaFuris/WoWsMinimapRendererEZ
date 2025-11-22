# クイックリファレンス - WoWs Minimap Renderer GUI化プロジェクト

このドキュメントは各会話セッションの冒頭で参照してください。

## プロジェクト概要（10秒で理解）

**目的**: World of WarshipsのリプレイからミニマップGIF動画を生成するPythonツールを、Windows用の簡易GUIアプリにする

**配布形態**: zipファイル → 解凍 → exe起動 → ブラウザでGUI操作

**技術**: Python 3.10 + Flask + HTML/CSS/JS → PyInstallerでexe化

## 重要なファイル

| ファイル名 | 役割 | いつ見る？ |
|-----------|------|-----------|
| `PROJECT_SPEC.md` | プロジェクト全体の設計書 | 要件を確認したいとき |
| `DEVELOPMENT_GUIDE.md` | 開発手順とチェックリスト | 実装中、次に何をすべきか確認 |
| `CLAUDE_CODE_GUIDE.md` | Claude Codeの使い方 | Claude Codeを試すとき |
| `QUICK_REFERENCE.md` | このファイル | 毎回のセッション開始時 |

## 現在の進捗状況

### ✅ 完了済み
- プロジェクト要件定義
- 技術スタック決定
- ドキュメント作成

### 🔄 進行中
- Phase 1.1: プロジェクト構造作成（次のステップ）

### 📋 未着手
- Phase 1.2: Flask基本アプリ
- Phase 1.3: minimap_renderer統合
- Phase 2: UI改善（リアルタイム進捗）
- Phase 3: パッケージング

## 次回セッション開始時の推奨フレーズ

```
「minimap_renderer_guiプロジェクトの開発を続けます。
QUICK_REFERENCE.mdで現在の進捗を確認してから、
DEVELOPMENT_GUIDE.mdに従って次のフェーズを進めてください。」
```

## よく使うコマンド

```bash
# 仮想環境の有効化（毎回開発前に実行）
venv\Scripts\activate

# Flaskアプリの起動
python app.py

# パッケージのインストール
pip install [パッケージ名]

# Git操作
git add .
git commit -m "メッセージ"
git status

# PyInstallerでexe化（Phase 3で使用）
pyinstaller --onefile --noconsole app.py
```

## トラブルシューティング

### 問題: Flaskアプリが起動しない
→ `venv\Scripts\activate` を実行したか確認
→ `pip install flask flask-socketio` を実行

### 問題: minimap_rendererが見つからない
→ `pip install --upgrade --force-reinstall git+https://github.com/WoWs-Builder-Team/minimap_renderer.git`

### 問題: ブラウザが自動で開かない
→ 手動で `http://localhost:5000` にアクセス

### 問題: ポート5000が使用中
→ app.pyのport番号を5001などに変更

## 技術的な重要ポイント

### ファイル構成
```
minimap_renderer_gui/
├── app.py                # メインアプリ（Flask）
├── requirements.txt      # 依存関係
├── templates/
│   └── index.html       # UI
├── static/
│   ├── css/style.css    # スタイル
│   ├── js/app.js        # フロントエンドロジック
│   └── videos/          # 生成された動画保存先
└── venv/                # 仮想環境（Gitに含めない）
```

### キーとなる技術的判断
1. **Flask使用**: 軽量、学習コストが低い
2. **Socket.IO使用**: リアルタイム進捗表示のため
3. **PyInstaller --onefile**: 単一exeで配布しやすい
4. **webbrowser.open()**: ブラウザ自動起動

### パフォーマンス考慮事項
- リプレイファイルは一時ディレクトリに保存→処理後削除
- 生成動画は`static/videos/`に保存（.gitignoreで除外）
- 動画ファイルは処理後も残す（ユーザーが再ダウンロード可能）

## ユーザー要件（再確認）

- ✅ Windows専用
- ✅ プログラミング経験不要で使える
- ✅ ワンクリックで起動
- ✅ WebブラウザベースのシンプルなUI
- ✅ 進捗表示あり
- ✅ 動画再生とダウンロード可能
- ✅ 連続処理可能（終了せずに次のファイル処理）
- ❌ 複数ファイル一括処理（不要）
- ❌ 設定変更機能（不要）
- ❌ 履歴管理（不要）

## Git管理方針

### ブランチ戦略
- `main`: 動作する安定版のみ
- `develop`: 開発中のコード
- `feature/*`: 機能ごとのブランチ

### 推奨コミットメッセージ
```
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
refactor: リファクタリング
style: コードスタイル修正
test: テスト追加
```

### .gitignoreで除外するもの
- `venv/`
- `__pycache__/`
- `*.pyc`
- `static/videos/*.mp4`
- `build/`, `dist/`, `*.spec`

## 開発環境情報

**必要な環境:**
- Windows 10/11
- Python 3.10
- Git for Windows
- 任意: VS Code

**推奨エディタ設定（VS Code）:**
```json
{
  "python.defaultInterpreterPath": "venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "editor.formatOnSave": true
}
```

## 次のアクション（Phase 1.1）

1. プロジェクトディレクトリ作成
2. Git初期化
3. 仮想環境作成
4. 依存パッケージインストール
5. ディレクトリ構造作成
6. .gitignore作成
7. 初回コミット

詳細は `DEVELOPMENT_GUIDE.md` の Phase 1.1 を参照。

## このプロジェクトの目標タイムライン

- **Phase 1**: 2-3日（基本機能実装）
- **Phase 2**: 1日（UI改善）
- **Phase 3**: 1日（パッケージング）

**合計**: 約4-5日で完成予定

---

**最終更新**: 2025-11-22
**現在のフェーズ**: Phase 1.1（準備中）
**次の会話での開始点**: DEVELOPMENT_GUIDE.md Phase 1.1の実行
