from flask import Flask, render_template, request, send_file, jsonify
from flask_socketio import SocketIO, emit
import os
import sys
import tempfile
import webbrowser
from threading import Timer, Thread
import time
import subprocess
import json
import urllib.request
import urllib.error
import shutil
import re

# 実行ファイルの場所を取得（exe化対応）
if getattr(sys, 'frozen', False):
    # PyInstallerでexe化されている場合
    # _internalフォルダ内にリソースが配置される（読み取り専用）
    BASE_DIR = sys._MEIPASS
    # 実行ファイルと同じ場所（書き込み可能）
    EXE_DIR = os.path.dirname(sys.executable)
    # 更新用ディレクトリをPythonパスに追加（更新されたバージョンを優先）
    UPDATE_DIR = os.path.join(EXE_DIR, '_update')
    if os.path.exists(UPDATE_DIR):
        sys.path.insert(0, UPDATE_DIR)
else:
    # 通常のPythonスクリプトとして実行されている場合
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR

# リバースプロキシ経由で動作する場合のサブパス設定
# 例: MINIMAP_SUBPATH=/apps/minimap-renderer
SUBPATH = os.environ.get('MINIMAP_SUBPATH', '')

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.config['SECRET_KEY'] = 'your-secret-key-here'
# 動画は実行ファイルと同じ場所に保存（書き込み可能）
app.config['UPLOAD_FOLDER'] = os.path.join(EXE_DIR, 'videos')

# サブパスが設定されている場合、SCRIPT_NAMEミドルウェアを適用
# これによりurl_for('static', ...)が正しいパスを生成する
if SUBPATH:
    class _PrefixMiddleware:
        def __init__(self, wsgi_app, prefix):
            self.wsgi_app = wsgi_app
            self.prefix = prefix
        def __call__(self, environ, start_response):
            environ['SCRIPT_NAME'] = self.prefix
            path_info = environ.get('PATH_INFO', '')
            if path_info.startswith(self.prefix):
                environ['PATH_INFO'] = path_info[len(self.prefix):]
            return self.wsgi_app(environ, start_response)
    app.wsgi_app = _PrefixMiddleware(app.wsgi_app, SUBPATH)

# Socket.IOのパス（サブパス対応）
_socketio_path = f'{SUBPATH}/socket.io' if SUBPATH else '/socket.io'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', path=_socketio_path)

# 動画保存ディレクトリの確保
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ジョブの状態を保存する辞書
job_status = {}

# 更新関連の設定
GITHUB_API_BASE = "https://api.github.com/repos/WoWs-Builder-Team/minimap_renderer"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/WoWs-Builder-Team/minimap_renderer/master"
update_status = {'updating': False, 'progress': 0, 'message': ''}

def get_local_versions():
    """ローカルにインストールされているバージョンのリストを取得"""
    versions = set()
    try:
        if getattr(sys, 'frozen', False):
            # EXE化されている場合
            # まず_update内を確認、なければ_internal内
            update_versions_dir = os.path.join(EXE_DIR, '_update', 'renderer', 'versions')
            internal_versions_dir = os.path.join(BASE_DIR, 'renderer', 'versions')

            for versions_dir in [update_versions_dir, internal_versions_dir]:
                if os.path.exists(versions_dir):
                    for item in os.listdir(versions_dir):
                        if os.path.isdir(os.path.join(versions_dir, item)) and re.match(r'^\d+_\d+', item):
                            versions.add(item)
        else:
            import renderer
            versions_dir = os.path.join(os.path.dirname(renderer.__file__), 'versions')
            if os.path.exists(versions_dir):
                for item in os.listdir(versions_dir):
                    if os.path.isdir(os.path.join(versions_dir, item)) and re.match(r'^\d+_\d+', item):
                        versions.add(item)
    except Exception as e:
        print(f"Error getting local versions: {e}")
    return versions

