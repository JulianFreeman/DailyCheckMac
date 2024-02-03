# coding: utf8
from PySide6 import QtWidgets, QtCore, QtGui
from util_ext import scan_extensions, ExtensionsData, ProfilesData
from global_vars import (
    ExtensionStatusRole,
    ExtensionIdRole,
)
from da_ext_settings import DaExtSettings
from da_show_profiles import DaShowProfiles


class UiWgExtensions(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)
        self.cmbx_browsers = QtWidgets.QComboBox(window)
        self.cbx_safe = QtWidgets.QCheckBox("安全", window)
        self.cbx_unsafe = QtWidgets.QCheckBox("不安全", window)
        self.cbx_unknown = QtWidgets.QCheckBox("未知", window)
        self.cbx_safe.setChecked(True)
        self.cbx_unsafe.setChecked(True)
        self.cbx_unknown.setChecked(True)
        self.cbx_compat = QtWidgets.QCheckBox("兼容模式", window)
        self.pbn_update = QtWidgets.QPushButton("更新", window)
        self.pbn_settings = QtWidgets.QPushButton("设置", window)
        self.hly_top.addWidget(self.cmbx_browsers)
        self.hly_top.addWidget(self.cbx_safe)
        self.hly_top.addWidget(self.cbx_unsafe)
        self.hly_top.addWidget(self.cbx_unknown)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.cbx_compat)
        self.hly_top.addWidget(self.pbn_update)
        self.hly_top.addWidget(self.pbn_settings)

        self.lv_extensions = QtWidgets.QListView(window)
        self.vly_m.addWidget(self.lv_extensions)


class BaseExtensionsListModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_profiles = {}  # type: ProfilesData
        self.all_extensions = {}  # type: ExtensionsData
        self.names = []  # type: list[tuple[str, str]]
        self.icons = {}  # type: dict[str, QtGui.QIcon]
        self.safe_info = {}  # type: dict[str, dict]
        self.blank_icon = QtGui.QIcon(":/images/blank_128.png")

        self.last_is_compat = False

    def update(self, is_compat=False):
        raise NotImplementedError

    def update_ext(self, browser: str, is_compat=False):
        """内部用"""
        self.all_profiles.clear()
        self.all_extensions.clear()
        self.names.clear()
        self.icons.clear()

        self.all_extensions, self.all_profiles = scan_extensions(browser, is_compat)
        self.last_is_compat = is_compat
        for ext_id in self.all_extensions:
            name = self.all_extensions[ext_id].name
            icon = self.all_extensions[ext_id].icon
            self.names.append((ext_id, name))
            if len(icon) == 0:
                self.icons[ext_id] = self.blank_icon
            else:
                self.icons[ext_id] = QtGui.QIcon(icon)
        self.names.sort(key=lambda x: x[1].lower())

        # print("updated " + browser)

    def update_safe_info(self, safe_info: dict):
        self.safe_info.clear()
        self.safe_info = safe_info

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.names)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        row = index.row()
        ext_id, name = self.names[row]

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return name
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            return self.icons[ext_id]
        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            is_safe = self.data(index, ExtensionStatusRole)
            if is_safe is True:
                return QtGui.QBrush(QtGui.QColor("lightgreen"))
            elif is_safe is False:
                return QtGui.QBrush(QtGui.QColor("lightpink"))
            else:
                return QtGui.QBrush(QtCore.Qt.BrushStyle.NoBrush)
        if role == ExtensionStatusRole:
            if ext_id not in self.safe_info:
                return None
            else:
                return self.safe_info[ext_id]["safe"]
        if role == ExtensionIdRole:
            return ext_id


class ChromeExtensionsListModel(BaseExtensionsListModel):

    def update(self, is_compat=False):
        super().update_ext("Chrome", is_compat)


class EdgeExtensionsListModel(BaseExtensionsListModel):

    def update(self, is_compat=False):
        super().update_ext("Edge", is_compat)


class BraveExtensionsListModel(BaseExtensionsListModel):

    def update(self, is_compat=False):
        super().update_ext("Brave", is_compat)


class BrowsersListModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.browsers = ["Chrome", "Edge", "Brave"]
        self.icons = [
            QtGui.QIcon(":/images/browsers/chrome_32.png"),
            QtGui.QIcon(":/images/browsers/edge_32.png"),
            QtGui.QIcon(":/images/browsers/brave_32.png"),
        ]

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.browsers)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        row = index.row()

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.browsers[row]
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            return self.icons[row]


