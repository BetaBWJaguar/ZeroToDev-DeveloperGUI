# -*- coding: utf-8 -*-
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from updater.auth_utils import require_admin_or_developer


CONFIG_FILE = Path(__file__).parent / "local_update_server.json"

with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent
updates_path = CONFIG["paths"]["updates_dir"]
UPDATES_DIR = Path(updates_path)
BASE_URL = CONFIG["endpoints"]["base_url"]


def calculate_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@router.get('/')
def index(current_user = Depends(require_admin_or_developer)) -> Dict:
    return {
        "status": "running",
        "service": "Local Update Server",
        "config": CONFIG,
        "updates_dir": str(UPDATES_DIR),
    }


@router.get('/updates')
def list_updates(current_user = Depends(require_admin_or_developer)) -> Dict[str, List[Dict]]:
    updates = []
    if UPDATES_DIR.exists():
        for file in sorted(UPDATES_DIR.glob("*.zip")):
            updates.append({
                "filename": file.name,
                "sha256": calculate_sha256(file),
                "size": file.stat().st_size,
                "url": f"{BASE_URL}/api/updates/{file.name}"
            })
    return {"updates": updates}


@router.get('/updates/zip_parts')
def get_zip_parts_for_update_info(current_user = Depends(require_admin_or_developer)) -> Dict:
    zip_parts = []
    if UPDATES_DIR.exists():
        for file in sorted(UPDATES_DIR.glob("*.zip")):
            zip_parts.append({
                "url": f"{BASE_URL}/api/updates/{file.name}",
                "sha256": calculate_sha256(file)
            })
    return {"zip_parts": zip_parts}


@router.get('/updates/{filename}')
def serve_update_file(filename: str, current_user = Depends(require_admin_or_developer)):
    file_path = UPDATES_DIR / filename
    if file_path.exists() and file_path.suffix == '.zip':
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")