from flask import Flask, render_template, request, send_file, jsonify
from flask_socketio import SocketIO, emit
import os
import sys
import tempfile
import webbrowser
from threading import Timer, Thread
import time
import subprocess

# 実行ファイルの場所を取得（exe化対応）
if getattr(sys, 'frozen', False):
    # PyInstallerでexe化されている場合
    # _internalフォルダ内にリソースが配置される（読み取り専用）
    BASE_DIR = sys._MEIPASS
    # 実行ファイルと同じ場所（書き込み可能）
    EXE_DIR = os.path.dirname(sys.executable)
else:
    # 通常のPythonスクリプトとして実行されている場合
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.config['SECRET_KEY'] = 'your-secret-key-here'
# 動画は実行ファイルと同じ場所に保存（書き込み可能）
app.config['UPLOAD_FOLDER'] = os.path.join(EXE_DIR, 'videos')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 動画保存ディレクトリの確保
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ジョブの状態を保存する辞書
job_status = {}

@app.route('/')
def index():
    """メイン画面を表示"""
    return render_template('index.html')

def process_video(job_id, temp_replay_path, video_path, video_filename):
    """動画生成処理を別スレッドで実行"""
    import logging
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    logging.info(f'Starting process_video: {temp_replay_path} -> {video_path}')

    try:
        # 進捗を更新（開始）
        job_status[job_id] = {'percent': 10, 'message': 'リプレイファイルを解析中...', 'status': 'processing'}
        logging.info('Set initial progress')
        time.sleep(0.5)

        # minimap_rendererを呼び出す
        job_status[job_id] = {'percent': 30, 'message': '動画を生成中...', 'status': 'processing'}

        # minimap_rendererをコマンドラインツールとして実行
        import sys
        start_time = time.time()

        # 進捗を定期的に更新するためにバックグラウンドで実行
        stop_progress = {'stop': False}

        def update_progress():
            current_progress = 30
            while not stop_progress['stop']:
                elapsed = time.time() - start_time
                # 時間経過に応じて進捗を増加（最大90%まで）
                if elapsed < 60:  # 1分以内
                    current_progress = min(30 + int(elapsed), 60)
                elif elapsed < 120:  # 2分以内
                    current_progress = min(60 + int((elapsed - 60) / 2), 80)
                else:  # 2分以上
                    current_progress = min(80 + int((elapsed - 120) / 10), 90)

                job_status[job_id] = {'percent': current_progress, 'message': '動画を生成中...', 'status': 'processing'}
                time.sleep(1)

                # タイムアウトチェック（5分）
                if elapsed > 300:
                    return

        # 進捗更新スレッドを開始
        from threading import Thread as SubThread
        progress_thread = SubThread(target=update_progress)
        progress_thread.daemon = True
        progress_thread.start()

        # minimap_rendererを実行
        # exe化されている場合は直接Pythonコードを呼び出す
        if getattr(sys, 'frozen', False):
            # exe化時は直接rendererを呼び出す
            try:
                from renderer.render import Renderer
                from replay_parser import ReplayParser

                output_file = temp_replay_path.replace('.wowsreplay', '.mp4')

                with open(temp_replay_path, 'rb') as f:
                    logging.info('Parsing the replay file...')
                    replay_info = ReplayParser(f, strict=True, raw_data_output=False).get_info()
                    logging.info(f"Replay has version {replay_info['open']['clientVersionFromExe']}")
                    logging.info('Rendering the replay file...')
                    renderer = Renderer(
                        replay_info['hidden']['replay_data'],
                        logs=True,
                        enable_chat=True,
                        use_tqdm=False  # exe環境ではtqdmを無効化
                    )
                    renderer.start(str(output_file))
                    logging.info(f'The video file is at: {output_file}')
                    logging.info('Done.')

                # 成功を示すダミーのresult
                class DummyResult:
                    returncode = 0
                    stdout = ''
                    stderr = f'The video file is at: {output_file}'
                result = DummyResult()
            except Exception as render_error:
                import traceback
                error_detail = traceback.format_exc()
                logging.error(f'Render error: {error_detail}')
                class ErrorResult:
                    returncode = 1
                    stdout = ''
                    stderr = str(render_error)
                result = ErrorResult()
        else:
            # 通常実行時はsubprocessで呼び出す
            result = subprocess.run(
                [sys.executable, '-m', 'render', '--replay', temp_replay_path],
                capture_output=True,
                text=True,
                timeout=300  # 5分タイムアウト
            )

        # 進捗更新を停止
        stop_progress['stop'] = True
        progress_thread.join(timeout=1)

        logging.info(f'render stdout: {result.stdout}')
        logging.info(f'render stderr: {result.stderr}')
        logging.info(f'render returncode: {result.returncode}')

        if result.returncode != 0:
            raise Exception(f'動画生成に失敗しました: {result.stderr}')

        # 出力ファイルの移動（rendererは同じディレクトリに出力するため）
        import shutil
        output_file = temp_replay_path.replace('.wowsreplay', '.mp4')
        logging.info(f'Looking for output file: {output_file}')
        logging.info(f'Output file exists: {os.path.exists(output_file)}')

        if os.path.exists(output_file):
            logging.info(f'Moving {output_file} to {video_path}')
            shutil.move(output_file, video_path)
            logging.info(f'File moved successfully')
        else:
            # ファイルが見つからない場合、ログから実際のファイル名を探す
            import re
            match = re.search(r'The video file is at: (.+\.mp4)', result.stderr)
            if match:
                actual_output = match.group(1)
                logging.info(f'Found actual output file from log: {actual_output}')
                if os.path.exists(actual_output):
                    shutil.move(actual_output, video_path)
                    logging.info(f'File moved successfully from {actual_output}')
                else:
                    raise Exception(f'動画ファイルが見つかりません: {actual_output}')
            else:
                raise Exception(f'動画ファイルが生成されませんでした。期待したパス: {output_file}')

        # 完了
        job_status[job_id] = {
            'percent': 100,
            'message': '完了しました',
            'status': 'complete',
            'video_url': f'/videos/{video_filename}'
        }
        logging.info('Job completed successfully')

    except Exception as e:
        import traceback
        import logging
        error_detail = traceback.format_exc()
        logging.error(f'Error in process_video: {error_detail}')
        job_status[job_id] = {
            'status': 'error',
            'error': f'{str(e)}\n\n詳細:\n{error_detail}'
        }
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

    # ジョブIDと出力ファイル名を生成
    job_id = str(int(time.time() * 1000))  # ミリ秒単位のタイムスタンプ
    video_filename = f'replay_{job_id}.mp4'
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)

    # ジョブの初期状態を設定
    job_status[job_id] = {'percent': 0, 'message': '処理を開始しています...', 'status': 'processing'}

    # 別スレッドで処理を実行
    thread = Thread(target=process_video, args=(job_id, temp_replay.name, video_path, video_filename))
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'job_id': job_id})

@app.route('/status/<job_id>')
def check_status(job_id):
    """ジョブのステータスを取得"""
    if job_id in job_status:
        return jsonify(job_status[job_id])
    else:
        return jsonify({'error': 'ジョブが見つかりません'}), 404

@app.route('/videos/<filename>')
def serve_video(filename):
    """動画ファイルを配信"""
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(video_path):
        return send_file(video_path, mimetype='video/mp4')
    else:
        return jsonify({'error': 'ファイルが見つかりません'}), 404

def open_browser():
    """ブラウザを自動的に開く"""
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    import sys

    # exe化されているかチェック
    is_frozen = getattr(sys, 'frozen', False)

    # Flaskのreloaderによる複数起動を防ぐ
    # WERKZEUG_RUN_MAIN環境変数は、reloaderの子プロセスでのみ設定される
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # 1秒後にブラウザを開く（親プロセスまたはreloaderなしの場合のみ）
        Timer(1, open_browser).start()

    # Flaskアプリを起動（exe化時はdebugをオフ）
    socketio.run(app, debug=not is_frozen, host='0.0.0.0', port=5000)
