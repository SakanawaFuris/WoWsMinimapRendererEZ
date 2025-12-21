@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ===============================================
echo  WoWs Minimap Renderer 配布版作成スクリプト
echo ===============================================
echo.

REM 日付取得
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set DATE=%%a%%b%%c)
set VERSION=v%DATE:~2,6%

echo [1/5] クリーンアップ中...
if exist build rmdir /s /q build
if exist release rmdir /s /q release
mkdir release

echo.
echo [2/5] EXEファイルをビルド中...
call .\venv\Scripts\pyinstaller minimap_renderer_gui.spec --clean
if errorlevel 1 (
    echo エラー: EXEビルドに失敗しました
    pause
    exit /b 1
)

echo.
echo [3/5] README.txtを追加中...
copy /y dist\WoWsMinimapRenderer\README.txt dist\WoWsMinimapRenderer\README.txt >nul

echo.
echo [4/5] ZIP配布版を作成中...
powershell -Command "Compress-Archive -Path 'dist\WoWsMinimapRenderer\*' -DestinationPath 'release\WoWsMinimapRenderer_%VERSION%.zip' -Force"
if errorlevel 1 (
    echo エラー: ZIP作成に失敗しました
    pause
    exit /b 1
)

echo.
echo [5/5] インストーラーを確認中...
where iscc >nul 2>&1
if errorlevel 1 (
    echo 注意: Inno Setupがインストールされていません
    echo インストーラーの作成をスキップします
    echo ZIP配布版のみ作成されました: release\WoWsMinimapRenderer_%VERSION%.zip
) else (
    echo Inno Setupでインストーラーを作成中...
    iscc installer.iss
    if errorlevel 1 (
        echo エラー: インストーラー作成に失敗しました
        pause
        exit /b 1
    )
    echo.
    echo ===============================================
    echo  配布版作成完了！
    echo ===============================================
    echo.
    echo 作成されたファイル:
    echo - ZIP配布版: release\WoWsMinimapRenderer_%VERSION%.zip
    dir /b release\*.exe 2>nul && (
        echo - インストーラー: release\WoWsMinimapRenderer_Setup_%VERSION%.exe
    )
    goto :end
)

:end
echo.
echo ===============================================
pause
