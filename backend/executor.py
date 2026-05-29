閿?""鐎瑰鍙忛幍褑顢戦崳?閳?SSH/subprocess + 閸涙垝鎶ら惂钘夋倳閸?姒涙垵鎮曢崡?""
import subprocess
import os
import shlex
from typing import Optional

# ===== 閸涙垝鎶ら惂钘夋倳閸?=====
COMMAND_WHITELIST = [
    "uptime", "free", "df", "docker", "nginx", "curl",
    "ss", "systemctl", "tail", "cat", "ls", "ps", "top",
    "journalctl", "who", "last", "ping", "dig", "openssl", "pgrep", "host", "acme.sh",
    "du", "grep", "wc", "sort", "head", "echo", "date",
]

# ===== 閸楅亶娅撻崨鎴掓姢姒涙垵鎮曢崡?=====
DANGEROUS_PATTERNS = [
    "rm -rf", "mkfs", "dd if=", "reboot", "shutdown",
    "DROP DATABASE", "DROP TABLE", "TRUNCATE", "DELETE FROM",
    "chmod -R 777", "chown -R", "passwd", "userdel",
    "iptables -F", "ufw disable",
    "docker system prune", "docker volume rm",
    "> /dev/", "| bash", "| sh", "curl.*| bash",
    "wget.*| bash", "eval", "exec ",
]

# ===== 閸涙垝鎶ら崣鍌涙殶娓氬顦?=====
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
    """鐎瑰鍙忔潻婵婎潐瀵倸鐖?""
    pass


def _check_command(cmd_str: str):
    """濡偓閺屻儱鎳℃禒銈嗘Ц閸氾箑鐣ㄩ崗?""
    parts = shlex.split(cmd_str)
    if not parts:
        raise SecurityError("缁屽搫鎳℃禒?)

    base = parts[0]

    # 閻ц棄鎮曢崡鏇燁梾閺?    if base not in COMMAND_WHITELIST:
        raise SecurityError(f"閸涙垝鎶ゆ稉宥呮躬閻ц棄鎮曢崡鏇氳厬: {base}")

    # 姒涙垵鎮曢崡鏇燁梾閺?    full_cmd = cmd_str.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in full_cmd:
            raise SecurityError(f"閸涙垝鎶ら崠鍛儓閸楅亶娅撻幙宥勭稊: {pattern}")

    # 娓氬顦荤憴鍕灟濡偓閺?    if base in ALLOWED_OVERRIDES:
        allowed_args = ALLOWED_OVERRIDES[base]
        if allowed_args:
            rest = parts[1:]
            ok = not rest  # 閺冪姴寮弫鐗堟閸忎浇顔?            for arg in rest:
                if any(arg.startswith(a) for a in allowed_args):
                    ok = True
                    break
            if not ok:
                raise SecurityError(f"閸涙垝鎶?{base} 閸欏倹鏆熸稉宥呮躬閸忎浇顔忛懠鍐ㄦ纯閸愬懌鈧倸鍘戠拋? {', '.join(allowed_args)}")
    return parts


async def execute(cmd_str: str, timeout: int = 30) -> dict:
    """
    鐎瑰鍙忛幍褑顢戦張顒€婀撮崨鎴掓姢閵?    鏉╂柨娲? {"success": bool, "stdout": str, "stderr": str, "exit_code": int}
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
        return {"success": False, "stdout": "", "stderr": f"閹笛嗩攽鐡掑懏妞?({timeout}s)", "exit_code": -1}
    except FileNotFoundError:
        return {"success": False, "stdout": "", "stderr": f"閸涙垝鎶ら張顏呭閸? {parts[0]}", "exit_code": -1}
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
    闁俺绻?SSH 鏉╂粎鈻奸幍褑顢戦崨鎴掓姢閵?    閺€顖涘瘮鐎靛棛鐖滅拋銈堢槈閸滃苯鐦戦柦銉吇鐠囦椒琚辩粔宥嗘煙瀵繈鈧?    """
    from config import SSH_HOST, SSH_PORT, SSH_USER, SSH_KEY_PATH

    host = host or SSH_HOST
    user = ssh_user or SSH_USER
    key_path = ssh_key_path or SSH_KEY_PATH
    port = SSH_PORT

    if not host:
        return {"success": False, "stdout": "", "stderr": "SSH 娑撶粯婧€閸︽澘娼冮張顏堝帳缂?(SSH_HOST)", "exit_code": -1}

    try:
        # 鐏忔繆鐦担璺ㄦ暏 SSH 閸涙垝鎶ら惄瀛樺复鏉╃偞甯?        ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"
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
        return {"success": False, "stdout": "", "stderr": f"SSH 閹笛嗩攽鐡掑懏妞?({timeout}s)", "exit_code": -1}
    except FileNotFoundError:
        return {"success": False, "stdout": "", "stderr": "SSH 鐎广垺鍩涚粩顖涙弓鐎瑰顥?, "exit_code": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": f"SSH 閹笛嗩攽婢惰精瑙? {str(e)}", "exit_code": -1}


async def execute_db(sql: str, db_name: str = "mall") -> dict:
    """
    闁俺绻?MySQL 鐎广垺鍩涚粩顖涘⒔鐞涘本鏆熼幑顔肩氨閺屻儴顕楅妴?    鏉╂柨娲? {"success": bool, "rows": list, "error": str}
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
        return {"success": False, "stdout": "", "stderr": "閺佺増宓佹惔鎾寸叀鐠囥垼绉撮弮?, "exit_code": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}


