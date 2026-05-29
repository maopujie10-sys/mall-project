"""安全执行器 — SSH/subprocess + 命令白名单/黑名单"""
import subprocess
import os
import shlex
from typing import Optional

# ===== 命令白名单 =====
COMMAND_WHITELIST = [
    "uptime", "free", "df", "docker", "nginx", "curl",
    "ss", "systemctl", "tail", "cat", "ls", "ps", "top",
    "journalctl", "who", "last", "ping", "dig", "openssl", "pgrep", "host", "acme.sh",
    "du", "grep", "wc", "sort", "head", "echo", "date",
]

# ===== 危险命令黑名单 =====
DANGEROUS_PATTERNS = [
    "rm -rf", "mkfs", "dd if=", "reboot", "shutdown",
    "DROP DATABASE", "DROP TABLE", "TRUNCATE", "DELETE FROM",
    "chmod -R 777", "chown -R", "passwd", "userdel",
    "iptables -F", "ufw disable",
    "docker system prune", "docker volume rm",
    "> /dev/", "| bash", "| sh", "curl.*| bash",
    "wget.*| bash", "eval", "exec ",
]

# ===== 命令参数例外 =====
ALLOWED_OVERRIDES = {
    "df": ["-h"],
    "ps": ["aux", "ef"],
    "docker": ["ps", "logs", "compose", "inspect", "stats", "images", "info", "version", "system", "network", "volume", "restart", "stop", "start"],
    "systemctl": ["status", "is-active"],
    "journalctl": ["-xe", "-u", "--no-pager", "-n"],
    "tail": ["-n", "-f"],
    "cat": [],
}


class SecurityError(Exception):
    """安全违规异常"""
    pass


def _check_command(cmd_str: str):
    """检查命令是否安全"""
    parts = shlex.split(cmd_str)
    if not parts:
        raise SecurityError("空命令")

    base = parts[0]

    # 白名单检查
    if base not in COMMAND_WHITELIST:
        raise SecurityError(f"命令不在白名单中: {base}")

    # 黑名单检查
    full_cmd = cmd_str.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in full_cmd:
            raise SecurityError(f"命令包含危险操作: {pattern}")

    # 例外规则检查
    if base in ALLOWED_OVERRIDES:
        allowed_args = ALLOWED_OVERRIDES[base]
        if allowed_args:
            rest = parts[1:]
            ok = not rest  # 无参数时允许
            for arg in rest:
                if any(arg.startswith(a) for a in allowed_args):
                    ok = True
                    break
            if not ok:
                raise SecurityError(f"命令 {base} 参数不在允许范围内。允许: {', '.join(allowed_args)}")
    return parts


async def execute(cmd_str: str, timeout: int = 30) -> dict:
    """
    安全执行本地命令。
    返回: {"success": bool, "stdout": str, "stderr": str, "exit_code": int}
    """
    try:
        parts = _check_command(cmd_str)
    except SecurityError as e:
        return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}

    try:
        result = subprocess.run(
            parts,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[-50000:],
            "stderr": result.stderr[-10000:],
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": f"执行超时 ({timeout}s)", "exit_code": -1}
    except FileNotFoundError:
        return {"success": False, "stdout": "", "stderr": f"命令未找到: {parts[0]}", "exit_code": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}


async def execute_ssh(
    host: str,
    cmd_str: str,
    ssh_user: str = "agent_user",
    ssh_key_path: str = "",
    timeout: int = 30,
) -> dict:
    """
    通过 SSH 远程执行命令。
    支持密码认证和密钥认证两种方式。
    """
    from config import SSH_HOST, SSH_PORT, SSH_USER, SSH_KEY_PATH

    host = host or SSH_HOST
    user = ssh_user or SSH_USER
    key_path = ssh_key_path or SSH_KEY_PATH
    port = SSH_PORT

    if not host:
        return {"success": False, "stdout": "", "stderr": "SSH 主机地址未配置 (SSH_HOST)", "exit_code": -1}

    try:
        # 尝试使用 SSH 命令直接连接
        ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"
        if key_path:
            ssh_cmd += f" -i {key_path}"
        ssh_cmd += f" -p {port} {user}@{host}"
        full_cmd = f"{ssh_cmd} {shlex.quote(cmd_str)}"

        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[-50000:],
            "stderr": result.stderr[-10000:],
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": f"SSH 执行超时 ({timeout}s)", "exit_code": -1}
    except FileNotFoundError:
        return {"success": False, "stdout": "", "stderr": "SSH 客户端未安装", "exit_code": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": f"SSH 执行失败: {str(e)}", "exit_code": -1}


async def execute_db(sql: str, db_name: str = "mall") -> dict:
    """
    通过 MySQL 客户端执行数据库查询。
    返回: {"success": bool, "rows": list, "error": str}
    """
    from config import MALL_DB_HOST, MALL_DB_PORT, MALL_DB_USER, MALL_DB_PASSWORD, MALL_DB_NAME

    sql_upper = sql.strip().upper()
    if sql_upper.startswith("SELECT") or sql_upper.startswith("SHOW") or sql_upper.startswith("DESCRIBE"):
        cmd = f'MYSQL_PWD={MALL_DB_PASSWORD} mysql -h {MALL_DB_HOST} -P {MALL_DB_PORT} -u {MALL_DB_USER} {db_name} -e "{sql}" --table 2>&1'
    else:
        cmd = f'MYSQL_PWD={MALL_DB_PASSWORD} mysql -h {MALL_DB_HOST} -P {MALL_DB_PORT} -u {MALL_DB_USER} {db_name} -e "{sql}" 2>&1'

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[-50000:],
            "stderr": result.stderr[-10000:],
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "数据库查询超时", "exit_code": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}


