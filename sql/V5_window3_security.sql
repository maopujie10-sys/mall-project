-- V5 窗口3：谷歌验证器+资金密码 数据库迁移
-- 2026-05-23
ALTER TABLE mall_user
    ADD COLUMN google_auth_secret VARCHAR(255) DEFAULT NULL COMMENT '谷歌验证器密钥',
    ADD COLUMN safeword VARCHAR(255) DEFAULT NULL COMMENT '资金密码BCrypt';
