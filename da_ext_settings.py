# coding: utf8
from PySide6 import QtWidgets, QtCore


class PushButtonWithId(QtWidgets.QPushButton):

    clicked_with_id = QtCore.Signal(str)

    def __init__(self, ids: str, parent: QtWidgets.QWidget = None, title: str = ""):
        super().__init__(title, parent)
        self.ids = ids
        self.clicked.connect(self.on_self_clicked)

    def on_self_clicked(self):
        self.clicked_with_id.emit(self.ids)


class DaExtSettings(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("设置")

        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)

        self.gbx_exec = QtWidgets.QGroupBox("执行文件路径", self)
        self.vly_m.addWidget(self.gbx_exec)

        self.gly_gbx_exec = QtWidgets.QGridLayout()
        self.gbx_exec.setLayout(self.gly_gbx_exec)

        self.lb_exec_chrome = QtWidgets.QLabel("Chrome", self)
        self.lb_exec_edge = QtWidgets.QLabel("Edge", self)
        self.lb_exec_brave = QtWidgets.QLabel("Brave", self)
        self.lne_exec_chrome = QtWidgets.QLineEdit(self)
        self.lne_exec_edge = QtWidgets.QLineEdit(self)
        self.lne_exec_brave = QtWidgets.QLineEdit(self)
        self.pbn_exec_chrome = PushButtonWithId("ChromeExec", self, "选择")
        self.pbn_exec_edge = PushButtonWithId("EdgeExec", self, "选择")
        self.pbn_exec_brave = PushButtonWithId("BraveExec", self, "选择")

        self.gly_gbx_exec.addWidget(self.lb_exec_chrome, 0, 0)
        self.gly_gbx_exec.addWidget(self.lb_exec_edge, 1, 0)
        self.gly_gbx_exec.addWidget(self.lb_exec_brave, 2, 0)
        self.gly_gbx_exec.addWidget(self.lne_exec_chrome, 0, 1)
        self.gly_gbx_exec.addWidget(self.lne_exec_edge, 1, 1)
        self.gly_gbx_exec.addWidget(self.lne_exec_brave, 2, 1)
        self.gly_gbx_exec.addWidget(self.pbn_exec_chrome, 0, 2)
        self.gly_gbx_exec.addWidget(self.pbn_exec_edge, 1, 2)
        self.gly_gbx_exec.addWidget(self.pbn_exec_brave, 2, 2)

        self.gbx_data = QtWidgets.QGroupBox("用户数据路径", self)
        self.vly_m.addWidget(self.gbx_data)

        self.gly_gbx_data = QtWidgets.QGridLayout()
        self.gbx_data.setLayout(self.gly_gbx_data)

        self.lb_data_chrome = QtWidgets.QLabel("Chrome", self)
        self.lb_data_edge = QtWidgets.QLabel("Edge", self)
        self.lb_data_brave = QtWidgets.QLabel("Brave", self)
        self.lne_data_chrome = QtWidgets.QLineEdit(self)
        self.lne_data_edge = QtWidgets.QLineEdit(self)
        self.lne_data_brave = QtWidgets.QLineEdit(self)
        self.pbn_data_chrome = PushButtonWithId("ChromeData", self, "选择")
        self.pbn_data_edge = PushButtonWithId("EdgeData", self, "选择")
        self.pbn_data_brave = PushButtonWithId("BraveData", self, "选择")

        self.gly_gbx_data.addWidget(self.lb_data_chrome, 0, 0)
        self.gly_gbx_data.addWidget(self.lb_data_edge, 1, 0)
        self.gly_gbx_data.addWidget(self.lb_data_brave, 2, 0)
        self.gly_gbx_data.addWidget(self.lne_data_chrome, 0, 1)
        self.gly_gbx_data.addWidget(self.lne_data_edge, 1, 1)
        self.gly_gbx_data.addWidget(self.lne_data_brave, 2, 1)
        self.gly_gbx_data.addWidget(self.pbn_data_chrome, 0, 2)
        self.gly_gbx_data.addWidget(self.pbn_data_edge, 1, 2)
        self.gly_gbx_data.addWidget(self.pbn_data_brave, 2, 2)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.pbn_save = QtWidgets.QPushButton("保存", self)
        self.pbn_cancel = QtWidgets.QPushButton("取消", self)

        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_save)
        self.hly_bot.addWidget(self.pbn_cancel)

        self.vly_m.addLayout(self.hly_bot)
        self.vly_m.addStretch(1)

        self.pbn_save.clicked.connect(self.on_pbn_save_clicked)
        self.pbn_cancel.clicked.connect(self.on_pbn_cancel_clicked)

        self.pbn_exec_chrome.clicked_with_id.connect(self.on_pbn_exec_n_clicked_with_id)
        self.pbn_exec_edge.clicked_with_id.connect(self.on_pbn_exec_n_clicked_with_id)
        self.pbn_exec_brave.clicked_with_id.connect(self.on_pbn_exec_n_clicked_with_id)

        self.pbn_data_chrome.clicked_with_id.connect(self.on_pbn_data_n_clicked_with_id)
        self.pbn_data_edge.clicked_with_id.connect(self.on_pbn_data_n_clicked_with_id)
        self.pbn_data_brave.clicked_with_id.connect(self.on_pbn_data_n_clicked_with_id)

        self.read_settings()

    def sizeHint(self):
        return QtCore.QSize(540, 140)

    def read_settings(self):
        us = QtCore.QSettings()
        chrome_exec = str(us.value("ChromeExec", ""))
        edge_exec = str(us.value("EdgeExec", ""))
        brave_exec = str(us.value("BraveExec", ""))

        chrome_data = str(us.value("ChromeData", ""))
        edge_data = str(us.value("EdgeData", ""))
        brave_data = str(us.value("BraveData", ""))

        self.lne_exec_chrome.setText(chrome_exec)
        self.lne_exec_edge.setText(edge_exec)
        self.lne_exec_brave.setText(brave_exec)

        self.lne_data_chrome.setText(chrome_data)
        self.lne_data_edge.setText(edge_data)
        self.lne_data_brave.setText(brave_data)

    def on_pbn_exec_n_clicked_with_id(self, ids: str):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, f"选择 {ids}")
        if len(filename) == 0:
            return
        if ids == "ChromeExec":
            self.lne_exec_chrome.setText(filename)
        elif ids == "EdgeExec":
            self.lne_exec_edge.setText(filename)
        elif ids == "BraveExec":
            self.lne_exec_brave.setText(filename)

    def on_pbn_data_n_clicked_with_id(self, ids: str):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, f"选择 {ids}")
        if len(dirname) == 0:
            return
        if ids == "ChromeData":
            self.lne_data_chrome.setText(dirname)
        elif ids == "EdgeData":
            self.lne_data_edge.setText(dirname)
        elif ids == "BraveData":
            self.lne_data_brave.setText(dirname)

    def on_pbn_save_clicked(self):
        us = QtCore.QSettings()
        us.setValue("ChromeExec", self.lne_exec_chrome.text())
        us.setValue("EdgeExec", self.lne_exec_edge.text())
        us.setValue("BraveExec", self.lne_exec_brave.text())

        us.setValue("ChromeData", self.lne_data_chrome.text())
        us.setValue("EdgeData", self.lne_data_edge.text())
        us.setValue("BraveData", self.lne_data_brave.text())

        self.accept()

    def on_pbn_cancel_clicked(self):
        self.reject()
