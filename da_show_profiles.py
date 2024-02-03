# coding: utf8
import os
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
from util_ext import ProfilesData, DeleteThread, DeleteThreadManager
from global_vars import accept_warning


def sort_profiles_id_func(profile_id: str) -> int:
    if profile_id == "Default":
        return 0
    else:
        seq = profile_id.split(" ", 1)[-1]
        try:
            return int(seq)
        except ValueError:
            # if the id is weird
            return 999


class ProfilesModel(QtCore.QAbstractTableModel):

    def __init__(self,
                 profiles_data: ProfilesData,
                 ext_id: str,
                 profiles: list[str],
                 parent=None):
        super().__init__(parent)
        self.ext_id = ext_id
        self.profiles = profiles
        self.profiles.sort(key=sort_profiles_id_func)
        self.profiles_data = profiles_data

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.profiles)

    def columnCount(self, parent: QtCore.QModelIndex = ...):
        return 2

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        row = index.row()
        col = index.column()

        if col == 0:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return self.profiles[row]
        elif col == 1:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return self.profiles_data[self.profiles[row]].name

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return "ID"
            if section == 1:
                return "名称"


class DaShowProfiles(QtWidgets.QDialog):

    def __init__(self,
                 browser: str,
                 is_compat: bool,
                 profiles_data: ProfilesData,
                 ext_id: str,
                 ext_name: str,
                 ext_icon: QtGui.QIcon,
                 profiles: list[str],
                 parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setWindowTitle(ext_name)
        self.setWindowIcon(ext_icon)
        self.browser = browser
        self.is_compat = is_compat

        self.process = QtCore.QProcess(self)

        # ========== UI ==============

        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)

        self.lne_info = QtWidgets.QLineEdit(ext_id, self)
        self.lne_info.setReadOnly(True)
        self.vly_m.addWidget(self.lne_info)

        self.trv_profiles = QtWidgets.QTreeView(self)
        self.trv_profiles.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.vly_m.addWidget(self.trv_profiles)

        self.pgb_del = QtWidgets.QProgressBar(self)
        self.pgb_del.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.vly_m.addWidget(self.pgb_del)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.pbn_delete_selected = QtWidgets.QPushButton("删除所选", self)
        self.pbn_open = QtWidgets.QPushButton("打开", self)
        self.pbn_cancel = QtWidgets.QPushButton("取消", self)
        self.hly_bot.addWidget(self.pbn_delete_selected)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_open)
        self.hly_bot.addWidget(self.pbn_cancel)
        self.vly_m.addLayout(self.hly_bot)

        self.profiles_model = ProfilesModel(profiles_data, ext_id, profiles, self)
        self.trv_profiles.setModel(self.profiles_model)

        self.pbn_delete_selected.clicked.connect(self.on_pbn_delete_selected_clicked)
        self.pbn_open.clicked.connect(self.on_pbn_open_clicked)
        self.pbn_cancel.clicked.connect(self.reject)

    def sizeHint(self):
        return QtCore.QSize(400, 360)

    def on_pbn_open_clicked(self):
        us = QtCore.QSettings()
        exec_path = str(us.value(f"{self.browser}Exec", ""))
        if len(exec_path) == 0 or not os.path.exists(exec_path):
            QtWidgets.QMessageBox.critical(self, "错误", f"无法找到 {self.browser} 浏览器的执行路径")
            return

        indexes = self.trv_profiles.selectedIndexes()
        cmd = rf'"{exec_path}" --profile-directory="{{0}}"'
        for idx in indexes:
            if idx.column() != 0:
                continue
            profile_id = self.profiles_model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole)
            # setProgram 不行，不知道为什么，莫名其妙
            self.process.startCommand(cmd.format(profile_id))
            self.process.waitForFinished(10000)

    def on_pbn_delete_selected_clicked(self):
        us = QtCore.QSettings()
        user_data_path = str(us.value(f"{self.browser}Data", ""))
        if self.is_compat:
            pref_name = "Preferences"
        else:
            pref_name = "Secure Preferences"

        indexes = self.trv_profiles.selectedIndexes()
        total = len(indexes) // 2
        if accept_warning(self, True, "警告", f"确定要删除这 {total} 项吗？"):
            return

        del_thd_mgr = DeleteThreadManager(total, self.pgb_del, self)

        for idx in indexes:
            if idx.column() != 0:
                continue
            profile_id = self.profiles_model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole)
            del_thd = DeleteThread(
                str(Path(user_data_path, profile_id)),
                pref_name,
                [self.lne_info.text()],
                self
            )
            del_thd_mgr.start(del_thd)
