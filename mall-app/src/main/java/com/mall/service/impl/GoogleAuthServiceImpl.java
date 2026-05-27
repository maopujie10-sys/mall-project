package com.mall.service.impl;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.client.j2se.MatrixToImageWriter;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;
import com.mall.service.GoogleAuthService;
import org.springframework.stereotype.Service;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.ByteArrayOutputStream;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.Map;

@Service
public class GoogleAuthServiceImpl implements GoogleAuthService {

    private static final String ISSUER = "TikTokMall";
    private static final int SECRET_BYTES = 20;
    private static final int DIGITS = 6;
    private static final int PERIOD = 30;
    private static final String HMAC_ALGO = "HmacSHA1";

    @Override
    public Map<String, String> generateSecret(String email) {
        byte[] secretBytes = new byte[SECRET_BYTES];
        new SecureRandom().nextBytes(secretBytes);
        String secret = base32Encode(secretBytes);

        String otpauthUrl = String.format(
            "otpauth://totp/%s:%s?secret=%s&issuer=%s&digits=%d&period=%d",
            ISSUER, email != null ? email : "user", secret, ISSUER, DIGITS, PERIOD);

        String qrBase64 = generateQrBase64(otpauthUrl);
        return Map.of("secret", secret, "qrUrl", qrBase64);
    }

    @Override
    public boolean verifyCode(String secret, int code) {
        long counter = System.currentTimeMillis() / 1000 / PERIOD;
        // Check current and adjacent windows
        return generateTotp(secret, counter) == code
            || generateTotp(secret, counter - 1) == code
            || generateTotp(secret, counter + 1) == code;
    }

    @Override
    public int getCurrentCode(String secret) {
        long counter = System.currentTimeMillis() / 1000 / PERIOD;
        return generateTotp(secret, counter);
    }

    private int generateTotp(String secret, long counter) {
        byte[] key = base32Decode(secret);
        byte[] data = new byte[8];
        for (int i = 7; i >= 0; i--) {
            data[i] = (byte) (counter & 0xFF);
            counter >>= 8;
        }
        try {
            Mac mac = Mac.getInstance(HMAC_ALGO);
            mac.init(new SecretKeySpec(key, HMAC_ALGO));
            byte[] hash = mac.doFinal(data);
            int offset = hash[hash.length - 1] & 0x0F;
            int binary = ((hash[offset] & 0x7F) << 24)
                        | ((hash[offset + 1] & 0xFF) << 16)
                        | ((hash[offset + 2] & 0xFF) << 8)
                        | (hash[offset + 3] & 0xFF);
            return binary % (int) Math.pow(10, DIGITS);
        } catch (Exception e) {
            throw new RuntimeException("TOTP generation failed", e);
        }
    }

    private String generateQrBase64(String content) {
        try {
            QRCodeWriter writer = new QRCodeWriter();
            BitMatrix matrix = writer.encode(content, BarcodeFormat.QR_CODE, 200, 200);
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            MatrixToImageWriter.writeToStream(matrix, "PNG", bos);
            return "data:image/png;base64," + Base64.getEncoder().encodeToString(bos.toByteArray());
        } catch (Exception e) {
            throw new RuntimeException("QR code generation failed", e);
        }
    }

    // Base32 encoding (RFC 4648 alphabet, no padding)
    private static final String BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

    private String base32Encode(byte[] data) {
        StringBuilder sb = new StringBuilder();
        int buffer = 0;
        int bitsLeft = 0;
        for (byte b : data) {
            buffer = (buffer << 8) | (b & 0xFF);
            bitsLeft += 8;
            while (bitsLeft >= 5) {
                sb.append(BASE32_ALPHABET.charAt((buffer >> (bitsLeft - 5)) & 0x1F));
                bitsLeft -= 5;
            }
        }
        if (bitsLeft > 0) {
            sb.append(BASE32_ALPHABET.charAt((buffer << (5 - bitsLeft)) & 0x1F));
        }
        return sb.toString();
    }

    private byte[] base32Decode(String input) {
        String s = input.toUpperCase().replaceAll("[^A-Z2-7]", "");
        int outLen = s.length() * 5 / 8;
        byte[] out = new byte[outLen];
        int buffer = 0;
        int bitsLeft = 0;
        int idx = 0;
        for (char c : s.toCharArray()) {
            int val = BASE32_ALPHABET.indexOf(c);
            if (val < 0) continue;
            buffer = (buffer << 5) | val;
            bitsLeft += 5;
            if (bitsLeft >= 8) {
                out[idx++] = (byte) ((buffer >> (bitsLeft - 8)) & 0xFF);
                bitsLeft -= 8;
            }
        }
        return out;
    }
}