def get_remote_versions():
    """GitHubから利用可能なバージョンのリストを取得

    Returns:
        tuple: (versions: set, error: str or None)
    """
    versions = set()
    try:
        url = f"{GITHUB_API_BASE}/contents/src/renderer/versions"
        req = urllib.request.Request(url, headers={'User-Agent': 'WoWsMinimapRenderer'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            for item in data:
                if item['type'] == 'dir' and re.match(r'^\d+_\d+', item['name']):
                    versions.add(item['name'])
        return versions, None
    except urllib.error.URLError as e:
        error_msg = f"ネットワークエラー: {e.reason}"
        print(f"Error getting remote versions: {error_msg}")
        return versions, error_msg
    except urllib.error.HTTPError as e:
        if e.code == 403:
            error_msg = "GitHub APIの制限に達しました。しばらく待ってから再試行してください。"
        else:
            error_msg = f"HTTPエラー: {e.code}"
        print(f"Error getting remote versions: {error_msg}")
        return versions, error_msg
    except Exception as e:
        error_msg = f"エラー: {str(e)}"
        print(f"Error getting remote versions: {error_msg}")
        return versions, error_msg

def download_version_files(version_name, target_dir):
    """指定バージョンのファイルをダウンロード"""
    base_path = f"src/renderer/versions/{version_name}"

    # ディレクトリ構造を作成
    version_dir = os.path.join(target_dir, version_name)
    layers_dir = os.path.join(version_dir, 'layers')
    resources_dir = os.path.join(version_dir, 'resources')
    os.makedirs(layers_dir, exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)

    # __init__.py
    download_file(f"{GITHUB_RAW_BASE}/{base_path}/__init__.py",
                  os.path.join(version_dir, '__init__.py'))

    # layers内のファイル
    try:
        url = f"{GITHUB_API_BASE}/contents/{base_path}/layers"
        req = urllib.request.Request(url, headers={'User-Agent': 'WoWsMinimapRenderer'})
        with urllib.request.urlopen(req, timeout=10) as response:
            files = json.loads(response.read().decode())
            for f in files:
                if f['name'].endswith('.py'):
                    download_file(f['download_url'], os.path.join(layers_dir, f['name']))
    except Exception as e:
        print(f"Error downloading layers: {e}")

    # resources内のファイル
    try:
        url = f"{GITHUB_API_BASE}/contents/{base_path}/resources"
        req = urllib.request.Request(url, headers={'User-Agent': 'WoWsMinimapRenderer'})
        with urllib.request.urlopen(req, timeout=10) as response:
            files = json.loads(response.read().decode())
            for f in files:
                download_file(f['download_url'], os.path.join(resources_dir, f['name']))
    except Exception as e:
        print(f"Error downloading resources: {e}")

def download_file(url, target_path):
    """ファイルをダウンロードして保存"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WoWsMinimapRenderer'})
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(target_path, 'wb') as f:
                f.write(response.read())
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def version_sort_key(v):
    """バージョン文字列をソート用の数値タプルに変換"""
    try:
        return tuple(int(n) for n in v.split('_'))
    except:
        return (0,)

def merge_ships_to_default():
    """全バージョンのships.jsonを統合してデフォルトを最新化する"""
    try:
        if getattr(sys, 'frozen', False):
            renderer_dir = os.path.join(BASE_DIR, 'renderer')
            version_dirs = [os.path.join(renderer_dir, 'versions')]
            update_versions_dir = os.path.join(EXE_DIR, '_update', 'renderer', 'versions')
            if os.path.exists(update_versions_dir):
                version_dirs.append(update_versions_dir)
        else:
            import renderer
            renderer_dir = os.path.dirname(renderer.__file__)
            version_dirs = [os.path.join(renderer_dir, 'versions')]

        default_path = os.path.join(renderer_dir, 'resources', 'ships.json')

        merged = {}
        for versions_dir in version_dirs:
            if not os.path.exists(versions_dir):
                continue
            for v in sorted(os.listdir(versions_dir), key=version_sort_key):
                ships_path = os.path.join(versions_dir, v, 'resources', 'ships.json')
                if os.path.exists(ships_path):
                    with open(ships_path, 'r', encoding='utf-8') as f:
                        merged.update(json.load(f))

        if merged:
            with open(default_path, 'w', encoding='utf-8') as f:
                json.dump(merged, f, ensure_ascii=False)
            print(f"ships.json merged: {len(merged)} ships")

        # achievements.json も同様にマージ
        merged_ach = {}
        for versions_dir in version_dirs:
            if not os.path.exists(versions_dir):
                continue
            for v in sorted(os.listdir(versions_dir), key=version_sort_key):
                ach_path = os.path.join(versions_dir, v, 'resources', 'achievements.json')
                if os.path.exists(ach_path):
                    with open(ach_path, 'r', encoding='utf-8') as f:
                        merged_ach.update(json.load(f))

        if merged_ach:
            ach_default = os.path.join(renderer_dir, 'resources', 'achievements.json')
            with open(ach_default, 'w', encoding='utf-8') as f:
                json.dump(merged_ach, f, ensure_ascii=False)
            print(f"achievements.json merged: {len(merged_ach)} entries")
    except Exception as e:
        print(f"merge_ships_to_default error: {e}")

GITHUB_REPO = "SakanawaFuris/WoWsMinimapRendererEZ"
_github_pat = None

def _get_github_pat():
    global _github_pat
    if _github_pat:
        return _github_pat
    pat_file = os.path.join(BASE_DIR, 'github_pat.txt')
    if os.path.exists(pat_file):
        with open(pat_file) as f:
            _github_pat = f.read().strip()
    return _github_pat

def _github_api(path):
    url = f"https://api.github.com/{path}"
    req = urllib.request.Request(url)
    pat = _get_github_pat()
    if pat:
        req.add_header("Authorization", f"Bearer {pat}")
    req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read())

def _get_local_hash():
    """ローカルのコミットハッシュを取得（exe版はVERSIONファイル、開発版はgit）"""
    if getattr(sys, 'frozen', False):
        version_file = os.path.join(EXE_DIR, 'VERSION')
        if os.path.exists(version_file):
            with open(version_file) as f:
                return f.read().strip()
        return None
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=BASE_DIR
        ).decode().strip()
    except Exception:
        return None

@app.route('/api/check-update')
def check_update():
    """GitHubのmainブランチと現在のコミットを比較して更新確認"""
    try:
        local_hash = _get_local_hash()
        if not local_hash:
            return jsonify({'status': 'error', 'message': 'バージョン情報が取得できませんでした'})
        data = _github_api(f"repos/{GITHUB_REPO}/commits/main")
        remote_hash = data['sha']
        has_update = local_hash != remote_hash
        return jsonify({
            'status': 'success',
            'has_update': has_update,
            'local_hash': local_hash[:7],
            'remote_hash': remote_hash[:7],
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/update', methods=['POST'])
def apply_update():
    """git pullで更新してプロセスを再起動"""
    try:
        result = subprocess.run(
            ['git', 'pull'], cwd=BASE_DIR,
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return jsonify({'status': 'error', 'message': result.stderr})
        def restart():
            time.sleep(1)
            os.execv(sys.executable, [sys.executable] + sys.argv)
        Thread(target=restart, daemon=True).start()
        return jsonify({'status': 'success', 'message': '更新しました。再起動します...'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def do_update(versions):
    """実際の更新処理"""
    global update_status
    update_status = {'updating': True, 'progress': 0, 'message': '更新を開始...'}

    try:
        if getattr(sys, 'frozen', False):
            # EXE化されている場合、EXE_DIR内に更新用ディレクトリを作成
            versions_dir = os.path.join(EXE_DIR, '_update', 'renderer', 'versions')
        else:
            import renderer
            versions_dir = os.path.join(os.path.dirname(renderer.__file__), 'versions')

        os.makedirs(versions_dir, exist_ok=True)

        total = len(versions)
        for i, version in enumerate(versions):
            update_status['message'] = f'{version} をダウンロード中...'
            update_status['progress'] = int((i / total) * 100)
            download_version_files(version, versions_dir)

        merge_ships_to_default()
        update_status['progress'] = 100
        update_status['message'] = '更新完了！アプリを再起動してください。'
        update_status['updating'] = False

    except Exception as e:
        update_status['message'] = f'エラー: {str(e)}'
        update_status['updating'] = False

@app.route('/api/update-status')
def get_update_status():
    """更新処理の進捗を取得"""
    return jsonify(update_status)

@app.route('/')
def index():
    """メイン画面を表示"""
    return render_template('index.html', socket_io_path=_socketio_path)

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
            'video_url': f'{SUBPATH}/videos/{video_filename}'
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

    if is_frozen:
        # EXE版の場合：本番用サーバーとして起動（警告を抑制）
        import logging

        # Werkzeugの警告ログを抑制
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # ブラウザを開く
        Timer(1, open_browser).start()

        # 本番用の情報を表示
        print('=' * 50)
        print('  WoWs Minimap Renderer v1.0.0')
        print('=' * 50)
        print('ブラウザで http://localhost:5000 が開きます')
        print('終了するには Ctrl+C を押してください')
        print('=' * 50)
        print()

        # Socket.IOサーバーで起動（本番モード）
        socketio.run(app, debug=False, host='0.0.0.0', port=5000, log_output=False, allow_unsafe_werkzeug=True)
    elif SUBPATH:
        # サーバーモード（リバースプロキシ経由）：localhost専用・ブラウザ起動なし
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        merge_ships_to_default()

        print('=' * 50)
        print('  WoWs Minimap Renderer - Server Mode')
        print('=' * 50)
        print(f'Subpath: {SUBPATH}')
        print(f'Listening on: http://127.0.0.1:5001')
        print('終了するには Ctrl+C を押してください')
        print('=' * 50)

        socketio.run(app, debug=False, host='127.0.0.1', port=5001, log_output=False, allow_unsafe_werkzeug=True)
    else:
        # 開発環境の場合：Flaskの開発サーバーを使用
        # Flaskのreloaderによる複数起動を防ぐ
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            Timer(1, open_browser).start()

        # Flaskアプリを起動（開発モード）
        socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
