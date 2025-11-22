# WoWs Minimap Renderer - GUI化プロジェクト

World of Warshipsのリプレイファイルから、ミニマップの動画を生成するツールを、Windows向けの使いやすいGUIアプリケーションとして実装するプロジェクトです。

## 📚 ドキュメント構成

このプロジェクトには、複数の会話セッションにまたがって開発を進めるための詳細なドキュメントが用意されています。

### 必須ドキュメント

| ドキュメント | 目的 | いつ読む？ |
|------------|------|-----------|
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | クイックリファレンス | **毎回のセッション開始時** |
| **[PROJECT_SPEC.md](PROJECT_SPEC.md)** | プロジェクト全体の設計書 | 要件・仕様を確認したいとき |
| **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** | 開発手順とチェックリスト | 実装中、次のステップを確認 |
| **[CLAUDE_CODE_GUIDE.md](CLAUDE_CODE_GUIDE.md)** | Claude Codeの使い方 | Claude Codeを試すとき |

### ドキュメントの読む順番

#### 初めてこのプロジェクトに触れる場合
```
1. README.md（このファイル） ← 今ここ
   ↓
2. PROJECT_SPEC.md
   - プロジェクトの全体像を理解
   - 要件定義を確認
   ↓
3. DEVELOPMENT_GUIDE.md
   - 開発手順を確認
   - Phase 1.1から開始
   ↓
4. CLAUDE_CODE_GUIDE.md（オプション）
   - Claude Codeを使う場合のみ
```

#### 開発を再開する場合
```
1. QUICK_REFERENCE.md
   - 現在の進捗を確認
   - 次のステップを把握
   ↓
2. DEVELOPMENT_GUIDE.md
   - 該当するPhaseの手順を実行
```

## 🚀 プロジェクト概要

### 現状（Before）
- コマンドライン操作が必要
- Python環境のセットアップが必要
- 技術的な知識が必要

### 目標（After）
- ✨ exeファイルをダブルクリックで起動
- ✨ ブラウザで簡単に操作できるGUI
- ✨ プログラミング知識不要

### ユーザー体験
```
1. minimap_renderer.exe をダブルクリック
   ↓
2. ブラウザが自動で開く
   ↓
3. リプレイファイルを選択
   ↓
4. 「動画生成」をクリック
   ↓
5. 進捗を見ながら待つ
   ↓
6. 動画を再生 or ダウンロード
```

## 📋 開発状況

### ✅ 完了
- [x] プロジェクト要件定義
- [x] 技術スタック決定
- [x] ドキュメント作成
- [x] Git管理方針決定

### 🔄 進行中
- [ ] Phase 1: 基本機能実装

### 📅 予定
- [ ] Phase 2: UI改善
- [ ] Phase 3: パッケージング

## 🛠️ 技術スタック

- **言語**: Python 3.10
- **Webフレームワーク**: Flask 3.x
- **リアルタイム通信**: Flask-SocketIO
- **フロントエンド**: HTML5, CSS3, JavaScript (Vanilla)
- **レンダリングエンジン**: minimap_renderer（既存）
- **パッケージング**: PyInstaller

## 📂 ディレクトリ構成（完成予定）

```
minimap_renderer_gui/
├── README.md                     # このファイル
├── PROJECT_SPEC.md              # プロジェクト設計書
├── DEVELOPMENT_GUIDE.md         # 開発手順書
├── CLAUDE_CODE_GUIDE.md         # Claude Code活用ガイド
├── QUICK_REFERENCE.md           # クイックリファレンス
├── app.py                       # Flaskメインアプリ
├── requirements.txt             # 依存パッケージリスト
├── build_exe.bat               # ビルドスクリプト
├── .gitignore                  # Git除外設定
├── venv/                       # 仮想環境（Git管理外）
├── static/                     # 静的ファイル
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── videos/                # 生成動画（Git管理外）
└── templates/                  # HTMLテンプレート
    └── index.html
```

## 🎯 次のアクション

### すぐに開発を始める場合

**方法1: 手動実装**
```bash
# 1. DEVELOPMENT_GUIDE.mdを開く
# 2. Phase 1.1の手順に従う
# 3. コマンドを1つずつ実行
```

**方法2: Claude Code使用（推奨）**
```bash
# 1. CLAUDE_CODE_GUIDE.mdを読む
# 2. Claude Codeをセットアップ
# 3. claude code を実行
# 4. 「DEVELOPMENT_GUIDE.mdのPhase 1.1を実装してください」と指示
```

### まず理解を深める場合
```bash
# 1. PROJECT_SPEC.mdを読む（プロジェクト全体の理解）
# 2. 元のリポジトリを確認
#    https://github.com/WoWs-Builder-Team/minimap_renderer
# 3. DEVELOPMENT_GUIDE.mdを読む（実装手順の理解）
```

## 🤝 開発の進め方

### 推奨ワークフロー

1. **セッション開始時**
   - QUICK_REFERENCE.mdで進捗確認
   - 前回からの変更点を確認

2. **実装中**
   - DEVELOPMENT_GUIDE.mdの該当Phaseを参照
   - チェックボックスで進捗を記録
   - 小まめにコミット

3. **問題発生時**
   - エラーメッセージをコピー
   - Claude.aiまたはClaude Codeに相談
   - 解決後、DEVELOPMENT_GUIDE.mdに追記

4. **セッション終了時**
   - QUICK_REFERENCE.mdの進捗状況を更新
   - git commitで作業内容を保存
   - 次回の開始点をメモ

### Git管理

```bash
# 機能開発時
git checkout -b feature/機能名
# 開発...
git add .
git commit -m "feat: 機能の説明"
git checkout develop
git merge feature/機能名

# 安定版リリース時
git checkout main
git merge develop
git tag v1.0.0
```

## 📖 よくある質問

### Q: 開発環境は何が必要？
A: Windows 10/11、Python 3.10、Git for Windows。エディタはVS Code推奨。

### Q: Python経験がないけど大丈夫？
A: DEVELOPMENT_GUIDE.mdに全コマンドとコードが記載されています。コピー＆ペーストで進められます。

### Q: 複数の会話セッションにまたがっても大丈夫？
A: はい。QUICK_REFERENCE.mdで進捗を確認し、DEVELOPMENT_GUIDE.mdで続きから再開できます。

### Q: Claude Codeは必須？
A: いいえ、オプションです。手動実装でも問題ありません。ただし、Claude Codeの方が効率的です。

### Q: エラーが出たらどうする？
A: エラーメッセージをClaude.aiまたはClaude Codeに貼り付けて相談してください。

### Q: 開発期間はどのくらい？
A: 約4-5日を想定しています。1日2-3時間の作業で1週間程度。

## 🔗 関連リンク

- **元のリポジトリ**: https://github.com/WoWs-Builder-Team/minimap_renderer
- **Flask公式ドキュメント**: https://flask.palletsprojects.com/
- **PyInstaller公式**: https://pyinstaller.org/
- **Claude.ai**: https://claude.ai/

## 📝 ライセンス

このプロジェクトは元のminimap_rendererと同じく GNU AGPLv3 ライセンスを継承します。

## 👥 貢献者

- プロジェクトオーナー: [あなたの名前]
- 技術サポート: Claude (Anthropic)

---

**開発を始める準備はできましたか？**

👉 次は [QUICK_REFERENCE.md](QUICK_REFERENCE.md) を開いて、現在の状況を確認してください。
👉 その後、[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) のPhase 1.1から開始します。

**成功を祈っています！🎮🚀**
