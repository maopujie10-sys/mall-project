"""Skill Loader - ZIP Plugin Loader"""
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
    ''''''
    return os.path.join(SKILLS_DIR, skill_id)


def get_manifest(skill_id: str) -> Optional[dict]:
    ''" manifest.json''"
    mp = os.path.join(_skill_path(skill_id), "skill.json")
    if os.path.exists(mp):
        with open(mp, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def list_installed() -> list[dict]:
    ''''''
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
    ''" ZIP ''"
    if not os.path.exists(zip_path):
        return {"ok": False, "error": "ZIP "}

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            #  manifest
            if "skill.json" not in zf.namelist():
                return {"ok": False, "error": "ZIP  skill.json"}
            manifest = json.loads(zf.read("skill.json"))
            skill_id = manifest.get("id", '')
            if not skill_id:
                return {"ok": False, "error": "skill.json  id "}

            
            existing = get_manifest(skill_id)
            if existing:
                from packaging.version import parse as vp
                if existing.get("version", "0") >= manifest.get("version", "0"):
                    return {"ok": False, "error": f" {existing['version']},"}

            # :
            dangerous = [n for n in zf.namelist() if n.startswith("..") or "/.." in n or n.startswith("/")]
            if dangerous:
                return {"ok": False, "error": f"ZIP : {dangerous}"}

            
            target = _skill_path(skill_id)
            if os.path.exists(target):
                shutil.rmtree(target)
            os.makedirs(target, exist_ok=True)
            zf.extractall(target)

            
            manifest["installed_at"] = datetime.now().isoformat()
            manifest["install_source"] = source
            manifest["install_path"] = target
            with open(os.path.join(target, "skill.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)

            
            entry = manifest.get("entry", "main.py")
            entry_path = os.path.join(target, entry)
            if not os.path.exists(entry_path):
                return {"ok": True, "warning": f" {entry} ,", "skill_id": skill_id, "manifest": manifest}

            return {"ok": True, "skill_id": skill_id, "manifest": manifest, "path": target}

    except zipfile.BadZipFile:
        return {"ok": False, "error": "ZIP "}
    except json.JSONDecodeError:
        return {"ok": False, "error": "skill.json "}
    except Exception as e:
        return {"ok": False, "error": f": {str(e)}"}


async def uninstall(skill_id: str) -> dict:
    ''"()''"
    target = _skill_path(skill_id)
    if not os.path.exists(target):
        return {"ok": False, "error": ''}
    try:
        shutil.rmtree(target)
        return {"ok": True, "skill_id": skill_id, "uninstalled": True}
    except Exception as e:
        return {"ok": False, "error": f": {str(e)}"}


async def load_skill_module(skill_id: str) -> Optional[object]:
    ''"()''"
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
    ''" ZIP ''"
    target = _skill_path(skill_id)
    if not os.path.exists(target):
        return {"ok": False, "error": ''}
    manifest = get_manifest(skill_id)
    if not manifest:
        return {"ok": False, "error": ''}

    zip_path = os.path.join(output_path, f"{skill_id}-v{manifest.get('version','0')}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(target):
            for f in files:
                fp = os.path.join(root, f)
                arcname = os.path.relpath(fp, target)
                zf.write(fp, arcname)

    return {"ok": True, "path": zip_path, "size": os.path.getsize(zip_path)}