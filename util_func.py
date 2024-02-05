# coding: utf8
import os
import json
from pathlib import Path
import xml.etree.ElementTree as Et

from global_vars import request_content


def get_isp_name() -> str:
    try:
        data = json.loads(request_content("https://ipinfo.io/"))
        return data.get("org", "[Not found]")
    except json.JSONDecodeError:
        return "[Decode Error]"


def get_app_icon_path(info_file: Path) -> str:
    try:
        tree = Et.parse(info_file)
    except Et.ParseError:
        return ""
    root = tree.getroot()
    dic = root[0]
    keys = []
    values = []
    for c in dic:
        if c.tag == "key":
            keys.append(c.text)
        else:
            values.append(c.text)

    res = {k: v for k, v in zip(keys, values)}
    if "CFBundleIconFile" not in res:
        return ""
    name = res["CFBundleIconFile"]
    path = str(info_file.parent / "Resources" / name)
    if not path.endswith(".icns"):
        path = path + ".icns"
    return path


def get_mac_installed_software() -> dict[str, str]:
    p1 = Path("/Applications")
    p2 = Path("/System/Applications")
    p3 = Path(os.path.expanduser("~"), "Applications")

    all_soft: list[Path] = []

    def search(path: Path):
        for c in path.glob("*"):
            if str(c).endswith(".app"):
                if c.is_dir() and (c / "Contents" / "Info.plist").exists():
                    all_soft.append(c)
            elif c.is_dir():
                search(c)

    search(p1)
    search(p2)
    search(p3)
    all_soft.sort(key=lambda x: x.name.lower())

    return {
        app.name: get_app_icon_path(app / "Contents" / "Info.plist")
        for app in all_soft
    }
