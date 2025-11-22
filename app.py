from flask import Flask, render_template, request, send_file, jsonify
from flask_socketio import SocketIO, emit
import os
import tempfile
import webbrowser
from threading import Timer, Thread
import time
import subprocess

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

def process_video(temp_replay_path, video_path, video_filename):
    """動画生成処理を別スレッドで実行"""
    try:
        # 進捗を送信（開始）
        socketio.emit('progress', {'percent': 10, 'message': 'リプレイファイルを解析中...'})
        time.sleep(0.5)

        # minimap_rendererを呼び出す
        socketio.emit('progress', {'percent': 30, 'message': '動画を生成中...'})

        # Popenで実行し、進捗をシミュレート
        process = subprocess.Popen(
            ['python', '-m', 'render', '--replay', temp_replay_path, '--output', video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # プロセスが実行中の間、進捗を更新
        start_time = time.time()
        current_progress = 30

        while process.poll() is None:
            elapsed = time.time() - start_time
            # 時間経過に応じて進捗を増加（最大90%まで）
            if elapsed < 60:  # 1分以内
                current_progress = min(30 + int(elapsed), 60)
            elif elapsed < 120:  # 2分以内
                current_progress = min(60 + int((elapsed - 60) / 2), 80)
            else:  # 2分以上
                current_progress = min(80 + int((elapsed - 120) / 10), 90)

            socketio.emit('progress', {'percent': current_progress, 'message': '動画を生成中...'})
            time.sleep(1)

            # タイムアウトチェック（5分）
            if elapsed > 300:
                process.kill()
                socketio.emit('error', {'error': '処理がタイムアウトしました（5分以上）'})
                return

        # プロセス完了
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            socketio.emit('error', {'error': f'動画生成に失敗しました: {stderr}'})
            return

        if not os.path.exists(video_path):
            socketio.emit('error', {'error': '動画ファイルが生成されませんでした'})
            return

        # 完了
        socketio.emit('progress', {'percent': 100, 'message': '完了しました'})
        socketio.emit('complete', {
            'success': True,
            'video_url': f'/static/videos/{video_filename}'
        })

    except Exception as e:
        socketio.emit('error', {'error': str(e)})
    finally:
        # 一時ファイル削除
        if os.path.exists(temp_replay_path):
            os.unlink(temp_replay_path)

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
    timestamp = int(time.time())
    video_filename = f'replay_{timestamp}.mp4'
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)

    # 別スレッドで処理を実行
    thread = Thread(target=process_video, args=(temp_replay.name, video_path, video_filename))
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'message': '処理を開始しました'})

def open_browser():
    """ブラウザを自動的に開く"""
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # 1秒後にブラウザを開く
    Timer(1, open_browser).start()
    # Flaskアプリを起動
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
