# -*- coding: utf-8 -*-
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from PathHelper import PathHelper
from usermanager.UserManager import UserManager
from data_manager.MemoryManager import MemoryManager
from language_manager.LangManager import LangManager

security = HTTPBasic()

langs_dir = PathHelper.resource_path("langs")
ui_lang = MemoryManager.get("ui_language", "english")
lang_manager = LangManager(langs_dir=langs_dir, default_lang=ui_lang)
user_manager = UserManager(lang=lang_manager)


def get_current_user(credentials: HTTPBasicCredentials = Security(security)):
    user = user_manager.login_user(credentials.username, credentials.password)
    
    if isinstance(user, str):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user


def require_admin_or_developer(current_user = Depends(get_current_user)):

    role = None

    if isinstance(current_user.id, dict) and "role" in current_user.id:
        role = current_user.id["role"]

    if str(role).upper() not in {"ADMIN", "DEVELOPER"}:
        raise HTTPException(
            status_code=403,
            detail="Access denied. ADMIN or DEVELOPER role required."
        )

    return current_user