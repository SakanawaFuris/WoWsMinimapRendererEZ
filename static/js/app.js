// Socket.IO接続
const socket = io();

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
        const response = await fetch('/upload', {
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
            const response = await fetch(`/status/${jobId}`);
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
