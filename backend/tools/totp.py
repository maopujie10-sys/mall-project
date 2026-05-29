"""Google Authenticator TOTP双重验证 — 纯Python实现(无需pyotp)"""
import hmac, hashlib, struct, base64, time, os, io
from typing import Optional

def _int_to_bytestring(i: int, padding: int = 8) -> bytes:
    result = bytearray()
    while i != 0:
        result.append(i & 0xFF)
        i >>= 8
    return bytes(bytearray(reversed(result)).rjust(padding, b"\x00"))

def generate_secret() -> str:
    """生成16字节随机密钥(base32)"""
    return base64.b32encode(os.urandom(16)).decode("utf-8")

def get_totp_token(secret: str, interval: int = 30) -> str:
    """获取当前TOTP令牌"""
    key = base64.b32decode(secret.upper())
    msg = _int_to_bytestring(int(time.time()) // interval)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 0xF
    code = (struct.unpack(">I", h[o:o+4])[0] & 0x7FFFFFFF) % 1000000
    return str(code).zfill(6)

def verify_totp(secret: str, token: str, window: int = 1) -> bool:
    """验证TOTP令牌（允许前后window个周期）"""
    for i in range(-window, window + 1):
        expected = get_totp_token(secret, time.time() + i * 30)
        if token == expected:
            return True
    return False

def get_provisioning_uri(secret: str, account: str = "admin@friday-ai") -> str:
    """生成Google Authenticator导入URI"""
    return f"otpauth://totp/FridayAI:{account}?secret={secret}&issuer=FridayAI&algorithm=SHA1&digits=6&period=30"

def generate_qr_svg(uri: str) -> str:
    """生成QR码SVG（用于扫码绑定）"""
    try:
        import qrcode
        qr = qrcode.make(uri)
        buf = io.BytesIO()
        qr.save(buf, format="SVG")
        return buf.getvalue().decode("utf-8")
    except ImportError:
        # 无qrcode库时返回URI文本
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
<rect width="200" height="200" fill="white"/>
<text x="10" y="30" font-size="12" fill="#333">请手动输入密钥:</text>
<text x="10" y="55" font-size="14" fill="#667eea" font-weight="bold">{secret}</text>
<text x="10" y="80" font-size="11" fill="#999">或安装: pip install qrcode[pil]</text>
</svg>"""