class WgExtensions(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiWgExtensions(self)

        self.browsers_list_model = BrowsersListModel(self)
        self.ui.cmbx_browsers.setModel(self.browsers_list_model)

        self.ext_list_models: dict[str, BaseExtensionsListModel] = {
            "Chrome": ChromeExtensionsListModel(self),
            "Edge": EdgeExtensionsListModel(self),
            "Brave": BraveExtensionsListModel(self),
        }
        self.model_is_initial = {
            "Chrome": True,
            "Edge": True,
            "Brave": True,
        }
        self.switch_model(self.get_current_browser())

        self.ui.cbx_compat.clicked.connect(self.on_cbx_compat_clicked)
        self.ui.cmbx_browsers.currentTextChanged.connect(self.on_cmbx_browsers_current_text_changed)
        self.ui.cbx_safe.clicked.connect(self.on_cbx_safe_clicked)
        self.ui.cbx_unsafe.clicked.connect(self.on_cbx_unsafe_clicked)
        self.ui.cbx_unknown.clicked.connect(self.on_cbx_unknown_clicked)
        self.ui.pbn_update.clicked.connect(self.on_pbn_update_clicked)
        self.ui.pbn_settings.clicked.connect(self.on_pbn_settings_clicked)
        self.ui.lv_extensions.doubleClicked.connect(self.on_lv_extensions_double_clicked)

    def on_pbn_settings_clicked(self):
        da_es = DaExtSettings(self)
        da_es.exec()

    def get_current_browser(self) -> str:
        return self.ui.cmbx_browsers.currentData(QtCore.Qt.ItemDataRole.DisplayRole)

    def show_all_rows(self):
        # 在 update 之前调用
        self.filters_clicked(True, True)
        self.filters_clicked(False, True)
        self.filters_clicked(None, True)

    def apply_rows_hidden(self):
        # 在 update 之后调用
        self.filters_clicked(True, self.ui.cbx_safe.isChecked())
        self.filters_clicked(False, self.ui.cbx_unsafe.isChecked())
        self.filters_clicked(None, self.ui.cbx_unknown.isChecked())

    def update_model(self, browser: str):
        model = self.ext_list_models[browser]
        self.show_all_rows()
        model.update(is_compat=self.ui.cbx_compat.isChecked())
        self.apply_rows_hidden()

    def switch_model(self, browser: str):
        if self.model_is_initial[browser] is True:
            self.update_model(browser)
            self.model_is_initial[browser] = False

        model = self.ext_list_models[browser]
        self.show_all_rows()
        self.ui.lv_extensions.setModel(model)
        self.apply_rows_hidden()
        # 单纯的切换浏览器不一定会导致更新数据，所以需要同步兼容模式的设置
        self.ui.cbx_compat.setChecked(model.last_is_compat)

    def on_cbx_compat_clicked(self):
        self.update_model(self.get_current_browser())

    def on_cmbx_browsers_current_text_changed(self, text: str):
        self.switch_model(text)

    def filters_clicked(self, safe_mark: bool | None, checked: bool):
        model = self.ext_list_models[self.get_current_browser()]
        for row in range(model.rowCount()):
            idx = model.index(row)
            is_safe = model.data(idx, ExtensionStatusRole)
            if is_safe is safe_mark:
                self.ui.lv_extensions.setRowHidden(row, not checked)

    def on_cbx_safe_clicked(self, checked: bool):
        self.filters_clicked(True, checked)

    def on_cbx_unsafe_clicked(self, checked: bool):
        self.filters_clicked(False, checked)

    def on_cbx_unknown_clicked(self, checked: bool):
        self.filters_clicked(None, checked)

    def on_pbn_update_clicked(self):
        self.update_model(self.get_current_browser())

    def on_lv_extensions_double_clicked(self, index: QtCore.QModelIndex):
        model = self.ext_list_models[self.get_current_browser()]
        ext_id = model.data(index, ExtensionIdRole)
        node = model.all_extensions[ext_id]
        da_sp = DaShowProfiles(
            self.get_current_browser(),
            self.ui.cbx_compat.isChecked(),
            model.all_profiles,
            ext_id,
            node.name,
            model.icons[ext_id],
            node.profiles,
            self
        )
        da_sp.exec()

    def update_safe(self, safe_info: dict):
        for browser in self.ext_list_models:
            self.ext_list_models[browser].update_safe_info(safe_info)

    def export_unknown(self) -> dict[str, dict]:
        unknown_ext = {}
        for browser in self.ext_list_models:
            model = self.ext_list_models[browser]
            for row in range(model.rowCount()):
                idx = model.index(row)
                is_safe = model.data(idx, ExtensionStatusRole)
                if is_safe is None:
                    ext_id = model.data(idx, ExtensionIdRole)
                    name = model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole)
                    unknown_ext[ext_id] = {"name": name}
        return unknown_ext
