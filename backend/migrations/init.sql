-- TikTokMall AI Agent 数据库初始化脚本
-- 数据库：ai_agent

CREATE DATABASE IF NOT EXISTS ai_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_agent;

-- 任务主表
CREATE TABLE IF NOT EXISTS agent_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(64) NOT NULL UNIQUE,
    user_message TEXT,
    intent VARCHAR(128),
    mode VARCHAR(32) DEFAULT 'ai_control',
    risk_level VARCHAR(4) DEFAULT 'L1',
    status VARCHAR(32) DEFAULT 'pending',
    need_confirm TINYINT(1) DEFAULT 0,
    confidence DECIMAL(4,2),
    result_summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 任务步骤表
CREATE TABLE IF NOT EXISTS agent_task_steps (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(64) NOT NULL,
    step_order INT DEFAULT 0,
    step_name VARCHAR(128),
    tool_name VARCHAR(64),
    status VARCHAR(32) DEFAULT 'pending',
    input_data TEXT,
    output_data TEXT,
    evidence TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 命令日志表
CREATE TABLE IF NOT EXISTS agent_command_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(64),
    command_text TEXT NOT NULL,
    risk_level VARCHAR(4) DEFAULT 'L1',
    executed TINYINT(1) DEFAULT 0,
    exit_code INT DEFAULT -1,
    stdout TEXT,
    stderr TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 审批记录表
CREATE TABLE IF NOT EXISTS agent_confirmations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(64) NOT NULL,
    action_name VARCHAR(128),
    risk_level VARCHAR(4),
    risk_description TEXT,
    diff_preview TEXT,
    backup_path VARCHAR(512),
    rollback_plan TEXT,
    confirmed_by VARCHAR(64),
    confirmed_at DATETIME,
    status VARCHAR(16) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 备份记录表
CREATE TABLE IF NOT EXISTS agent_backups (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    backup_id VARCHAR(64) NOT NULL UNIQUE,
    task_id VARCHAR(64),
    backup_type VARCHAR(32) DEFAULT 'manual',
    target_name VARCHAR(128),
    backup_path VARCHAR(512),
    verified TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_backup_id (backup_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 人机接管记录表
CREATE TABLE IF NOT EXISTS agent_handover_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    mode VARCHAR(32) NOT NULL,
    reason TEXT,
    triggered_by VARCHAR(64) DEFAULT 'system',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 商城结构地图表
CREATE TABLE IF NOT EXISTS mall_structure_maps (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    map_id VARCHAR(64) NOT NULL UNIQUE,
    project_path VARCHAR(512),
    frontend_structure JSON,
    backend_structure JSON,
    database_structure JSON,
    interface_routes JSON,
    permission_map JSON,
    risk_fields JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_map_id (map_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 客服 AI 日志表
CREATE TABLE IF NOT EXISTS customer_ai_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(64),
    user_id VARCHAR(64),
    question TEXT,
    ai_reply TEXT,
    question_type VARCHAR(64),
    risk_level VARCHAR(4) DEFAULT 'L1',
    escalated TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 告警记录表
CREATE TABLE IF NOT EXISTS agent_alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    alert_id VARCHAR(64) NOT NULL UNIQUE,
    level VARCHAR(4) DEFAULT 'P3',
    title VARCHAR(256),
    detail TEXT,
    source VARCHAR(64) DEFAULT 'system',
    resolved TINYINT(1) DEFAULT 0,
    resolved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alert_id (alert_id),
    INDEX idx_level (level),
    INDEX idx_resolved (resolved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
