package com.mall.common;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Date;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class JwtUtil {

    private final RedisTemplate<String, Object> redisTemplate;

    @Value("${jwt.secret:}")
    private String secret;

    private static final long EXPIRE = 7 * 24 * 3600 * 1000L;

    @PostConstruct
    public void init() {
        if (secret == null || secret.isBlank() || secret.length() < 32) {
            throw new IllegalStateException(
                "jwt.secret 必须配置！至少32字符。请在环境变量中设置 JWT_SECRET");
        }
    }

    private SecretKey getKey() {
        return Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    public String generateToken(Long userId, String role) {
        long now = System.currentTimeMillis();
        String tokenVersion = getOrInitTokenVersion(userId);
        return Jwts.builder()
            .id(UUID.randomUUID().toString().replace("-", ""))
            .claim("userId", userId)
            .claim("role", role)
            .claim("tokenVersion", tokenVersion)
            .issuedAt(new Date(now))
            .expiration(new Date(now + EXPIRE))
            .signWith(getKey())
            .compact();
    }

    public Claims parseToken(String token) {
        return Jwts.parser()
            .verifyWith(getKey())
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    public Long getUserId(String token) {
        return parseToken(token).get("userId", Long.class);
    }

    public String getRole(String token) {
        return parseToken(token).get("role", String.class);
    }

    // ==================== Token Blacklist & Revocation ====================

    /** Blacklist a single token (used on logout) */
    public void revokeToken(String token) {
        try {
            Claims claims = parseToken(token);
            Date expiration = claims.getExpiration();
            long ttl = expiration.getTime() - System.currentTimeMillis();
            if (ttl > 0) {
                String jti = claims.getId();
                redisTemplate.opsForValue().set(
                    "mall:token:blacklist:" + jti, "1",
                    Duration.ofMillis(ttl));
            }
        } catch (Exception ignored) {
            // token already invalid — nothing to revoke
        }
    }

    /** Revoke ALL tokens for a user by incrementing their token version */
    public void revokeUserTokens(Long userId) {
        redisTemplate.opsForValue().increment("mall:token:version:" + userId);
    }

    /** Check if a token has been revoked */
    public boolean isTokenRevoked(String token) {
        try {
            Claims claims = parseToken(token);
            // Check individual token blacklist
            String jti = claims.getId();
            if (Boolean.TRUE.equals(redisTemplate.hasKey("mall:token:blacklist:" + jti))) {
                return true;
            }
            // Check user-level token version
            Long userId = claims.get("userId", Long.class);
            String tokenVersion = claims.get("tokenVersion", String.class);
            String currentVersion = getOrInitTokenVersion(userId);
            return !currentVersion.equals(tokenVersion);
        } catch (Exception e) {
            return true; // can't parse = treat as revoked
        }
    }

    private String getOrInitTokenVersion(Long userId) {
        String key = "mall:token:version:" + userId;
        Object val = redisTemplate.opsForValue().get(key);
        if (val == null) {
            String initVer = String.valueOf(System.currentTimeMillis());
            redisTemplate.opsForValue().set(key, initVer);
            return initVer;
        }
        return val.toString();
    }
}
