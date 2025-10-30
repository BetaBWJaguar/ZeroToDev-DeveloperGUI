from cryptography.fernet import Fernet
from pathlib import Path
import tempfile, runpy, sys, os

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
KEY_FILE = ROOT / "secret.key"
ENC_FILE = ROOT / "main.enc"

def decrypt_and_run():
    key = KEY_FILE.read_bytes()
    cipher = Fernet(key)
    data = cipher.decrypt(ENC_FILE.read_bytes())
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
    tmp.write(data)
    tmp.flush()
    tmp.close()
    runpy.run_path(tmp.name, run_name='__main__')

if __name__ == '__main__':
    decrypt_and_run()
