import os
import sys
import threading
import webbrowser
import streamlit.web.cli as stcli


def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def open_browser():
    webbrowser.open("http://localhost:8501")


if __name__ == "__main__":

    threading.Timer(1.5, open_browser).start()

    main_script = resource_path("main.py")

    sys.argv = [
        "streamlit",
        "run",
        main_script,
        "--server.headless=true",
        "--global.developmentMode=false",
    ]

    sys.exit(stcli.main())