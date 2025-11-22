# 開発手順書 - WoWs Minimap Renderer GUI化

このドキュメントは、複数の会話セッションにまたがって開発を進める際の指針となります。
各フェーズの完了状況をチェックボックスで管理してください。

## 事前準備

### ✅ チェックリスト
- [ ] Windows環境の確認
- [ ] Python 3.10のインストール確認: `python --version`
- [ ] Gitのインストール確認: `git --version`
- [ ] プロジェクトディレクトリの作成
- [ ] Git初期化
- [ ] 仮想環境の作成と有効化
- [ ] 基本依存パッケージのインストール

### 📝 実行コマンド

```bash
# プロジェクトディレクトリ作成
cd %USERPROFILE%\Documents
mkdir minimap_renderer_gui
cd minimap_renderer_gui

# Git初期化
git init
git branch -M main

# 仮想環境作成
python -m venv venv

# 仮想環境有効化（毎回開発時に実行）
venv\Scripts\activate

# 依存パッケージインストール
pip install flask flask-socketio python-socketio eventlet
pip install --upgrade --force-reinstall git+https://github.com/WoWs-Builder-Team/minimap_renderer.git
pip install pyinstaller

# requirements.txt生成
pip freeze > requirements.txt

# .gitignore作成（後述）
```

---

## Phase 1: 基本機能実装

### 1.1 プロジェクト構造の作成

#### ✅ チェックリスト
- [ ] ディレクトリ構造の作成
- [ ] .gitignoreファイルの作成
- [ ] 初回コミット

#### 📝 実行コマンド

```bash
# ディレクトリ作成
mkdir static
mkdir static\css
mkdir static\js
mkdir static\videos
mkdir templates

# .gitignoreファイル作成（内容は下記参照）
type nul > .gitignore

# 初回コミット
git add .
git commit -m "feat: プロジェクト初期構造を作成"
```

#### 📄 作成するファイル

**`.gitignore`の内容:**
```
# Python
venv/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/

# 動画ファイル
static/videos/*.mp4
static/videos/*.avi

# IDE
.vscode/
.idea/
*.swp

# OS
Thumbs.db
.DS_Store

# PyInstaller
*.spec
build/
dist/
```

---

### 1.2 Flaskアプリケーションの基本実装

#### ✅ チェックリスト
- [ ] app.pyの作成（基本構造）
- [ ] index.htmlの作成（UI骨組み）
- [ ] style.cssの作成（基本スタイル）
- [ ] app.jsの作成（基本ロジック）
- [ ] 動作確認（Flask起動）

#### 📄 作成するファイル: `app.py`

```python
from flask import Flask, render_template, request, send_file, jsonify
from flask_socketio import SocketIO, emit
import os
import tempfile
import webbrowser
from threading import Timer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'videos')
socketio = SocketIO(app, cors_allowed_origins="*")

# 動画保存ディレクトリの確保
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """メイン画面を表示"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """リプレイファイルをアップロードして動画生成"""
    if 'replay_file' not in request.files:
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    file = request.files['replay_file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    if not file.filename.endswith('.wowsreplay'):
        return jsonify({'error': 'リプレイファイル (.wowsreplay) を選択してください'}), 400
    
    # 一時ファイルとして保存
    temp_replay = tempfile.NamedTemporaryFile(delete=False, suffix='.wowsreplay')
    file.save(temp_replay.name)
    
    try:
        # TODO: ここでminimap_rendererを呼び出す
        # 今はダミーレスポンス
        video_filename = 'output_test.mp4'
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        
        return jsonify({
            'success': True,
            'video_url': f'/static/videos/{video_filename}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # 一時ファイル削除
        if os.path.exists(temp_replay.name):
            os.unlink(temp_replay.name)

def open_browser():
    """ブラウザを自動的に開く"""
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # 1秒後にブラウザを開く
    Timer(1, open_browser).start()
    # Flaskアプリを起動
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
```

