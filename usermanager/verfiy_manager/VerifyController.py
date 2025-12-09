# -*- coding: utf-8 -*-
import uuid
from datetime import datetime

from fastapi import APIRouter, Query, Form

from usermanager.verfiy_manager.VerifyUtils import VerifyUtils

router = APIRouter()
verify_utils = VerifyUtils()


@router.post("/email")
def verify_email(token: str = Form(...)):
    return verify_utils.verify_email_token(token)


@router.post("/resend")
def resend_verification(email: str = Form(...), app_url: str = Form(...)):
    user_doc = verify_utils.collection.find_one({"email": email})

    if not user_doc:
        return {"success": False, "message": "No user found with this email."}

    if user_doc.get("email_verified"):
        return {"success": False, "message": "Email is already verified."}

    new_token = str(uuid.uuid4())

    verify_utils.collection.update_one(
        {"email": email},
        {"$set": {"email_verification_token": new_token}}
    )

    result = verify_utils.send_verification_email(email, new_token, app_url)

    if result:
        return {"success": True, "message": "Verification email resent successfully."}
    else:
        return {"success": False, "message": "Failed to send verification email."}


@router.get("/reset-confirm")
def confirm_password_reset(token: str = Query(...)):
    now = datetime.utcnow()

    user_doc = verify_utils.collection.find_one({
        "password_reset_token": token,
        "password_reset_expires": {"$gt": now}
    })

    if not user_doc:
        return {"success": False, "message": "Invalid or expired reset token."}

    verify_utils.collection.update_one(
        {"id": user_doc["id"]},
        {"$set": {
            "password": user_doc["password_reset_temp_password"],
            "failed_attempts": 0,
            "lock_until": None
        },
            "$unset": {
                "password_reset_token": "",
                "password_reset_expires": "",
                "password_reset_temp_password": ""
            }}
    )

    return {
        "success": True,
        "message": "New password activated successfully. You can now log in."
    }
