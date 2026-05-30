''" -- 

:
  - : 138****5678
  - : abc***@example.com
  - /Token/API Key: 
  - : 
  - : 
  - Cookie/Session: 

:
  from mask import mask_sensitive, mask_dict, mask_text
  clean = mask_sensitive(original_data)
''"
import re
from typing import Any


# =====  =====

def mask_phone(text: str) -> str:
    ''": 13812345678 -> 138****5678''"
    return re.sub(r'(1[3-9]\d)\d{4}(\d{4})', r'\1****\2', text)


def mask_email(text: str) -> str:
    ''": abc@gmail.com -> a***@gmail.com''"
    return re.sub(r'(\w)[\w.]*(@\w+\.\w+)', lambda m: m.group(1) + '***' + m.group(2), text)


def mask_password(text: str) -> str:
    ''"/:  ***''"
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
    ''"/: 6222021234567890 -> 6222********7890''"
    text = re.sub(r'(\d{4})\d{8,12}(\d{4})', r'\1********\2', text)
    return text


def mask_address(text: str) -> str:
    ''": xxx123 -> ***''"
    return re.sub(r'(|||||)([\u4e00-\u9fa5\d\-]+??)', r'\1***', text)


def mask_id_card(text: str) -> str:
    ''": 110101199001011234 -> 110101********1234''"
    return re.sub(r'(\d{6})\d{8,10}(\d{4}[\dXx]?)', r'\1********\2', text)


def mask_cookie(text: str) -> str:
    ''"Cookie/Session: session=abc123 -> session=***''"
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
    ''"IP : 192.168.1.100 -> 192.168.*.*''"
    return re.sub(r'(\d{1,3}\.\d{1,3})\.\d{1,3}\.\d{1,3}', r'\1.*.*', text)


# =====  =====

def mask_text(text: str, level: str = "full") -> str:
    ''"
    
    level:
      "full" - 
      "basic" - /Token/
      "user" - /
    ''"
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
    ''''''
    if not data:
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            
            if any(kw in key.lower() for kw in ("password", "passwd", "token", "secret", "key", "auth")):
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
    ''",''"
    if isinstance(data, str):
        return mask_text(data, level)
    elif isinstance(data, dict):
        return mask_dict(data, level)
    elif isinstance(data, list):
        return [mask_sensitive(item, level) for item in data]
    return data


# ===== ()=====

SENSITIVE_FIELDS = {
    "users": ["password", "pay_password", "balance", "phone", "email", "real_name", "id_card"],
    "orders": ["consignee", "phone", "address", "payment_info"],
    "admins": ["password", "token"],
    "withdraw": ["bank_card", "bank_name", "real_name", "phone"],
    "recharge": ["payment_info"],
}

# =====  =====

class SensitiveMaskMiddleware:
    ''"FastAPI :''"
    
    @staticmethod
    async def mask_response(data: Any) -> Any:
        return mask_sensitive(data, level="full")



mask = mask_text  # from mask import mask; mask("13812345678") -> "138****5678"
