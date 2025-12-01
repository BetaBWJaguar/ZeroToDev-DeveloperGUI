# -*- coding: utf-8 -*-
import json
import requests
from updater.Updater_Utils import download_update_zip, extract_update_zip, get_current_version
import subprocess
import sys
import os
from pathlib import Path

UPDATE_INFO_URL = ""


def check_for_update():
    try:
        print("[Updater] Checking for updates...")

        response = requests.get(UPDATE_INFO_URL, timeout=5)
        data = response.json()

        remote_version = data["version"]
        zip_url = data["zip_url"]

        local_version = get_current_version()

        if remote_version != local_version:
            print(f"[Updater] New version found → {remote_version}")
            zip_path = download_update_zip(zip_url)
            extract_update_zip(zip_path)

            run_updater()
        else:
            print("[Updater] Application is up-to-date.")
    except Exception as e:
        print("[Updater] Update check failed:", e)


def run_updater():
    updater_script = Path(__file__).parent / "Updater.py"
    subprocess.Popen([sys.executable, str(updater_script)])
    sys.exit(0)
