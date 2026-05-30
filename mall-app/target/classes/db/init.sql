-- TikTokMall 跨境商城 数据库初始化
-- 数据库: mall_db (由 docker-compose MYSQL_DATABASE 自动创建)
-- 表结构由 Spring Boot JPA/Hibernate 自动生成 (ddl-auto=update)

-- 确保字符集
ALTER DATABASE mall_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 初始管理员账号 (密码需要 BCrypt 加密后插入)
-- INSERT INTO mall_admin (username, password, role, status) VALUES ('admin', 'BCRYPT_HASH', 'SUPER_ADMIN', 1);
