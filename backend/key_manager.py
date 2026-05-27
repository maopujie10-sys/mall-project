"""密钥管理 - 密钥轮换/审计/安全存储"""
import os, secrets, re, json, shutil
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
KEYS_FILE = ROOT / "key_registry.json"
class KeyManager:
    @staticmethod
    def generate_key(length=32):
        return secrets.token_hex(length)
    @staticmethod
    def list_keys():
        keys=[]
        env_file=ROOT/".env"
        if env_file.exists():
            with open(env_file,encoding="utf-8") as f:
                for line in f:
                    line=line.strip()
                    if "=" in line and not line.startswith("#"):
                        keys.append({"name":line.split("=")[0].strip(),"status":"active"})
        return keys
    @staticmethod
    def rotate_key(key_name):
        new_key=KeyManager.generate_key()
        env_file=ROOT/".env"
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file=ROOT/f".env.backup.{ts}"
        if not env_file.exists(): return {"ok":False,"error":".env not found"}
        shutil.copy(env_file,backup_file)
        with open(env_file,encoding="utf-8") as f: content=f.read()
        pattern=key_name+r"\s*=\s*.*"
        new_line=f"{key_name}={new_key}"
        new_content,count=re.subn(pattern,new_line,content,flags=re.MULTILINE)
        if count==0: return {"ok":False,"error":f"key {key_name} not found"}
        with open(env_file,"w",encoding="utf-8") as f: f.write(new_content)
        KeyManager._audit(key_name,"rotate",backup_file.name)
        return {"ok":True,"key":key_name,"backup":str(backup_file)}
    @staticmethod
    def _audit(key_name,action,detail=""):
        entry={"time":datetime.now().isoformat(),"key":key_name,"action":action,"detail":detail}
        logs=[]
        if KEYS_FILE.exists():
            try:
                with open(KEYS_FILE,encoding="utf-8") as f: logs=json.load(f)
            except: pass
        logs.append(entry)
        logs=logs[-100:]
        with open(KEYS_FILE,"w",encoding="utf-8") as f: json.dump(logs,f,ensure_ascii=False,indent=2)
    @staticmethod
    def audit_history(limit=20):
        if not KEYS_FILE.exists(): return []
        with open(KEYS_FILE,encoding="utf-8") as f: return json.load(f)[-limit:]
    @staticmethod
    def check_env_security():
        issues=[]
        env_file=ROOT/".env"
        gitignore=ROOT/".gitignore"
        if not env_file.exists(): issues.append("no .env")
        if gitignore.exists():
            with open(gitignore,encoding="utf-8") as f:
                if ".env" not in f.read(): issues.append(".env not in gitignore")
        else: issues.append("no gitignore")
        return {"ok":len(issues)==0,"issues":issues}