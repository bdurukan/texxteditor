# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['config', 'config.settings', 'audio', 'audio.recorder', 'audio.transcription', 
                   'audio.system_capture', 'dialogs', 'dialogs.api_key_dialog', 
                   'dialogs.shortcut_editor', 'dialogs.system_audio_dialog', 'file', 
                   'file.operations', 'text', 'text.formatter', 'text.search', 
                   'text.statistics', 'text.editor', 'text.handler', 'text.selection',
                   'ui', 'ui.theme', 'ui.document', 'ui.toolbar', 'ui.statusbar', 
                   'ui.canvas_manager', 'main'],
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
    name='TeXXtEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='C:\\Users\\Admin\\Desktop\\text_to_speech_icon_135108.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TeXXtEditor',
)