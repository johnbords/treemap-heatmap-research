# -*- mode: python ; coding: utf-8 -*-
import os
import streamlit
from PyInstaller.utils.hooks import collect_all, copy_metadata

block_cipher = None

# --- project files ---
datas = [
    ('main.py', '.'),
    ('controller', 'controller'),
    ('model', 'model'),
    ('view', 'view'),
    ('.streamlit/config.toml', '.streamlit'),
]
binaries = []
hiddenimports = []

# --- FORCE hidden import for this dependency ---
hiddenimports += ["streamlit_scroll_to_top"]

# --- metadata (needed for importlib.metadata.version calls) ---
datas += copy_metadata('streamlit')
datas += copy_metadata('plotly')
datas += copy_metadata('altair')
datas += copy_metadata('streamlit_scroll_to_top')

# --- collect packages (modules + binaries + package datas) ---
tmp = collect_all('streamlit')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

tmp = collect_all('plotly')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

tmp = collect_all('altair')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

tmp = collect_all('streamlit_scroll_to_top')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# --- HARD FORCE: Streamlit frontend static assets (fixes missing index.html) ---
streamlit_dir = os.path.dirname(streamlit.__file__)
datas += [
    (os.path.join(streamlit_dir, "static"), "streamlit/static"),
]

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,   # include binaries in the onefile
    a.datas,      # include datas in the onefile
    [],
    name='run_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
)