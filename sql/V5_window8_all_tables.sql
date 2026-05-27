-- ============================================================
-- 窗口8 | 数据库+配置 — 全模块建表 + 修复
-- 日期: 2026-05-23
-- ============================================================

USE malldb;

-- ============================================================
-- Part 1: 新建7张缺失表
-- ============================================================

-- 1. T_MALL_USERADDRESS (收货地址 — Address模块)
DROP TABLE IF EXISTS T_MALL_USERADDRESS;
CREATE TABLE T_MALL_USERADDRESS (
    UUID          VARCHAR(32)  NOT NULL PRIMARY KEY,
    PARTY_ID      VARCHAR(32)  NOT NULL,
    RECEIVER_NAME VARCHAR(50),
    RECEIVER_PHONE VARCHAR(20),
    COUNTRY_ID     VARCHAR(32),
    STATE_ID       VARCHAR(32),
    CITY_ID        VARCHAR(32),
    ADDRESS_DETAIL VARCHAR(500),
    ZIP_CODE       VARCHAR(20),
    IS_DEFAULT     INT          DEFAULT 0,
    CREATE_TIME    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    UPDATE_TIME    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    STATUS         INT          DEFAULT 1,
    INDEX idx_party_id (PARTY_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. mall_third_party_recharge (第三方支付 — ThirdPartyRecharge模块)
DROP TABLE IF EXISTS mall_third_party_recharge;
CREATE TABLE mall_third_party_recharge (
    id             BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    trade_no       VARCHAR(64)  NOT NULL,
    user_id        BIGINT       NOT NULL,
    amount         DECIMAL(20,2) NOT NULL,
    channel        VARCHAR(32)  NOT NULL COMMENT 'PAYPAL/STRIPE/BINANCE',
    status         INT          DEFAULT 0 COMMENT '0=待支付 1=已支付 2=失败',
    callback_data  TEXT         COMMENT '第三方回调原始数据',
    create_time    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX uk_trade_no (trade_no),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. mall_upload_img (图片上传记录 — UploadImg模块)
DROP TABLE IF EXISTS mall_upload_img;
CREATE TABLE mall_upload_img (
    id             BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id        BIGINT       NOT NULL,
    file_name      VARCHAR(255),
    file_url       VARCHAR(500) NOT NULL,
    file_size      BIGINT,
    file_type      VARCHAR(50)  COMMENT 'image/jpeg, image/png等',
    upload_type    VARCHAR(32)  COMMENT 'AVATAR/PRODUCT/KYC/BANNER',
    related_id     VARCHAR(64)  COMMENT '关联业务ID',
    create_time    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_related (related_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. mall_idcode (短信/邮箱验证码 — Idcode模块)
DROP TABLE IF EXISTS mall_idcode;
CREATE TABLE mall_idcode (
    id             BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    target         VARCHAR(100) NOT NULL COMMENT '手机号或邮箱',
    code           VARCHAR(10)  NOT NULL COMMENT '验证码',
    type           VARCHAR(32)  NOT NULL COMMENT 'REGISTER/LOGIN/RESET_PWD/BIND',
    expire_at      DATETIME     NOT NULL COMMENT '过期时间',
    used           INT          DEFAULT 0 COMMENT '0=未使用 1=已使用',
    ip             VARCHAR(50)  COMMENT '发送IP',
    create_time    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_target_type (target, type),
    INDEX idx_expire (expire_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. mall_sys_param (系统参数配置 — Syspara模块)
DROP TABLE IF EXISTS mall_sys_param;
CREATE TABLE mall_sys_param (
    id             BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    param_key      VARCHAR(100) NOT NULL COMMENT '参数键',
    param_value    TEXT         COMMENT '参数值',
    param_type     VARCHAR(32)  DEFAULT 'STRING' COMMENT 'STRING/INT/DOUBLE/JSON',
    description    VARCHAR(500) COMMENT '参数说明',
    editable       INT          DEFAULT 1 COMMENT '0=不可编辑 1=可编辑',
    create_time    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX uk_param_key (param_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. mall_kyc (实名认证 — KYC模块)
DROP TABLE IF EXISTS mall_kyc;
CREATE TABLE mall_kyc (
    id                BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id           BIGINT       NOT NULL UNIQUE,
    real_name         VARCHAR(100) COMMENT '真实姓名',
    id_card_no        VARCHAR(50)  COMMENT '证件号码',
    id_card_type      VARCHAR(32)  DEFAULT 'ID_CARD' COMMENT 'ID_CARD/PASSPORT/DRIVER_LICENSE',
    front_img         VARCHAR(500) COMMENT '证件正面',
    back_img          VARCHAR(500) COMMENT '证件反面',
    hand_img          VARCHAR(500) COMMENT '手持证件',
    status            INT          DEFAULT 0 COMMENT '0=待审核 1=通过 2=拒绝',
    reject_reason     VARCHAR(500),
    audit_admin_id    BIGINT,
    audit_time        DATETIME,
    submit_time       DATETIME     DEFAULT CURRENT_TIMESTAMP,
    create_time       DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time       DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_id_card (id_card_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. mall_chat_message (在线客服消息 — OnlineChat模块)
DROP TABLE IF EXISTS mall_chat_message;
CREATE TABLE mall_chat_message (
    id               BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    conversation_id  VARCHAR(64)  NOT NULL COMMENT '会话ID',
    from_user_id     BIGINT       NOT NULL,
    to_user_id       BIGINT       NOT NULL COMMENT '接收方ID，0=客服',
    content          TEXT         NOT NULL,
    msg_type         VARCHAR(32)  DEFAULT 'TEXT' COMMENT 'TEXT/IMAGE/FILE',
    is_read          INT          DEFAULT 0,
    create_time      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conversation (conversation_id),
    INDEX idx_from_user (from_user_id),
    INDEX idx_to_user (to_user_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. mall_subscribe (消息订阅 — Subscribe模块)
DROP TABLE IF EXISTS mall_subscribe;
CREATE TABLE mall_subscribe (
    id             BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id        BIGINT       NOT NULL,
    type           VARCHAR(32)  NOT NULL COMMENT 'ORDER/SYSTEM/PROMOTION/CHAT',
    target         VARCHAR(100) COMMENT '订阅目标',
    channel        VARCHAR(32)  DEFAULT 'APP' COMMENT 'APP/EMAIL/WHATSAPP/TELEGRAM',
    enabled        INT          DEFAULT 1 COMMENT '0=关闭 1=启用',
    create_time    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- Part 2: 修复已有表
-- ============================================================

-- 2a. T_MALL_CATEGORY 补 name 字段
ALTER TABLE T_MALL_CATEGORY ADD COLUMN NAME VARCHAR(100) AFTER UUID;

-- 2b. mall_recharge_order txHash 加唯一索引（防止重复充值）
-- 先检查是否存在 tx_hash 列，存在才加索引
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA='malldb' AND TABLE_NAME='mall_recharge_order' AND COLUMN_NAME='tx_hash');
SET @sqlstmt := IF(@exist > 0,
    'ALTER TABLE mall_recharge_order ADD UNIQUE INDEX uk_tx_hash (tx_hash)',
    'SELECT "tx_hash column not found, skip index" AS msg');
PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2c. mall_withdraw_order 补 usdt_network 字段
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA='malldb' AND TABLE_NAME='mall_withdraw_order' AND COLUMN_NAME='usdt_network');
SET @sqlstmt := IF(@exist = 0,
    'ALTER TABLE mall_withdraw_order ADD COLUMN usdt_network VARCHAR(10) COMMENT "TRC20/ERC20" AFTER usdt_address',
    'SELECT "usdt_network already exists" AS msg');
PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2d. T_MALL_ORDER 补收货地址快照字段
ALTER TABLE T_MALL_ORDER
    ADD COLUMN RECEIVER_NAME VARCHAR(50) AFTER LOGISTICS_COMPANY,
    ADD COLUMN RECEIVER_PHONE VARCHAR(20) AFTER RECEIVER_NAME,
    ADD COLUMN RECEIVER_ADDRESS VARCHAR(500) AFTER RECEIVER_PHONE;

-- ============================================================
-- Part 3: 插入默认系统参数
-- ============================================================

INSERT IGNORE INTO mall_sys_param (param_key, param_value, param_type, description) VALUES
('WITHDRAW_MAX_AMOUNT', '10000', 'DOUBLE', '提现单笔上限(USDT)'),
('RECHARGE_MIN_AMOUNT', '10', 'DOUBLE', '充值最低金额(USDT)'),
('SITE_NAME', 'TikTokMall', 'STRING', '商城名称'),
('SITE_NOTICE', 'Welcome to TikTokMall', 'STRING', '站点公告'),
('ORDER_TIMEOUT_MINUTES', '30', 'INT', '订单超时取消时间(分钟)');

-- ============================================================
-- 验证
-- ============================================================
SELECT '=== 建表完成，当前所有表 ===' AS status;
SHOW TABLES;