#### 📄 作成するファイル: `templates/index.html`

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WoWs Minimap Renderer</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>🎮 WoWs Minimap Renderer</h1>
        <p class="subtitle">リプレイファイルから動画を生成します</p>
        
        <div class="upload-section">
            <form id="uploadForm" enctype="multipart/form-data">
                <label for="replayFile" class="file-label">
                    📁 リプレイファイルを選択
                </label>
                <input type="file" id="replayFile" name="replay_file" accept=".wowsreplay" required>
                <p id="fileName" class="file-name"></p>
                <button type="submit" class="btn-primary">🎬 動画生成</button>
            </form>
        </div>

        <div id="progressSection" class="progress-section hidden">
            <h2>処理中...</h2>
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill"></div>
            </div>
            <p id="progressText" class="progress-text">0%</p>
        </div>

        <div id="resultSection" class="result-section hidden">
            <h2>✅ 生成完了！</h2>
            <video id="videoPlayer" controls class="video-player">
                <source id="videoSource" src="" type="video/mp4">
                お使いのブラウザは動画再生に対応していません。
            </video>
            <div class="button-group">
                <a id="downloadBtn" href="#" download class="btn-primary">⬇️ ダウンロード</a>
                <button id="resetBtn" class="btn-secondary">🔄 別のファイルを処理</button>
            </div>
        </div>

        <div id="errorSection" class="error-section hidden">
            <h2>❌ エラー</h2>
            <p id="errorMessage"></p>
            <button id="errorResetBtn" class="btn-secondary">🔄 やり直す</button>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

#### 📄 作成するファイル: `static/css/style.css`

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.container {
    background: white;
    border-radius: 20px;
    padding: 40px;
    max-width: 800px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

h1 {
    color: #333;
    text-align: center;
    margin-bottom: 10px;
    font-size: 2.5em;
}

.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 30px;
}

.upload-section {
    text-align: center;
    padding: 20px;
}

.file-label {
    display: inline-block;
    padding: 15px 30px;
    background-color: #667eea;
    color: white;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s;
    font-size: 1.1em;
    margin-bottom: 15px;
}

.file-label:hover {
    background-color: #5568d3;
}

input[type="file"] {
    display: none;
}

.file-name {
    color: #666;
    margin: 10px 0;
    min-height: 20px;
}

.btn-primary, .btn-secondary {
    padding: 15px 40px;
    border: none;
    border-radius: 10px;
    font-size: 1.1em;
    cursor: pointer;
    transition: all 0.3s;
    margin: 10px;
}

.btn-primary {
    background-color: #28a745;
    color: white;
}

.btn-primary:hover {
    background-color: #218838;
    transform: translateY(-2px);
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #5a6268;
}

.progress-section, .result-section, .error-section {
    text-align: center;
    padding: 20px;
}

.hidden {
    display: none !important;
}

.progress-bar {
    width: 100%;
    height: 30px;
    background-color: #e0e0e0;
    border-radius: 15px;
    overflow: hidden;
    margin: 20px 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    width: 0%;
    transition: width 0.3s;
}

.progress-text {
    font-size: 1.2em;
    color: #333;
    font-weight: bold;
}

.video-player {
    width: 100%;
    max-width: 700px;
    border-radius: 10px;
    margin: 20px 0;
}

.button-group {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
}

.error-section {
    background-color: #f8d7da;
    border-radius: 10px;
    padding: 30px;
}

#errorMessage {
    color: #721c24;
    font-size: 1.1em;
    margin: 20px 0;
}
```

#### 📄 作成するファイル: `static/js/app.js`

```javascript
// DOM要素の取得
const uploadForm = document.getElementById('uploadForm');
const replayFile = document.getElementById('replayFile');
const fileName = document.getElementById('fileName');
const progressSection = document.getElementById('progressSection');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const uploadSection = document.querySelector('.upload-section');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const videoPlayer = document.getElementById('videoPlayer');
const videoSource = document.getElementById('videoSource');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const errorResetBtn = document.getElementById('errorResetBtn');
const errorMessage = document.getElementById('errorMessage');

// ファイル選択時の処理
replayFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        fileName.textContent = `選択: ${e.target.files[0].name}`;
    }
});

// フォーム送信時の処理
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(uploadForm);
    
    // UIをリセット
    hideAllSections();
    progressSection.classList.remove('hidden');
    
    // 進捗を0%に
    updateProgress(0);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else {
            // 成功時の処理
            showResult(data.video_url);
        }
    } catch (error) {
        showError('処理中にエラーが発生しました: ' + error.message);
    }
});

// リセットボタンの処理
resetBtn.addEventListener('click', resetApp);
errorResetBtn.addEventListener('click', resetApp);

