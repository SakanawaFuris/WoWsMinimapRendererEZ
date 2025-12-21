# 開発進捗

## 最終更新: 2025/12/21

### 完了した作業
- [x] minimap_rendererを最新版（14_11_0対応）に更新
- [x] 自動更新機能を実装
  - 起動時にGitHub APIで最新バージョンをチェック
  - 新しいゲームバージョン対応があればバナー表示
  - ワンクリックでversionsファイルをダウンロード・適用
- [x] ~~EXEを再ビルド（v20251220）~~ → 現在、Python 3.13互換性問題によりEXEビルド保留
- [x] JS変数名重複エラーを修正（updateProgress → updateProgressSection）
- [x] **14_11_0完全対応（開発サーバー版）** ✨
  - replay_unpack 14_11_0 サポート追加
  - entity definitions (scripts/) 完全追加
  - 新マップ 56_AngelWings 対応
  - Pillow 10.x互換性修正 (getsize → getbbox)

### 動作確認済み
✅ **開発サーバー版で14_11_0リプレイの動画生成成功！**
- 起動方法: `./venv/Scripts/python app.py`
- http://localhost:5000 でアクセス
- 14.11.0のリプレイファイルが正常に処理できることを確認

### 既知の問題
⚠️ **EXE版のビルドエラー**
- Python 3.13とPyInstallerの互換性問題（Werkzeug metadata）
- 現在、開発サーバー版での使用を推奨

### 配布方法（暫定）
開発サーバー版を使用：
1. プロジェクトフォルダ全体を配布
2. `venv` 含めてZIP化
3. 実行: `venv\Scripts\python.exe app.py`

### 技術メモ

#### 自動更新機能の仕組み
- **更新チェック**: `/api/check-update` - GitHub APIでrenderer/versionsを比較
- **更新適用**: `/api/update` - 不足バージョンをダウンロード
- **進捗確認**: `/api/update-status` - ダウンロード進捗を取得
- **保存先**: EXE版は `_update/renderer/versions/` に保存、次回起動時に `sys.path` で優先読み込み

#### 修正したファイル
- `app.py` - 更新API追加、パス設定
- `templates/index.html` - 更新バナーHTML追加
- `static/css/style.css` - 更新バナースタイル追加
- `static/js/app.js` - 更新チェックJS追加

---

## 変更履歴

### v20251220
- 14_11_0（WoWs 14.11.0）対応
- 自動更新機能追加
- Flask-SocketIO設定更新（allow_unsafe_werkzeug）

### v20251123
- 初回リリース
- 14_10_0まで対応
