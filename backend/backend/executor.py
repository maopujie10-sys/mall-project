''" -- SSH/subprocess + /''"
import subprocess
import os
import shlex
from typing import Optional

# =====  =====
COMMAND_WHITELIST = [
    "uptime", "free", "df", "docker", "nginx", "curl",
    "ss", "systemctl", "tail", "cat", "ls", "ps", "top",
    "journalctl", "who", "last", "ping", "dig", "openssl", "pgrep", "host", "acme.sh",
    "du", "grep", "wc", "sort", "head", "echo", "date",
]

# =====  =====
DANGEROUS_PATTERNS = [
    "rm -rf", "mkfs", "dd if=", "reboot", "shutdown",
    "DROP DATABASE", "DROP TABLE", "TRUNCATE", "DELETE FROM",
    "chmod -R 777", "chown -R", "passwd", "userdel",
    "iptables -F", "ufw disable",
    "docker system prune", "docker volume rm",
    "> /dev/", "| bash", "| sh", "curl.*| bash",
    "wget.*| bash", "eval", "exec ",
]

# =====  =====
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
    ''''''
    pass


def _check_command(cmd_str: str):
    ''''''
    parts = shlex.split(cmd_str)
    if not parts:
        raise SecurityError('')

    base = parts[0]

    
    if base not in COMMAND_WHITELIST:
        raise SecurityError(f": {base}")

    
    full_cmd = cmd_str.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in full_cmd:
            raise SecurityError(f": {pattern}")

    
    if base in ALLOWED_OVERRIDES:
        allowed_args = ALLOWED_OVERRIDES[base]
        if allowed_args:
            rest = parts[1:]
            ok = not rest  
            for arg in rest:
                if any(arg.startswith(a) for a in allowed_args):
                    ok = True
                    break
            if not ok:
                raise SecurityError(f" {base} .: {', '.join(allowed_args)}")
    return parts


async def execute(cmd_str: str, timeout: int = 30) -> dict:
    ''"
    .
    : {"success": bool, "stdout": str, "stderr": str, "exit_code": int}
    ''"
    try:
        parts = _check_command(cmd_str)
    except SecurityError as e:
        return {"success": False, "stdout": '', "stderr": str(e), "exit_code": -1}

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
        return {"success": False, "stdout": '', "stderr": f" ({timeout}s)", "exit_code": -1}
    except FileNotFoundError:
        return {"success": False, "stdout": '', "stderr": f": {parts[0]}", "exit_code": -1}
    except Exception as e:
        return {"success": False, "stdout": '', "stderr": str(e), "exit_code": -1}


async def execute_ssh(
    host: str,
    cmd_str: str,
    ssh_user: str = "agent_user",
    ssh_key_path: str = '',
    timeout: int = 30,
) -> dict:
    ''"
     SSH .
    .
    ''"
    from config import SSH_HOST, SSH_PORT, SSH_USER, SSH_KEY_PATH

    host = host or SSH_HOST
    user = ssh_user or SSH_USER
    key_path = ssh_key_path or SSH_KEY_PATH
    port = SSH_PORT

    if not host:
        return {"success": False, "stdout": '', "stderr": "SSH  (SSH_HOST)", "exit_code": -1}

    try:
        #  SSH 
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
        return {"success": False, "stdout": '', "stderr": f"SSH  ({timeout}s)", "exit_code": -1}
    except FileNotFoundError:
        return {"success": False, "stdout": '', "stderr": "SSH ", "exit_code": -1}
    except Exception as e:
        return {"success": False, "stdout": '', "stderr": f"SSH : {str(e)}", "exit_code": -1}


async def execute_db(sql: str, db_name: str = "mall") -> dict:
    ''"
     MySQL .
    : {"success": bool, "rows": list, "error": str}
    ''"
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
        return {"success": False, "stdout": '', "stderr": '', "exit_code": -1}
    except Exception as e:
        return {"success": False, "stdout": '', "stderr": str(e), "exit_code": -1}


