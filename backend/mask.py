閿?""閺佺増宓侀懘杈ㄦ櫛濡€虫健 閳?閺佸繑鍔呮穱鈩冧紖閼奉亜濮╅柆顔挎杸

閺€顖涘瘮閼磋鲸鏅辩猾璇茬€烽敍?  - 閹靛婧€閸? 138****5678
  - 闁喚顔? abc***@example.com
  - 鐎靛棛鐖?Token/API Key: 閸忋劑鍎撮弴鎸庡床
  - 閺€顖欑帛娣団剝浼? 闁喚娲?  - 閻劍鍩涢崷鏉挎絻: 闁劌鍨庨柆顔炬磰
  - Cookie/Session: 闁喚娲?
閻劍纭?
  from mask import mask_sensitive, mask_dict, mask_text
  clean = mask_sensitive(original_data)
"""
import re
from typing import Any


# ===== 閼磋鲸鏅辩憴鍕灟 =====

def mask_phone(text: str) -> str:
    """閹靛婧€閸? 13812345678 閳?138****5678"""
    return re.sub(r'(1[3-9]\d)\d{4}(\d{4})', r'\1****\2', text)


def mask_email(text: str) -> str:
    """闁喚顔? abc@gmail.com 閳?a***@gmail.com"""
    return re.sub(r'(\w)[\w.]*(@\w+\.\w+)', lambda m: m.group(1) + '***' + m.group(2), text)


def mask_password(text: str) -> str:
    """鐎靛棛鐖?鐎靛棝鎸滈惄绋垮彠: 閸忋劑鍎撮弴鎸庡床娑?***"""
    patterns = [
        (r'(password[\s=:]+)(\S+)', r'\1***'),
        (r'(passwd[\s=:]+)(\S+)', r'\1***'),
        (r'(token[\s=:]+)(\S+)', r'\1***'),
        (r'(api[_-]?key[\s=:]+)(\S+)', r'\1***'),
        (r'(secret[\s=:]+)(\S+)', r'\1***'),
        (r'(access[_-]?key[\s=:]+)(\S+)', r'\1***'),
        (r'(Authorization:\s*)(\S+)', r'\1***'),
    ]
    for pat, repl in patterns:
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    return text


def mask_payment(text: str) -> str:
    """閺€顖欑帛/闁炬儼顢戦崡? 6222021234567890 閳?6222********7890"""
    text = re.sub(r'(\d{4})\d{8,12}(\d{4})', r'\1********\2', text)
    return text


def mask_address(text: str) -> str:
    """閸︽澘娼? 閸栨ぞ鍚敮鍌涙篂闂冨啿灏痻xx鐠?23閸?閳?閸栨ぞ鍚敮鍌涙篂闂冨啿灏?**"""
    return re.sub(r'(閻簠鐢€堥崠绨楅崢绺风悰妤呬壕|闂€?([\u4e00-\u9fa5\d\-]+?閸?)', r'\1***', text)


def mask_id_card(text: str) -> str:
    """闊偂鍞ょ拠? 110101199001011234 閳?110101********1234"""
    return re.sub(r'(\d{6})\d{8,10}(\d{4}[\dXx]?)', r'\1********\2', text)


def mask_cookie(text: str) -> str:
    """Cookie/Session: session=abc123 閳?session=***"""
    patterns = [
        (r'(session[=:]\s*)(\S+)', r'\1***'),
        (r'(cookie[=:]\s*)(\S+)', r'\1***'),
        (r'(JSESSIONID[=:]\s*)(\S+)', r'\1***'),
        (r'(csrf[=:]\s*)(\S+)', r'\1***'),
    ]
    for pat, repl in patterns:
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    return text


def mask_ip(text: str) -> str:
    """IP 閸︽澘娼冮柈銊ュ瀻闁喚娲? 192.168.1.100 閳?192.168.*.*"""
    return re.sub(r'(\d{1,3}\.\d{1,3})\.\d{1,3}\.\d{1,3}', r'\1.*.*', text)


# ===== 缂佺喍绔撮崗銉ュ經 =====

def mask_text(text: str, level: str = "full") -> str:
    """鐎佃鏋冮張顒冪箻鐞涘矁鍔氶弫蹇擃槱閻?    
    level:
      "full" - 閸忋劑鍎撮懘杈ㄦ櫛
      "basic" - 娴犲懎鐦戦惍?Token/鐎靛棝鎸?      "user" - 閹靛婧€/闁喚顔?闊偂鍞ょ拠?閸︽澘娼?    """
    if not text or not isinstance(text, str):
        return text

    if level in ("full", "basic"):
        text = mask_password(text)
        text = mask_cookie(text)

    if level in ("full", "user"):
        text = mask_phone(text)
        text = mask_email(text)
        text = mask_id_card(text)
        text = mask_address(text)
        text = mask_payment(text)
        text = mask_ip(text)

    return text


def mask_dict(data: dict, level: str = "full") -> dict:
    """鐎电懓鐡ч崗闀愯厬閹碘偓閺堝鐡х粭锔胯閸婅壈绻樼悰宀冨姎閺?""
    if not data:
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            # 閻楄鐣╂径鍕倞瀹歌尙鐓￠弫蹇斿妳鐎涙顔?            if any(kw in key.lower() for kw in ("password", "passwd", "token", "secret", "key", "auth")):
                result[key] = "***"
            else:
                result[key] = mask_text(value, level)
        elif isinstance(value, dict):
            result[key] = mask_dict(value, level)
        elif isinstance(value, list):
            result[key] = [mask_dict(item, level) if isinstance(item, dict) else mask_text(str(item), level) if isinstance(item, str) else item for item in value]
        else:
            result[key] = value
    return result


def mask_sensitive(data: Any, level: str = "full") -> Any:
    """闁氨鏁ら懘杈ㄦ櫛閸忋儱褰涢敍宀冨殰閸斻劌鍨介弬顓犺閸?""
    if isinstance(data, str):
        return mask_text(data, level)
    elif isinstance(data, dict):
        return mask_dict(data, level)
    elif isinstance(data, list):
        return [mask_sensitive(item, level) for item in data]
    return data


# ===== 鐎瑰鍙忕€涙顔岄崚妤勩€冮敍鍫滅返閸忔湹绮Ο鈥虫健瀵洜鏁ら敍?====

SENSITIVE_FIELDS = {
    "users": ["password", "pay_password", "balance", "phone", "email", "real_name", "id_card"],
    "orders": ["consignee", "phone", "address", "payment_info"],
    "admins": ["password", "token"],
    "withdraw": ["bank_card", "bank_name", "real_name", "phone"],
    "recharge": ["payment_info"],
}

# ===== 閼磋鲸鏅辨稉顓㈡？娴?=====

class SensitiveMaskMiddleware:
    """FastAPI 娑擃參妫挎禒璁圭窗閼奉亜濮╃€电懓鎼锋惔鏂捐厬閻ㄥ嫭鏅遍幇鐔风摟濞堜絻鍔氶弫?""
    
    @staticmethod
    async def mask_response(data: Any) -> Any:
        return mask_sensitive(data, level="full")


# 韫囶偊鈧喕鐨熼悽銊ュ焼閸?mask = mask_text  # from mask import mask; mask("閹靛婧€13812345678") 閳?"閹靛婧€138****5678"
