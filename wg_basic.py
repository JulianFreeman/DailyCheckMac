# coding: utf8
from PySide6 import QtWidgets, QtCore, QtGui
from util_func import (
    get_isp_name,
)


class UiWgBasic(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.gbx_isp = QtWidgets.QGroupBox("网络运营商", window)
        self.vly_m.addWidget(self.gbx_isp)
        self.vly_gbx_isp = QtWidgets.QVBoxLayout()
        self.gbx_isp.setLayout(self.vly_gbx_isp)

        self.lne_isp = QtWidgets.QLineEdit(self.gbx_isp)
        self.lne_isp.setReadOnly(True)
        self.vly_gbx_isp.addWidget(self.lne_isp)

        self.vly_m.addStretch(1)


class WgBasic(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiWgBasic(self)

        self.ui.lne_isp.setText(get_isp_name())

    def update_safe(self, isp_safe_info: dict):

        def set_palette(is_safe: bool | None, lne_w: QtWidgets.QLineEdit):
            pal = lne_w.palette()
            if is_safe is True:
                pal.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.blue)
            elif is_safe is False:
                pal.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.red)
            else:
                pal.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.black)
            lne_w.setPalette(pal)

        isp_text = self.ui.lne_isp.text()
        if isp_text in isp_safe_info:
            is_isp_safe = isp_safe_info[isp_text]["safe"]
            set_palette(is_isp_safe, self.ui.lne_isp)

    def export_unknown(self) -> dict:
        unknown = {}
        text_role = QtGui.QPalette.ColorRole.Text
        black = QtCore.Qt.GlobalColor.black
        if self.ui.lne_isp.palette().color(text_role) == black:
            unknown["isp"] = self.ui.lne_isp.text()
        return unknown
