# coding: utf8
import os.path

from PySide6 import QtWidgets, QtCore, QtGui
from util_func import (
    get_mac_installed_software,
)
from global_vars import (
    SoftwareStatusRole,
)


class UiWgSoftware(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)
        self.cbx_safe = QtWidgets.QCheckBox("安全", window)
        self.cbx_unsafe = QtWidgets.QCheckBox("不安全", window)
        self.cbx_unknown = QtWidgets.QCheckBox("未知", window)
        self.cbx_safe.setChecked(True)
        self.cbx_unsafe.setChecked(True)
        self.cbx_unknown.setChecked(True)
        self.hly_top.addWidget(self.cbx_safe)
        self.hly_top.addWidget(self.cbx_unsafe)
        self.hly_top.addWidget(self.cbx_unknown)
        self.hly_top.addStretch(1)

        self.lv_software = QtWidgets.QListView(window)
        self.vly_m.addWidget(self.lv_software)


class SoftwareListModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_software = {}  # type: dict[str, str]
        self.names = []  # type: list[str]
        self.icons = {}  # type: dict[str, QtGui.QIcon]
        self.safe_info = {}
        self.blank_icon = QtGui.QIcon(":/images/blank_128.png")
        self.update()

    def update(self):
        self.all_software.clear()
        self.names.clear()
        self.icons.clear()

        self.all_software = get_mac_installed_software()
        for s in self.all_software:
            self.names.append(s)
            ic = self.all_software[s]
            if len(ic) == 0 or not os.path.exists(ic):
                self.icons[s] = self.blank_icon
            else:
                self.icons[s] = QtGui.QIcon(ic)
        self.names.sort(key=lambda x: x.lower())

    def update_safe_info(self, safe_info: dict):
        self.safe_info.clear()
        self.safe_info = safe_info

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.names)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        row = index.row()
        name = self.names[row]

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return name
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            return self.icons[name]
        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            is_safe = self.data(index, SoftwareStatusRole)
            if is_safe is True:
                return QtGui.QBrush(QtGui.QColor("lightgreen"))
            elif is_safe is False:
                return QtGui.QBrush(QtGui.QColor("lightpink"))
            else:
                return QtGui.QBrush(QtCore.Qt.BrushStyle.NoBrush)
        if role == SoftwareStatusRole:
            if name not in self.safe_info:
                return None
            else:
                return self.safe_info[name]["safe"]


class WgSoftware(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiWgSoftware(self)

        self.software_list_model = SoftwareListModel(self)
        self.ui.lv_software.setModel(self.software_list_model)

        self.ui.cbx_safe.clicked.connect(self.on_cbx_safe_clicked)
        self.ui.cbx_unsafe.clicked.connect(self.on_cbx_unsafe_clicked)
        self.ui.cbx_unknown.clicked.connect(self.on_cbx_unknown_clicked)

    def filters_clicked(self, safe_mark: bool | None, checked: bool):
        for row in range(self.software_list_model.rowCount()):
            idx = self.software_list_model.index(row)
            is_safe = self.software_list_model.data(idx, SoftwareStatusRole)
            if is_safe is safe_mark:
                self.ui.lv_software.setRowHidden(row, not checked)

    def on_cbx_safe_clicked(self, checked: bool):
        self.filters_clicked(True, checked)

    def on_cbx_unsafe_clicked(self, checked: bool):
        self.filters_clicked(False, checked)

    def on_cbx_unknown_clicked(self, checked: bool):
        self.filters_clicked(None, checked)

    def update_safe(self, safe_info: dict):
        self.software_list_model.update_safe_info(safe_info)

    def export_unknown(self) -> list[str]:
        unknown_software = []
        for row in range(self.software_list_model.rowCount()):
            idx = self.software_list_model.index(row)
            is_safe = self.software_list_model.data(idx, SoftwareStatusRole)
            if is_safe is None:
                name = self.software_list_model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole)
                unknown_software.append(name)

        return unknown_software
