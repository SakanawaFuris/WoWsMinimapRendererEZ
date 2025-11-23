# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# データファイルを収集
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
]

# minimap_rendererのリソースも含める
import renderer
renderer_path = Path(renderer.__file__).parent
datas.append((str(renderer_path / 'resources'), 'renderer/resources'))
datas.append((str(renderer_path / 'layers'), 'renderer/layers'))
datas.append((str(renderer_path / 'versions'), 'renderer/versions'))

# replay_unpackのversionsディレクトリも含める
import replay_unpack
replay_unpack_path = Path(replay_unpack.__file__).parent
datas.append((str(replay_unpack_path / 'clients/wows/versions'), 'replay_unpack/clients/wows/versions'))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'flask',
        'flask_socketio',
        'socketio',
        'engineio',
        'engineio.async_drivers.threading',
        'eventlet',
        'dns',
        'dns.resolver',
        'dns.asyncresolver',
        'renderer',
        'renderer.render',
        'renderer.data',
        'renderer.resman',
        'renderer.conman',
        'renderer.base',
        'renderer.const',
        'renderer.utils',
        'renderer.exceptions',
        'renderer.shipbuilder',
        'replay_parser',
        'replay_unpack',
        'replay_unpack.clients',
        'replay_unpack.clients.wows',
        'replay_unpack.replay_reader',
        'replay_unpack.utils',
        'replay_unpack.core',
        'replay_unpack.core.network',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WoWsMinimapRenderer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # コンソールウィンドウを表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WoWsMinimapRenderer',
)
