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

def open_browser():
    """ブラウザを自動的に開く"""
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # 1秒後にブラウザを開く
    Timer(1, open_browser).start()
    # Flaskアプリを起動
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
