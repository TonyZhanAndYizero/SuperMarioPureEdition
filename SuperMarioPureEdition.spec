# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    [r'C:\Users\28600\Desktop\Mario6\SuperMarioPureEdition.py',r'C:\Users\28600\Desktop\Mario6\source\components\box.py',r'C:\Users\28600\Desktop\Mario6\source\components\brick.py',r'C:\Users\28600\Desktop\Mario6\source\components\coin.py',r'C:\Users\28600\Desktop\Mario6\source\components\enemy.py',r'C:\Users\28600\Desktop\Mario6\source\components\flagpole.py',r'C:\Users\28600\Desktop\Mario6\source\components\info.py',r'C:\Users\28600\Desktop\Mario6\source\components\player.py',r'C:\Users\28600\Desktop\Mario6\source\components\powerup.py',r'C:\Users\28600\Desktop\Mario6\source\components\stuff.py',r'C:\Users\28600\Desktop\Mario6\source\states\level.py',r'C:\Users\28600\Desktop\Mario6\source\states\load_screen.py',r'C:\Users\28600\Desktop\Mario6\source\states\main_menu.py',r'C:\Users\28600\Desktop\Mario6\source\consts.py',r'C:\Users\28600\Desktop\Mario6\source\setup.py',r'C:\Users\28600\Desktop\Mario6\source\sound.py',r'C:\Users\28600\Desktop\Mario6\source\tools.py'],
    pathex=[r'C:\Users\28600\Desktop\Mario6'],
    binaries=[],
    datas=[(r'C:\Users\28600\Desktop\Mario6\resources','resources'),(r'C:\Users\28600\Desktop\Mario6\source','source')],
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SuperMarioPureEdition',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[r'C:\Users\28600\Desktop\Mario6\smoke.ico'],
)
