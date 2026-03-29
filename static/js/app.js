// Socket.IO接続（サブパス対応: SOCKET_IO_PATHはindex.htmlで定義）
const socket = io({path: typeof SOCKET_IO_PATH !== 'undefined' ? SOCKET_IO_PATH : '/socket.io'});

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

// Socket.IOイベントハンドラ
socket.on('progress', (data) => {
    console.log('Progress:', data);
    updateProgress(data.percent, data.message);
});

socket.on('complete', (data) => {
    console.log('Complete:', data);
    showResult(data.video_url);
});

socket.on('error', (data) => {
    console.log('Error:', data);
    showError(data.error);
});

// Socket.IO接続状態のログ
socket.on('connect', () => {
    console.log('Socket.IO connected');
});

socket.on('disconnect', () => {
    console.log('Socket.IO disconnected');
});

// フォーム送信時の処理
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(uploadForm);

    // UIをリセット
    hideAllSections();
    progressSection.classList.remove('hidden');

    // 進捗を0%に
    updateProgress(0, '処理を開始しています...');

    try {
        const response = await fetch('./upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            showError(data.error);
        } else if (data.job_id) {
            // ポーリング開始
            pollStatus(data.job_id);
        }
    } catch (error) {
        showError('処理中にエラーが発生しました: ' + error.message);
    }
});

// ステータスをポーリングする関数
function pollStatus(jobId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`./status/${jobId}`);
            const data = await response.json();

            console.log('Status:', data);

            if (data.status === 'processing') {
                updateProgress(data.percent, data.message);
            } else if (data.status === 'complete') {
                clearInterval(interval);
                updateProgress(100, '完了しました');
                setTimeout(() => showResult(data.video_url), 500);
            } else if (data.status === 'error') {
                clearInterval(interval);
                showError(data.error);
            }
        } catch (error) {
            clearInterval(interval);
            showError('ステータスの取得に失敗しました: ' + error.message);
        }
    }, 500); // 500msごとにポーリング
}

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

function updateProgress(percent, message) {
    progressFill.style.width = percent + '%';
    if (message) {
        progressText.textContent = `${Math.round(percent)}% - ${message}`;
    } else {
        progressText.textContent = Math.round(percent) + '%';
    }
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

// ===== 更新チェック機能 =====
const updateBanner = document.getElementById('updateBanner');
const updateMessage = document.getElementById('updateMessage');
const updateBtn = document.getElementById('updateBtn');
const dismissBtn = document.getElementById('dismissBtn');
const updateProgressSection = document.getElementById('updateProgress');
const updateProgressFill = document.getElementById('updateProgressFill');
const updateProgressText = document.getElementById('updateProgressText');

// ステータスバー要素
const updateStatusBar = document.getElementById('updateStatusBar');
const updateStatusIcon = document.getElementById('updateStatusIcon');
const updateStatusText = document.getElementById('updateStatusText');

/**
 * ステータスバーの状態を更新
 * @param {'checking' | 'success' | 'update-available' | 'error'} status
 * @param {string} message
 */
function setUpdateStatus(status, message) {
    // すべての状態クラスを削除
    updateStatusBar.classList.remove('checking', 'success', 'update-available', 'error');
    updateStatusBar.classList.add(status);

    // アイコンを設定
    const icons = {
        'checking': '⏳',
        'success': '✅',
        'update-available': '🔔',
        'error': '⚠️'
    };
    updateStatusIcon.textContent = icons[status] || '❓';
    updateStatusText.textContent = message;
}

// 起動時にバージョンを表示
document.addEventListener('DOMContentLoaded', () => {
    checkForUpdates();
});

async function checkForUpdates() {
    try {
        const response = await fetch('./api/check-update');
        const data = await response.json();

        console.log('Update check:', data);

        // エラーが返された場合
        if (data.status === 'error') {
            setUpdateStatus('error', `確認失敗: ${data.error}`);
            return;
        }

        // 更新がある場合
        if (data.has_update) {
            setUpdateStatus('update-available', `更新があります (${data.local_hash} → ${data.remote_hash})`);
            updateMessage.textContent = `GitHubに新しい更新があります。`;
            updateBanner.classList.remove('hidden');
        } else {
            setUpdateStatus('success', `最新の状態です (${data.local_hash})`);
        }
    } catch (error) {
        console.log('Update check failed:', error);
        setUpdateStatus('error', `確認失敗: ネットワークエラー`);
    }
}

// 更新ボタンのクリック処理
updateBtn.addEventListener('click', async () => {
    updateBtn.disabled = true;
    updateBtn.textContent = '更新中...';
    dismissBtn.classList.add('hidden');
    updateProgressSection.classList.remove('hidden');

    try {
        const response = await fetch('./api/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await response.json();

        if (data.error) {
            updateProgressText.textContent = 'エラー: ' + data.error;
            updateBtn.disabled = false;
            updateBtn.textContent = '再試行';
        } else {
            pollUpdateStatus();
        }
    } catch (error) {
        updateProgressText.textContent = 'エラー: ' + error.message;
        updateBtn.disabled = false;
        updateBtn.textContent = '再試行';
    }
});

// 更新進捗のポーリング
function pollUpdateStatus() {
    const interval = setInterval(async () => {
        try {
            const response = await fetch('./api/update-status');
            const data = await response.json();

            updateProgressFill.style.width = data.progress + '%';
            updateProgressText.textContent = data.message;

            if (!data.updating && data.progress === 100) {
                clearInterval(interval);
                updateBtn.textContent = '完了';
                updateMessage.textContent = '更新が完了しました。アプリを再起動してください。';
            } else if (!data.updating && data.message.startsWith('エラー')) {
                clearInterval(interval);
                updateBtn.disabled = false;
                updateBtn.textContent = '再試行';
            }
        } catch (error) {
            console.log('Update status check failed:', error);
        }
    }, 500);
}

// 後でボタン
dismissBtn.addEventListener('click', () => {
    updateBanner.classList.add('hidden');
});
