-- 域名轮值系统表
-- V5 新增：独立的域名轮值模块，不依赖AI后台

CREATE TABLE IF NOT EXISTS mall_domain_rotation (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'rotation' COMMENT 'primary/rotation',
    status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT 'active/blocked',
    clicks BIGINT NOT NULL DEFAULT 0,
    blocked_reason VARCHAR(500) NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 预置9个域名（1主 + 8轮值）
INSERT INTO mall_domain_rotation (domain, role, status, clicks) VALUES
('tiktook.eu.cc', 'primary', 'active', 0),
('chxhx.eu.cc', 'rotation', 'active', 0),
('drrgr.eu.cc', 'rotation', 'active', 0),
('drrimrf.eu.cc', 'rotation', 'active', 0),
('drriiu.eu.cc', 'rotation', 'active', 0),
('duomi.eu.cc', 'rotation', 'active', 0),
('dengruihan.eu.cc', 'rotation', 'active', 0),
('yyawzx.eu.cc', 'rotation', 'active', 0),
('gamed.eu.cc', 'rotation', 'active', 0);
