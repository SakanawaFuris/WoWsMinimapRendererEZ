@echo off
echo ========================================
echo WoWs Minimap Renderer Update Script
echo ========================================
echo.

echo [1/5] Checking current version...
call venv\Scripts\pip show minimap-renderer | findstr "Version"
echo.

echo [2/5] Updating minimap_renderer...
call venv\Scripts\pip install --upgrade --force-reinstall git+https://github.com/WoWs-Builder-Team/minimap_renderer.git
if errorlevel 1 (
    echo ERROR: Failed to update minimap_renderer
    pause
    exit /b 1
)
echo.

echo [3/5] Testing the application...
echo Starting Flask app for 10 seconds...
start /B venv\Scripts\python app.py
timeout /t 10 /nobreak > nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *" > nul 2>&1
echo Test complete.
echo.

echo [4/5] Rebuilding exe...
if exist dist rmdir /S /Q dist
if exist build rmdir /S /Q build
call venv\Scripts\pyinstaller minimap_renderer_gui.spec
if errorlevel 1 (
    echo ERROR: Failed to build exe
    pause
    exit /b 1
)
echo.

echo [5/5] Creating distribution package...
call venv\Scripts\python -c "import zipfile, os; from pathlib import Path; from datetime import datetime; version = datetime.now().strftime('%%Y%%m%%d'); zip_name = f'WoWsMinimapRenderer_v{version}.zip'; z = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED); z.write('README.md', 'WoWsMinimapRenderer/README.md'); [z.write(f, 'WoWsMinimapRenderer/' + str(f.relative_to('dist'))) for f in Path('dist/WoWsMinimapRenderer').rglob('*') if f.is_file()]; z.close(); print(f'Created: {zip_name}'); print(f'Size: {os.path.getsize(zip_name) / 1024 / 1024:.1f} MB')"
echo.

echo ========================================
echo Update and build completed successfully!
echo ========================================
echo.
echo Check the dist folder for the new executable.
echo Check the root folder for the new ZIP package.
pause
