# -*- coding: utf-8 -*-
import requests
from updater.UpdaterGUI import UpdaterGUI
from updater.Updater_Utils import download_update_zip_parts, extract_update_zip, get_current_version

UPDATE_INFO_URL = "http://localhost:3000/MyProjects/ZeroToDev-DeveloperGUI/raw/branch/master/updater/update_info.json"


def check_for_update_gui(parent, lang, logger):
    try:
        response = requests.get(UPDATE_INFO_URL, timeout=5)
        data = response.json()

        remote_version = data["version"]
        zip_parts = data["zip_parts"]
        changelog = data.get("changelog", "")

        local_version = get_current_version()

        if remote_version != local_version:

            def confirmed():
                zip_path = download_update_zip_parts(zip_parts)
                extract_update_zip(zip_path)
                run_updater()

            UpdaterGUI(
                parent=parent,
                lang=lang,
                logger=logger,
                local_version=local_version,
                remote_version=remote_version,
                changelog=changelog,
                on_confirm=confirmed
            )

    except Exception as e:
        print("[Updater] GUI Update check failed:", e)


def run_updater():
    import subprocess
    from PathHelper import PathHelper

    base_dir = PathHelper.base_dir()
    updater_exe = base_dir / "Updater.exe"

    if not updater_exe.exists():
        print("[Updater] ERROR: Updater.exe not found:", updater_exe)
        return

    subprocess.Popen(
        [str(updater_exe)],
        cwd=str(base_dir),
        close_fds=True,
        creationflags=subprocess.DETACHED_PROCESS
    )
