锘?""Google Authenticator TOTP鍙岄噸楠岃瘉 鈥?绾疨ython瀹炵幇(鏃犻渶pyotp)"""
import hmac, hashlib, struct, base64, time, os, io
from typing import Optional

def _int_to_bytestring(i: int, padding: int = 8) -> bytes:
    result = bytearray()
    while i != 0:
        result.append(i & 0xFF)
        i >>= 8
    return bytes(bytearray(reversed(result)).rjust(padding, b"\x00"))

def generate_secret() -> str:
    """鐢熸垚16瀛楄妭闅忔満瀵嗛挜(base32)"""
    return base64.b32encode(os.urandom(16)).decode("utf-8")

def get_totp_token(secret: str, interval: int = 30) -> str:
    """鑾峰彇褰撳墠TOTP浠ょ墝"""
    key = base64.b32decode(secret.upper())
    msg = _int_to_bytestring(int(time.time()) // interval)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 0xF
    code = (struct.unpack(">I", h[o:o+4])[0] & 0x7FFFFFFF) % 1000000
    return str(code).zfill(6)

def verify_totp(secret: str, token: str, window: int = 1) -> bool:
    """楠岃瘉TOTP浠ょ墝锛堝厑璁稿墠鍚巜indow涓懆鏈燂級"""
    for i in range(-window, window + 1):
        expected = get_totp_token(secret, time.time() + i * 30)
        if token == expected:
            return True
    return False

def get_provisioning_uri(secret: str, account: str = "admin@friday-ai") -> str:
    """鐢熸垚Google Authenticator瀵煎叆URI"""
    return f"otpauth://totp/FridayAI:{account}?secret={secret}&issuer=FridayAI&algorithm=SHA1&digits=6&period=30"

def generate_qr_svg(uri: str) -> str:
    """鐢熸垚QR鐮丼VG锛堢敤浜庢壂鐮佺粦瀹氾級"""
    try:
        import qrcode
        qr = qrcode.make(uri)
        buf = io.BytesIO()
        qr.save(buf, format="SVG")
        return buf.getvalue().decode("utf-8")
    except ImportError:
        # 鏃爍rcode搴撴椂杩斿洖URI鏂囨湰
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
<rect width="200" height="200" fill="white"/>
<text x="10" y="30" font-size="12" fill="#333">璇锋墜鍔ㄨ緭鍏ュ瘑閽?</text>
<text x="10" y="55" font-size="14" fill="#667eea" font-weight="bold">{secret}</text>
<text x="10" y="80" font-size="11" fill="#999">鎴栧畨瑁? pip install qrcode[pil]</text>
</svg>"""