function resetApp() {
    hideAllSections();
    uploadSection.classList.remove('hidden');
    uploadForm.reset();
    fileName.textContent = '';
}

function hideAllSections() {
    uploadSection.classList.add('hidden');
    progressSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
}

function updateProgress(percent) {
    progressFill.style.width = percent + '%';
    progressText.textContent = Math.round(percent) + '%';
}

function showResult(videoUrl) {
    hideAllSections();
    resultSection.classList.remove('hidden');
    
    videoSource.src = videoUrl;
    videoPlayer.load();
    downloadBtn.href = videoUrl;
    downloadBtn.download = 'minimap_' + Date.now() + '.mp4';
}

function showError(message) {
    hideAllSections();
    errorSection.classList.remove('hidden');
    errorMessage.textContent = message;
}

// TODO: Socket.IOで進捗をリアルタイム受信
// const socket = io();
// socket.on('progress', (data) => {
//     updateProgress(data.percent);
// });
```

#### 📝 動作確認コマンド

```bash
# Flaskアプリを起動
python app.py

# ブラウザが自動的に開くはず
# 開かない場合は手動で http://localhost:5000 にアクセス
```

#### 📝 コミット

```bash
git add .
git commit -m "feat: Flask基本アプリとUIを実装"
```

---

### 1.3 minimap_rendererとの統合

#### ✅ チェックリスト
- [ ] minimap_rendererの呼び出しコード実装
- [ ] エラーハンドリング実装
- [ ] 実際のリプレイファイルでテスト

#### 📝 `app.py`の修正箇所

`app.py`の`upload_file()`関数を以下のように修正:

```python
@app.route('/upload', methods=['POST'])
def upload_file():
    """リプレイファイルをアップロードして動画生成"""
    if 'replay_file' not in request.files:
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    file = request.files['replay_file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    if not file.filename.endswith('.wowsreplay'):
        return jsonify({'error': 'リプレイファイル (.wowsreplay) を選択してください'}), 400
    
    # 一時ファイルとして保存
    temp_replay = tempfile.NamedTemporaryFile(delete=False, suffix='.wowsreplay')
    file.save(temp_replay.name)
    
    # 出力ファイル名を生成
    import time
    timestamp = int(time.time())
    video_filename = f'replay_{timestamp}.mp4'
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    
    try:
        # minimap_rendererを呼び出す
        import subprocess
        
        # renderモジュールを実行
        result = subprocess.run(
            ['python', '-m', 'render', '--replay', temp_replay.name, '--output', video_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分のタイムアウト
        )
        
        if result.returncode != 0:
            raise Exception(f'動画生成に失敗しました: {result.stderr}')
        
        if not os.path.exists(video_path):
            raise Exception('動画ファイルが生成されませんでした')
        
        return jsonify({
            'success': True,
            'video_url': f'/static/videos/{video_filename}'
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': '処理がタイムアウトしました（5分以上）'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # 一時ファイル削除
        if os.path.exists(temp_replay.name):
            os.unlink(temp_replay.name)
```

#### 📝 コミット

```bash
git add app.py
git commit -m "feat: minimap_rendererとの統合を実装"
```

---

## Phase 2: UI改善（リアルタイム進捗表示）

### 2.1 Socket.IOによる進捗通知

#### ✅ チェックリスト
- [ ] Socket.IO実装（バックエンド）
- [ ] Socket.IO実装（フロントエンド）
- [ ] 進捗表示のテスト

#### 📝 詳細は次の会話で実装

---

## Phase 3: パッケージング

### 3.1 PyInstallerでexe化

#### ✅ チェックリスト
- [ ] specファイルの作成
- [ ] ビルドスクリプトの作成
- [ ] exe生成テスト
- [ ] 動作確認

#### 📝 詳細は次の会話で実装

---

## 開発進捗トラッキング

### 現在のステータス
- **現在のフェーズ**: Phase 1.2 - Flaskアプリ基本実装
- **最終更新日**: 2025-11-22
- **次のステップ**: 基本アプリの動作確認

### 完了済み
- [ ] Phase 1.1: プロジェクト構造
- [ ] Phase 1.2: Flask基本アプリ
- [ ] Phase 1.3: minimap_renderer統合

### 保留中の課題
- なし

### 次回セッションで確認すること
1. 基本アプリが起動するか
2. UIが正常に表示されるか
3. ファイル選択が動作するか
