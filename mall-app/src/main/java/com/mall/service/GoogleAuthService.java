package com.mall.service;

import java.util.Map;

public interface GoogleAuthService {
    /** 生成TOTP密钥+QR码base64，返回{secret, qrUrl} */
    Map<String, String> generateSecret(String email);
    /** 验证TOTP码 */
    boolean verifyCode(String secret, int code);
    /** 获取密钥的当前TOTP码（用于调试） */
    int getCurrentCode(String secret);
}
