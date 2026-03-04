import os
import sys
import threading
import webbrowser
import streamlit.web.cli as stcli


def open_browser():
    webbrowser.open("http://localhost:8501")


if __name__ == "__main__":

    # open browser after server starts
    threading.Timer(1.5, open_browser).start()

    sys.argv = [
        "streamlit",
        "run",
        os.path.join(os.path.dirname(__file__), "main.py"),
        "--server.headless=true",
        "--global.developmentMode=false",
    ]

    sys.exit(stcli.main())