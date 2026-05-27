"""数据脱敏模块 — 敏感信息自动遮蔽

支持脱敏类型：
  - 手机号: 138****5678
  - 邮箱: abc***@example.com
  - 密码/Token/API Key: 全部替换
  - 支付信息: 遮盖
  - 用户地址: 部分遮盖
  - Cookie/Session: 遮盖

用法:
  from mask import mask_sensitive, mask_dict, mask_text
  clean = mask_sensitive(original_data)
"""
import re
from typing import Any


# ===== 脱敏规则 =====

def mask_phone(text: str) -> str:
    """手机号: 13812345678 → 138****5678"""
    return re.sub(r'(1[3-9]\d)\d{4}(\d{4})', r'\1****\2', text)


def mask_email(text: str) -> str:
    """邮箱: abc@gmail.com → a***@gmail.com"""
    return re.sub(r'(\w)[\w.]*(@\w+\.\w+)', lambda m: m.group(1) + '***' + m.group(2), text)


def mask_password(text: str) -> str:
    """密码/密钥相关: 全部替换为 ***"""
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
    """支付/银行卡: 6222021234567890 → 6222********7890"""
    text = re.sub(r'(\d{4})\d{8,12}(\d{4})', r'\1********\2', text)
    return text


def mask_address(text: str) -> str:
    """地址: 北京市朝阳区xxx路123号 → 北京市朝阳区***"""
    return re.sub(r'(省|市|区|县|街道|镇)([\u4e00-\u9fa5\d\-]+?号?)', r'\1***', text)


def mask_id_card(text: str) -> str:
    """身份证: 110101199001011234 → 110101********1234"""
    return re.sub(r'(\d{6})\d{8,10}(\d{4}[\dXx]?)', r'\1********\2', text)


def mask_cookie(text: str) -> str:
    """Cookie/Session: session=abc123 → session=***"""
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
    """IP 地址部分遮盖: 192.168.1.100 → 192.168.*.*"""
    return re.sub(r'(\d{1,3}\.\d{1,3})\.\d{1,3}\.\d{1,3}', r'\1.*.*', text)


# ===== 统一入口 =====

def mask_text(text: str, level: str = "full") -> str:
    """对文本进行脱敏处理
    
    level:
      "full" - 全部脱敏
      "basic" - 仅密码/Token/密钥
      "user" - 手机/邮箱/身份证/地址
    """
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
    """对字典中所有字符串值进行脱敏"""
    if not data:
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            # 特殊处理已知敏感字段
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
    """通用脱敏入口，自动判断类型"""
    if isinstance(data, str):
        return mask_text(data, level)
    elif isinstance(data, dict):
        return mask_dict(data, level)
    elif isinstance(data, list):
        return [mask_sensitive(item, level) for item in data]
    return data


# ===== 安全字段列表（供其他模块引用）=====

SENSITIVE_FIELDS = {
    "users": ["password", "pay_password", "balance", "phone", "email", "real_name", "id_card"],
    "orders": ["consignee", "phone", "address", "payment_info"],
    "admins": ["password", "token"],
    "withdraw": ["bank_card", "bank_name", "real_name", "phone"],
    "recharge": ["payment_info"],
}

# ===== 脱敏中间件 =====

class SensitiveMaskMiddleware:
    """FastAPI 中间件：自动对响应中的敏感字段脱敏"""
    
    @staticmethod
    async def mask_response(data: Any) -> Any:
        return mask_sensitive(data, level="full")


# 快速调用别名
mask = mask_text  # from mask import mask; mask("手机13812345678") → "手机138****5678"
