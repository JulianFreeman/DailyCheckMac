# coding: utf8
import os
import json
import shutil
from pathlib import Path
# from typing import Callable
from PySide6 import QtCore, QtWidgets
from dataclasses import dataclass, field
from global_vars import get_with_chained_keys


@dataclass
class ProfileNode(object):
    gaia_given_name: str
    gaia_name: str
    name: str
    shortcut_name: str
    user_name: str


ProfilesData = dict[str, ProfileNode]


def scan_profiles(user_data_path: str) -> ProfilesData:
    local_state_path = Path(user_data_path, "Local State")
    if not local_state_path.exists():
        return {}

    local_state_data: dict = json.loads(local_state_path.read_text(encoding="utf8"))
    info_cache_data: dict = get_with_chained_keys(local_state_data, ["profile", "info_cache"])

    profiles_data: ProfilesData = {}

    for profile_id in info_cache_data:
        profile_data: dict = info_cache_data[profile_id]
        profile_node = ProfileNode(
            gaia_given_name=profile_data.get("gaia_given_name", ""),
            gaia_name=profile_data.get("gaia_name", ""),
            name=profile_data.get("name", ""),
            shortcut_name=profile_data.get("shortcut_name", ""),
            user_name=profile_data.get("user_name"),
        )
        profiles_data[profile_id] = profile_node

    return profiles_data


@dataclass
class ExtensionNode(object):
    # ids: str
    icon: str
    name: str
    # path: str
    profiles: list[str] = field(default_factory=list)


ExtensionsData = dict[str, ExtensionNode]


def get_extension_icon_path(ext_icons: dict[str, str], ext_path: str, profile_path: Path) -> str:
    if len(ext_icons) == 0:
        return ""

    if "128" in ext_icons:
        icon_file = ext_icons["128"]
    else:
        icon_file = ext_icons[str(max(map(lambda x: int(x), ext_icons.keys())))]
    # 如果路径以 / 开头，会被认为是根而忽略其他，因此需要检查一下
    if icon_file.startswith("/"):
        icon_file = icon_file[1:]

    full_path = Path(profile_path, "Extensions", ext_path, icon_file)
    if not full_path.exists():
        return ""
    return str(full_path)


def scan_extensions(browser: str, is_compat=False) -> tuple[ExtensionsData, ProfilesData]:
    us = QtCore.QSettings()
    user_data_path = str(us.value(f"{browser}Data", ""))
    if len(user_data_path) == 0 or not Path(user_data_path).exists():
        return {}, {}

    profile_data = scan_profiles(user_data_path)
    extensions_data: ExtensionsData = {}

    if is_compat:
        pref_file = "Preferences"
    else:
        pref_file = "Secure Preferences"

    # print(pref_file)

    for profile_id in profile_data:
        profile_path = Path(user_data_path, profile_id)
        secure_pref_path = Path(profile_path, pref_file)
        secure_pref_data: dict = json.loads(secure_pref_path.read_text(encoding="utf8"))
        ext_settings_data: dict = get_with_chained_keys(secure_pref_data, ["extensions", "settings"], dict())

        for ext_id in ext_settings_data:
            ext_data: dict = ext_settings_data[ext_id]
            # 这里插件有几种情况
            ext_path: str = ext_data.get("path", "")
            if len(ext_path) == 0:
                # 如果 path 是空，则该插件可能是一些内部插件，不予收集
                continue
            elif not (ext_path.startswith(ext_id) or os.path.exists(ext_path)):
                # 如果 path 以插件 ID 开头，则为商店安装的插件，
                # 如果不是以插件 ID 开头，但是是一个存在的路径，则为离线安装的插件
                # 否则，可能也是内部插件，不予收集
                continue
            ext_manifest: dict = ext_data.get("manifest", {})
            if len(ext_manifest) == 0:
                # 如果 manifest 为空，则该插件可能是离线插件，需要额外找它的 manifest
                ext_manifest_path = Path(ext_path, "manifest.json")
                ext_manifest: dict = json.loads(ext_manifest_path.read_text(encoding="utf8"))

            if ext_id not in extensions_data:
                ext_node = ExtensionNode(
                    # ids=ext_id,
                    icon=get_extension_icon_path(ext_manifest.get("icons", {}), ext_path, profile_path),
                    name=ext_manifest.get("name", ""),
                    # path=ext_data.get("path", ""),
                    profiles=[profile_id],
                )
                extensions_data[ext_id] = ext_node
            else:
                ext_node = extensions_data[ext_id]
                ext_node.profiles += [profile_id]

    return extensions_data, profile_data


