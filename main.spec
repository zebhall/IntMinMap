# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Zeb\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\customtkinter', 'customtkinter/'),('C:\\Users\\Zeb\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\CTkColorPicker', 'CTkColorPicker/'),("icons","icons")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
    icon=['icons\\pss_o.ico'],
)
