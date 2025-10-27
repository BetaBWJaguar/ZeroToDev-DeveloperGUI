# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo,
    VarFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarStruct,
    FixedFileInfo,
)

with open('version.txt', 'r', encoding='utf-8') as f:
    version_info_code = f.read()

version_info = eval(version_info_code)


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('langs', 'langs'), ('language_manager', 'language_manager'), ('utils', 'utils'), ('ffmpeg', 'ffmpeg'), ('fragments', 'fragments'), ('markup', 'markup'), ('media_formats', 'media_formats'), ('voicegui', 'voicegui'), ('tts', 'tts')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)


exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZeroToDev-DEVGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    version=version_info

)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZeroToDev'
)