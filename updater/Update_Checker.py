# -*- coding: utf-8 -*-
import requests
from updater.UpdaterGUI import UpdaterGUI
from updater.Updater_Utils import download_update_zip, extract_update_zip, get_current_version

UPDATE_INFO_URL = "https://raw.githubusercontent.com/BetaBWJaguar/ZeroToDev-DeveloperGUI/master/updater/update_info.json"


def check_for_update_gui(parent, lang, logger):
    try:
        response = requests.get(UPDATE_INFO_URL, timeout=5)
        data = response.json()

        remote_version = data["version"]
        zip_url = data["zip_url"]
        changelog = data.get("changelog", "")

        local_version = get_current_version()

        if remote_version != local_version:

            def confirmed():
                zip_path = download_update_zip(zip_url)
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
    from updater.Updater import main
    main()
