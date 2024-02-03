# coding: utf8
import requests
from PySide6 import QtWidgets

SoftwareStatusRole = 0x0101
ExtensionStatusRole = 0x0102
ExtensionIdRole = 0x0103


def accept_warning(widget: QtWidgets.QWidget, condition: bool,
                   caption: str = "Warning", text: str = "Are you sure to continue?") -> bool:
    if condition:
        b = QtWidgets.QMessageBox.question(widget, caption, text)
        if b == QtWidgets.QMessageBox.StandardButton.No:
            return True
    return False


def get_with_chained_keys(dic: dict, keys: list, default=None):
    """
    调用 get_with_chained_keys(d, ["a", "b", "c"])
    等同于 d["a"]["b"]["c"] ，
    只不过中间任意一次索引如果找不到键，则返回 default

    :param dic: 目标字典
    :param keys: 键列表
    :param default: 找不到键时的默认返回值
    :return:
    """
    k = keys[0]
    if k not in dic:
        return default
    if len(keys) == 1:
        return dic[k]
    return get_with_chained_keys(dic[k], keys[1:], default)


def request_content(url: str) -> bytes:
    req = requests.get(url)
    if req.status_code == 200:
        return req.content
    return b""
