# -*- coding: utf-8 -*-
from pathlib import Path
import qrcode
import uuid
from usermanager.verfiy_manager.twofa_manager.TwoFAUtils import TwoFAUtils


class TwoFA:

    @staticmethod
    def generate_qr(secret: str, email: str, issuer_name: str = "ZTDGUI") -> Path:
        totp = TwoFAUtils.get_totp(secret)
        otp_uri = totp.provisioning_uri(name=email, issuer_name=issuer_name)

        filename = f"2fa_qr_{uuid.uuid4().hex}.png"
        qr_path = Path(filename)

        qrcode.make(otp_uri).save(qr_path)
        return qr_path

    @staticmethod
    def verify(secret: str, code: str) -> bool:
        if not TwoFAUtils.verify_code_format(code):
            return False

        totp = TwoFAUtils.get_totp(secret)
        return totp.verify(code)
