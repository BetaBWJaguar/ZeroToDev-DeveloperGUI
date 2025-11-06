# -*- coding: utf-8 -*-
from fastapi import APIRouter, Query

from usermanager.verfiy_manager.VerifyUtils import VerifyUtils

router = APIRouter()
verify_utils = VerifyUtils()


@router.get("/verify/email")
def verify_email(token: str = Query(...)):
    return verify_utils.verify_email_token(token)
