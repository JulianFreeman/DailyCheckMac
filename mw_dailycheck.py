# coding: utf8
import json
from pathlib import Path
from datetime import datetime
from PySide6 import QtWidgets, QtGui, QtCore
from wg_basic import WgBasic
from wg_software import WgSoftware
from wg_extensions import WgExtensions
from global_vars import (
    request_content,
    accept_warning,
)


class UiMwDailyCheck(object):

    def __init__(self, window: QtWidgets.QMainWindow):

        self.cw = QtWidgets.QWidget(window)
        window.setCentralWidget(self.cw)

        self.vly_m = QtWidgets.QVBoxLayout()
        self.cw.setLayout(self.vly_m)
        self.tw_m = QtWidgets.QTabWidget(self.cw)
        self.vly_m.addWidget(self.tw_m)
        self.wg_basic = WgBasic(self.cw)
        self.wg_software = WgSoftware(self.cw)
        self.wg_extensions = WgExtensions(self.cw)
        self.tw_m.addTab(self.wg_basic, "基本信息")
        self.tw_m.addTab(self.wg_software, "已安装软件")
        self.tw_m.addTab(self.wg_extensions, "已安装插件")

        self.menu_bar = window.menuBar()
        self.menu_help = self.menu_bar.addMenu("帮助")
        self.menu_about = self.menu_bar.addMenu("关于")

        self.act_update_safe = QtGui.QAction("更新安全标注", window)
        self.act_export_unknown = QtGui.QAction("导出未知", window)

        self.act_about = QtGui.QAction("关于", window)
        self.act_about_qt = QtGui.QAction("关于 Qt", window)

        self.menu_help.addActions([self.act_update_safe, self.act_export_unknown])
        self.menu_about.addActions([self.act_about, self.act_about_qt])


class MwDailyCheck(QtWidgets.QMainWindow):

    def __init__(self, version: tuple, parent=None):
        super().__init__(parent)
        self.version = version
        self.setWindowTitle("日常检查工具")
        self.setWindowIcon(QtGui.QIcon(":/images/dailycheck_128.png"))
        self.ui = UiMwDailyCheck(self)

        self.ui.act_update_safe.triggered.connect(self.on_act_update_safe_triggered)
        self.ui.act_export_unknown.triggered.connect(self.on_act_export_unknown_triggered)
        self.ui.act_about.triggered.connect(self.on_act_about_triggered)
        self.ui.act_about_qt.triggered.connect(self.on_act_about_qt_triggered)

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def on_act_about_triggered(self):
        msg = f"日常检查工具\n\n适用于 MacOS 平台。版本：{self.version[0]}.{self.version[1]}.{self.version[-1]}"
        QtWidgets.QMessageBox.about(self, "关于", msg)

    def on_act_about_qt_triggered(self):
        QtWidgets.QMessageBox.aboutQt(self, "关于 Qt")

    def on_act_update_safe_triggered(self):
        root_url = "https://julianfreeman.github.io/dailycheckutils"
        marks_all = request_content(f"{root_url}/marks_all.json").decode("utf8")
        if len(marks_all) == 0:
            return
        marks_all_d = json.loads(marks_all)
        self.ui.wg_software.update_safe(marks_all_d["software_mac"])
        self.ui.wg_extensions.update_safe(marks_all_d["extensions"])
        self.ui.wg_basic.update_safe(marks_all_d["isp"])

    def on_act_export_unknown_triggered(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "导出未知")
        if len(dirname) == 0:
            return
        now = datetime.strftime(datetime.now(), "%y%m%d%H%M")
        ex_file = Path(dirname, f"未知信息{now}.json")
        if accept_warning(self, ex_file.exists(), "警告", "文件已存在，确认覆盖吗？"):
            return

        unknown_software = self.ui.wg_software.export_unknown()
        unknown_ext = self.ui.wg_extensions.export_unknown()
        unknown_isp_manu = self.ui.wg_basic.export_unknown()

        unknown_all = {
            "software_mac": unknown_software,
            "extensions": unknown_ext,
        }
        unknown_all.update(unknown_isp_manu)

        ex_file.write_text(json.dumps(unknown_all, indent=4, ensure_ascii=False), "utf8")
        QtWidgets.QMessageBox.information(self, "提示", f"已导出到 {ex_file}")
