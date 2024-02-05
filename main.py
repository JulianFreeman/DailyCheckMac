# coding: utf8
import os
import sys
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from mw_dailycheck import MwDailyCheck

import daily_check_rc

version = (1, 0, 1)

ORG_NAME = "JnPrograms"
APP_NAME = "DailyCheck"


def set_default_settings():
    plat = sys.platform
    user_path = os.path.expanduser("~")
    user_data_path_map = {
        "win32": {
            "Chrome": str(Path(user_path, r"AppData\Local\Google\Chrome\User Data")),
            "Edge": str(Path(user_path, r"AppData\Local\Microsoft\Edge\User Data")),
            "Brave": str(Path(user_path, r"AppData\Local\BraveSoftware\Brave-Browser\User Data")),
        },
        "darwin": {
            "Chrome": str(Path(user_path, "Library/Application Support/Google/Chrome")),
            "Edge": str(Path(user_path, "Library/Application Support/Microsoft Edge")),
            "Brave": str(Path(user_path, "Library/Application Support/BraveSoftware/Brave-Browser")),
        },
    }
    exec_path_map = {
        "win32": {
            "Chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "Edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "Brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        },
        "darwin": {
            "Chrome": r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "Edge": r"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "Brave": r"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        },
    }
    user_data_path = user_data_path_map[plat]
    exec_path = exec_path_map[plat]
    settings_map = {
        "ChromeExec": exec_path["Chrome"],
        "EdgeExec": exec_path["Edge"],
        "BraveExec": exec_path["Brave"],
        "ChromeData": user_data_path["Chrome"],
        "EdgeData": user_data_path["Edge"],
        "BraveData": user_data_path["Brave"],
    }
    us = QtCore.QSettings()
    exist_keys = us.childKeys()
    for s in settings_map:
        if s not in exist_keys:
            us.setValue(s, settings_map[s])
            # print(f"Add key {s}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)

    set_default_settings()

    win = MwDailyCheck(version)
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
