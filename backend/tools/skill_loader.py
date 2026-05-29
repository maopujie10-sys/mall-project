"""鎶€鑳藉寘鍔犺浇寮曟搸 鈥?鐪熸鐨勬妧鑳藉垎鍙戠郴缁?鏀寔 ZIP 鍖呭畨瑁呫€佺増鏈鐞嗐€佷緷璧栬В鏋愩€佺儹鍔犺浇"""
import os
import json
import zipfile
import hashlib
import shutil
import importlib.util
from datetime import datetime
from typing import Optional

SKILLS_DIR = os.getenv("SKILLS_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills"))


def _skill_path(skill_id: str) -> str:
    """鎶€鑳藉畨瑁呰矾寰?""
    return os.path.join(SKILLS_DIR, skill_id)


def get_manifest(skill_id: str) -> Optional[dict]:
    """璇诲彇宸插畨瑁呮妧鑳界殑 manifest.json"""
    mp = os.path.join(_skill_path(skill_id), "skill.json")
    if os.path.exists(mp):
        with open(mp, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def list_installed() -> list[dict]:
    """鍒楀嚭鎵€鏈夊凡瀹夎鐨勬妧鑳?""
    if not os.path.exists(SKILLS_DIR):
        return []
    skills = []
    for name in os.listdir(SKILLS_DIR):
        mp = os.path.join(SKILLS_DIR, name, "skill.json")
        if os.path.exists(mp):
            with open(mp, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                skills.append(manifest)
    return skills


async def install_from_zip(zip_path: str, source: str = "upload") -> dict:
    """浠?ZIP 鍖呭畨瑁呮妧鑳?""
    if not os.path.exists(zip_path):
        return {"ok": False, "error": "ZIP 鏂囦欢涓嶅瓨鍦?}

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # 璇诲彇 manifest
            if "skill.json" not in zf.namelist():
                return {"ok": False, "error": "ZIP 鍖呯己灏?skill.json"}
            manifest = json.loads(zf.read("skill.json"))
            skill_id = manifest.get("id", "")
            if not skill_id:
                return {"ok": False, "error": "skill.json 缂哄皯 id 瀛楁"}

            # 鐗堟湰鏍￠獙
            existing = get_manifest(skill_id)
            if existing:
                from packaging.version import parse as vp
                if existing.get("version", "0") >= manifest.get("version", "0"):
                    return {"ok": False, "error": f"宸插畨瑁呯増鏈?{existing['version']}锛屾棤闇€闄嶇骇"}

            # 瀹夊叏鏍￠獙锛氭鏌ユ槸鍚︽湁鍗遍櫓鏂囦欢
            dangerous = [n for n in zf.namelist() if n.startswith("..") or "/.." in n or n.startswith("/")]
            if dangerous:
                return {"ok": False, "error": f"ZIP 鍖呭寘鍚嵄闄╄矾寰? {dangerous}"}

            # 瑙ｅ帇鍒扮洰鏍囩洰褰?            target = _skill_path(skill_id)
            if os.path.exists(target):
                shutil.rmtree(target)
            os.makedirs(target, exist_ok=True)
            zf.extractall(target)

            # 鍐欏叆瀹夎璁板綍
            manifest["installed_at"] = datetime.now().isoformat()
            manifest["install_source"] = source
            manifest["install_path"] = target
            with open(os.path.join(target, "skill.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)

            # 灏濊瘯楠岃瘉涓诲叆鍙ｆ枃浠?            entry = manifest.get("entry", "main.py")
            entry_path = os.path.join(target, entry)
            if not os.path.exists(entry_path):
                return {"ok": True, "warning": f"鍏ュ彛鏂囦欢 {entry} 涓嶅瓨鍦紝闇€鎵嬪姩鍒涘缓", "skill_id": skill_id, "manifest": manifest}

            return {"ok": True, "skill_id": skill_id, "manifest": manifest, "path": target}

    except zipfile.BadZipFile:
        return {"ok": False, "error": "ZIP 鏂囦欢鎹熷潖"}
    except json.JSONDecodeError:
        return {"ok": False, "error": "skill.json 鏍煎紡閿欒"}
    except Exception as e:
        return {"ok": False, "error": f"瀹夎澶辫触: {str(e)}"}


async def uninstall(skill_id: str) -> dict:
    """鍗歌浇鎶€鑳斤紙鍒犻櫎鏂囦欢锛?""
    target = _skill_path(skill_id)
    if not os.path.exists(target):
        return {"ok": False, "error": "鎶€鑳芥湭瀹夎"}
    try:
        shutil.rmtree(target)
        return {"ok": True, "skill_id": skill_id, "uninstalled": True}
    except Exception as e:
        return {"ok": False, "error": f"鍗歌浇澶辫触: {str(e)}"}


async def load_skill_module(skill_id: str) -> Optional[object]:
    """鍔ㄦ€佸姞杞芥妧鑳芥ā鍧楋紙鐑姞杞斤級"""
    manifest = get_manifest(skill_id)
    if not manifest:
        return None
    entry = manifest.get("entry", "main.py")
    entry_path = os.path.join(_skill_path(skill_id), entry)
    if not os.path.exists(entry_path):
        return None
    try:
        spec = importlib.util.spec_from_file_location(f"skill_{skill_id}", entry_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    except Exception:
        pass
    return None


def create_skill_package(skill_id: str, output_path: str) -> dict:
    """鍒涘缓鎶€鑳藉垎鍙?ZIP 鍖?""
    target = _skill_path(skill_id)
    if not os.path.exists(target):
        return {"ok": False, "error": "鎶€鑳芥湭瀹夎"}
    manifest = get_manifest(skill_id)
    if not manifest:
        return {"ok": False, "error": "鎶€鑳芥竻鍗曚涪澶?}

    zip_path = os.path.join(output_path, f"{skill_id}-v{manifest.get('version','0')}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(target):
            for f in files:
                fp = os.path.join(root, f)
                arcname = os.path.relpath(fp, target)
                zf.write(fp, arcname)

    return {"ok": True, "path": zip_path, "size": os.path.getsize(zip_path)}