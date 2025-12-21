# 🔄 minimap_renderer 更新ガイド

## 現在のバージョン確認

```bash
./venv/Scripts/pip show minimap-renderer
```

## 更新手順

### 1. 最新バージョンの確認

GitHubで最新リリースを確認：
```
https://github.com/WoWs-Builder-Team/minimap_renderer/releases
```

### 2. minimap_rendererの更新

#### 方法A: 最新版に更新（推奨）

```bash
./venv/Scripts/pip install --upgrade --force-reinstall git+https://github.com/WoWs-Builder-Team/minimap_renderer.git
```

#### 方法B: 特定バージョンに更新

```bash
# 例: v0.11.9 に更新する場合
./venv/Scripts/pip install --upgrade --force-reinstall git+https://github.com/WoWs-Builder-Team/minimap_renderer.git@v0.11.9
```

### 3. 更新後のテスト

#### アプリケーションのテスト実行

```bash
./venv/Scripts/python app.py
```

ブラウザで http://localhost:5000 にアクセスし、リプレイファイルで動画生成をテスト。

### 4. exeファイルの再ビルド

更新が正常に動作することを確認したら、exeを再ビルド：

```bash
# 古いビルドを削除
rm -rf dist build

# 再ビルド
./venv/Scripts/pyinstaller minimap_renderer_gui.spec
```

### 5. 配布パッケージの作成

```bash
./venv/Scripts/python -c "
import zipfile
import os
from pathlib import Path

# バージョン番号を更新してください
version = '1.0.1'  # ← ここを変更
zip_name = f'WoWsMinimapRenderer_v{version}.zip'

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('README.md', 'WoWsMinimapRenderer/README.md')
    
    dist_path = Path('dist/WoWsMinimapRenderer')
    for file in dist_path.rglob('*'):
        if file.is_file():
            arcname = 'WoWsMinimapRenderer/' + str(file.relative_to('dist'))
            zipf.write(file, arcname)

print(f'Created: {zip_name}')
print(f'Size: {os.path.getsize(zip_name) / 1024 / 1024:.1f} MB')
"
```

## トラブルシューティング

### 更新後にエラーが発生する場合

#### 1. 依存関係の再インストール

```bash
./venv/Scripts/pip install --upgrade pip
./venv/Scripts/pip install --upgrade -r requirements.txt
```

#### 2. 仮想環境の再作成（最終手段）

```bash
# 古い仮想環境を削除
rm -rf venv

# 新しい仮想環境を作成
python -m venv venv

# 依存関係を再インストール
./venv/Scripts/pip install -r requirements.txt
./venv/Scripts/pip install --force-reinstall git+https://github.com/WoWs-Builder-Team/minimap_renderer.git
```

### PyInstallerでのエラー

specファイルのhiddenimportsに新しいモジュールを追加する必要がある場合があります。

エラーメッセージから不足しているモジュールを確認し、`minimap_renderer_gui.spec` の `hiddenimports` リストに追加：

```python
hiddenimports=[
    'flask',
    'flask_socketio',
    # ... 既存のインポート
    'new_module_name',  # ← 新しいモジュールを追加
],
```

## バージョン管理

### requirements.txtの更新

更新後、現在の依存関係を記録：

```bash
./venv/Scripts/pip freeze > requirements.txt
```

### 変更履歴の記録

CHANGELOG.md を作成して変更内容を記録することを推奨：

```markdown
## [1.0.1] - 2025-XX-XX
### Changed
- minimap_renderer を 0.11.8.1 → 0.11.9 に更新

### Fixed
- 新しいリプレイバージョンへの対応
```

## 定期的な更新チェック

月に1回程度、以下をチェック：
1. minimap_rendererの新しいリリース
2. World of Warshipsのアップデート後の互換性
3. 依存パッケージのセキュリティアップデート

---

**注意**: 本番環境（配布版）を更新する前に、必ず開発環境でテストしてください。