# ================== Deletion ====================


def delete_extensions(profile_path: str, pref_name: str, ext_ids: list[str]) -> tuple[int, int]:
    total = len(ext_ids)

    e_pref_path = Path(profile_path, pref_name)
    e_pref_data = json.loads(e_pref_path.read_text("utf8"))  # type: dict
    ext_set_data = get_with_chained_keys(e_pref_data, ["extensions", "settings"])  # type: dict
    if ext_set_data is None:
        return 0, total

    s_pref_path = Path(profile_path, "Secure Preferences")
    pref_path = Path(profile_path, "Preferences")
    s_pref_data = json.loads(s_pref_path.read_text("utf8"))  # type: dict
    pref_data = json.loads(pref_path.read_text("utf8"))  # type: dict

    macs = get_with_chained_keys(s_pref_data, ["protection", "macs", "extensions", "settings"])  # type: dict
    if macs is None:
        return 0, total

    success = 0
    for ids in ext_ids:
        c1 = ext_set_data.pop(ids, None)
        c2 = macs.pop(ids, None)
        if None not in (c1, c2):
            success += 1

    pinned_ext = get_with_chained_keys(pref_data, ["extensions", "pinned_extensions"])  # type: list
    if pinned_ext is not None:
        for ids in ext_ids:
            if ids in pinned_ext:
                pinned_ext.remove(ids)

    s_pref_path.write_text(json.dumps(s_pref_data, ensure_ascii=False), "utf8")
    pref_path.write_text(json.dumps(pref_data, ensure_ascii=False), "utf8")

    extensions_path_d = Path(profile_path, "Extensions")
    for ids in ext_ids:
        # 对于离线安装的插件，目录可能不在这个位置，所以就不删了
        ext_folder_path = Path(extensions_path_d, ids)
        if ext_folder_path.exists():
            shutil.rmtree(ext_folder_path, ignore_errors=True)

    return success, total


class DeleteThread(QtCore.QThread):

    deleted = QtCore.Signal(int, int)

    def __init__(self,
                 profile_path: str,
                 pref_name: str,
                 ext_ids: list[str],
                 parent: QtCore.QObject = None):
        super().__init__(parent)
        self.profile_path = profile_path
        self.pref_name = pref_name
        self.ext_ids = ext_ids
        self.finished.connect(self.deleteLater)

    def run(self):
        success, total = delete_extensions(self.profile_path, self.pref_name, self.ext_ids)
        self.deleted.emit(success, total)


class DeleteThreadManager(QtCore.QObject):

    def __init__(self, total: int, progress_bar: QtWidgets.QProgressBar, parent: QtWidgets.QDialog):
        super().__init__(parent)
        self.deletion_progress = 0
        self.success_deletion = 0
        self.fail_deletion = 0
        self.total_for_deletion = total
        self.deletion_info = "成功：{success} 个；失败：{fail} 个；总共 {total} 个。"
        self.progress_bar = progress_bar
        self.parent = parent

        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)

        self.progress_bar.valueChanged.connect(self.on_pgb_del_value_changed)

    def start(self, thread: DeleteThread):
        thread.deleted.connect(self.on_del_thd_deleted)
        thread.start()

    def on_del_thd_deleted(self, success: int, total: int):
        self.success_deletion += success
        self.deletion_progress += total
        self.fail_deletion += total - success
        self.progress_bar.setValue(self.deletion_progress)

    def on_pgb_del_value_changed(self, value: int):
        if value == self.total_for_deletion:
            QtWidgets.QMessageBox.information(
                self.parent, "删除结果", self.deletion_info.format(
                    success=self.success_deletion,
                    fail=self.fail_deletion,
                    total=self.total_for_deletion
                )
            )
            self.parent.accept()
