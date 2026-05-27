-- V5.0 新Entity建表DDL — 2026-05-22
-- 数据库: malldb | 引擎: InnoDB | 字符集: utf8mb4

CREATE TABLE IF NOT EXISTS mall_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(20),
    password VARCHAR(255),
    nickname VARCHAR(100),
    avatar VARCHAR(500),
    email VARCHAR(100),
    status INT DEFAULT 0,
    level_id INT DEFAULT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE IF NOT EXISTS mall_user_balance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    balance DECIMAL(20,2) DEFAULT 0.00,
    frozen DECIMAL(20,2) DEFAULT 0.00,
    version INT DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户余额表';

CREATE TABLE IF NOT EXISTS mall_balance_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(20,2),
    type VARCHAR(30),
    remark VARCHAR(500),
    related_id BIGINT DEFAULT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='余额变动日志';

CREATE TABLE IF NOT EXISTS mall_recharge_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(64) NOT NULL,
    user_id BIGINT NOT NULL,
    amount DECIMAL(20,2) NOT NULL,
    usdt_address VARCHAR(255) DEFAULT NULL,
    tx_hash VARCHAR(255) DEFAULT NULL,
    screenshot VARCHAR(500) DEFAULT NULL,
    status INT DEFAULT 0,
    reject_reason VARCHAR(500) DEFAULT NULL,
    audit_admin_id BIGINT DEFAULT NULL,
    audit_time DATETIME DEFAULT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='USDT充值单';

CREATE TABLE IF NOT EXISTS mall_withdraw_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(64) NOT NULL,
    user_id BIGINT NOT NULL,
    amount DECIMAL(20,2) NOT NULL,
    usdt_address VARCHAR(255) DEFAULT NULL,
    status INT DEFAULT 0,
    tx_hash VARCHAR(255) DEFAULT NULL,
    reject_reason VARCHAR(500) DEFAULT NULL,
    audit_admin_id BIGINT DEFAULT NULL,
    audit_time DATETIME DEFAULT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='USDT提现单';

CREATE TABLE IF NOT EXISTS mall_merchant (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    shop_name VARCHAR(200),
    shop_phone VARCHAR(30),
    shop_address VARCHAR(500),
    shop_remark VARCHAR(500),
    avatar VARCHAR(500) DEFAULT NULL,
    banner1 VARCHAR(500) DEFAULT NULL,
    banner2 VARCHAR(500) DEFAULT NULL,
    banner3 VARCHAR(500) DEFAULT NULL,
    status INT DEFAULT 0,
    contact VARCHAR(100),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商户表';

CREATE TABLE IF NOT EXISTS mall_merchant_apply (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    shop_name VARCHAR(200),
    shop_phone VARCHAR(30),
    shop_address VARCHAR(500),
    contact VARCHAR(100),
    remark VARCHAR(500) DEFAULT NULL,
    status INT DEFAULT 0,
    reject_reason VARCHAR(500) DEFAULT NULL,
    audit_admin_id BIGINT DEFAULT NULL,
    audit_time DATETIME DEFAULT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商户入驻申请表';

CREATE TABLE IF NOT EXISTS mall_admin (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar VARCHAR(500) DEFAULT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    status INT DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    UNIQUE KEY uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员表';

CREATE TABLE IF NOT EXISTS mall_cart (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id BIGINT,
    sku_id BIGINT,
    quantity INT DEFAULT 1,
    price DECIMAL(20,2),
    status INT DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='购物车';

CREATE TABLE IF NOT EXISTS T_MALL_PRODUCT (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    category_id BIGINT,
    brand_id BIGINT,
    name VARCHAR(200),
    subtitle VARCHAR(200) DEFAULT NULL,
    main_image VARCHAR(500) DEFAULT NULL,
    detail_images TEXT DEFAULT NULL,
    price DECIMAL(20,2),
    original_price DECIMAL(20,2) DEFAULT NULL,
    cost_price DECIMAL(20,2) DEFAULT NULL,
    total_stock INT DEFAULT 0,
    sales INT DEFAULT 0,
    virtual_sales INT DEFAULT 0,
    virtual_views INT DEFAULT 0,
    status INT DEFAULT 0,
    is_hot INT DEFAULT 0,
    is_new INT DEFAULT 0,
    sort INT DEFAULT 0,
    description TEXT,
    unit VARCHAR(20) DEFAULT NULL,
    is_wholesale INT DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    INDEX idx_category (category_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';
