锘?""GitHub MCP Agent 鈥?GitHub API 闆嗘垚
鑳藉姏锛氫粨搴撶姸鎬?Issues/PRs/Workflows/浠ｇ爜鎼滅储"""
import os
import httpx
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_API = "https://api.github.com"

@dataclass
class RepoInfo:
    full_name: str
    description: str
    stars: int
    forks: int
    open_issues: int
    language: str
    default_branch: str
    updated_at: str

class GitHubAgent:
    """GitHub 鎿嶄綔Agent 鈥?鐪熷疄API璋冪敤"""

    @staticmethod
    def _headers():
        h = {"Accept": "application/vnd.github.v3+json", "User-Agent": "FridayAI-OS"}
        if GITHUB_TOKEN:
            h["Authorization"] = f"token {GITHUB_TOKEN}"
        return h

    @staticmethod
    async def check_config() -> dict:
        """妫€鏌itHub閰嶇疆鐘舵€?""
        return {
            "configured": bool(GITHUB_TOKEN),
            "has_token": bool(GITHUB_TOKEN),
            "api_url": GITHUB_API,
        }

    @staticmethod
    async def get_repo(repo: str = "maopujie10-sys/mall-project") -> dict:
        """鑾峰彇浠撳簱淇℃伅"""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{GITHUB_API}/repos/{repo}", headers=GitHubAgent._headers())
                if r.status_code == 200:
                    d = r.json()
                    return {"ok": True, "repo": {
                        "name": d["full_name"], "desc": d["description"],
                        "stars": d["stargazers_count"], "forks": d["forks_count"],
                        "issues": d["open_issues_count"], "lang": d["language"],
                        "branch": d["default_branch"], "updated": d["updated_at"],
                        "size_mb": round(d["size"] / 1024, 1),
                    }}
                return {"ok": False, "error": f"GitHub杩斿洖 {r.status_code}", "detail": r.text[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def list_issues(repo: str = "maopujie10-sys/mall-project", state: str = "open", limit: int = 10) -> dict:
        """鍒楀嚭Issues"""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{GITHUB_API}/repos/{repo}/issues",
                    params={"state": state, "per_page": limit, "sort": "updated"},
                    headers=GitHubAgent._headers())
                if r.status_code == 200:
                    issues = []
                    for i in r.json():
                        if "pull_request" not in i:  # 杩囨护PR
                            issues.append({
                                "number": i["number"], "title": i["title"],
                                "state": i["state"], "user": i["user"]["login"],
                                "created": i["created_at"][:10],
                                "labels": [l["name"] for l in i["labels"]],
                                "url": i["html_url"],
                            })
                    return {"ok": True, "issues": issues, "count": len(issues)}
                return {"ok": False, "error": f"GitHub杩斿洖 {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def list_prs(repo: str = "maopujie10-sys/mall-project", state: str = "open", limit: int = 10) -> dict:
        """鍒楀嚭Pull Requests"""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{GITHUB_API}/repos/{repo}/pulls",
                    params={"state": state, "per_page": limit},
                    headers=GitHubAgent._headers())
                if r.status_code == 200:
                    prs = [{
                        "number": p["number"], "title": p["title"],
                        "state": p["state"], "user": p["user"]["login"],
                        "created": p["created_at"][:10],
                        "mergeable": p.get("mergeable"),
                        "url": p["html_url"],
                    } for p in r.json()]
                    return {"ok": True, "prs": prs, "count": len(prs)}
                return {"ok": False, "error": f"GitHub杩斿洖 {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def list_branches(repo: str = "maopujie10-sys/mall-project", limit: int = 20) -> dict:
        """鍒楀嚭鍒嗘敮"""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{GITHUB_API}/repos/{repo}/branches",
                    params={"per_page": limit},
                    headers=GitHubAgent._headers())
                if r.status_code == 200:
                    branches = [{"name": b["name"], "sha": b["commit"]["sha"][:7]} for b in r.json()]
                    return {"ok": True, "branches": branches, "count": len(branches)}
                return {"ok": False, "error": f"GitHub杩斿洖 {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def get_workflows(repo: str = "maopujie10-sys/mall-project", limit: int = 10) -> dict:
        """鍒楀嚭GitHub Actions宸ヤ綔娴?""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{GITHUB_API}/repos/{repo}/actions/workflows",
                    params={"per_page": limit},
                    headers=GitHubAgent._headers())
                if r.status_code == 200:
                    wfs = [{
                        "id": w["id"], "name": w["name"],
                        "state": w["state"], "path": w["path"],
                    } for w in r.json()["workflows"]]
                    return {"ok": True, "workflows": wfs, "count": len(wfs)}
                return {"ok": False, "error": f"GitHub杩斿洖 {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def get_commits(repo: str = "maopujie10-sys/mall-project", branch: str = "master", limit: int = 10) -> dict:
        """鍒楀嚭鏈€杩戞彁浜?""
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{GITHUB_API}/repos/{repo}/commits",
                    params={"sha": branch, "per_page": limit},
                    headers=GitHubAgent._headers())
                if r.status_code == 200:
                    commits = [{
                        "sha": c["sha"][:7], "message": c["commit"]["message"].split("\n")[0],
                        "author": c["commit"]["author"]["name"], "date": c["commit"]["author"]["date"][:10],
                    } for c in r.json()]
                    return {"ok": True, "commits": commits, "count": len(commits)}
                return {"ok": False, "error": f"GitHub杩斿洖 {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def create_issue(repo: str = "maopujie10-sys/mall-project", title: str = "", body: str = "") -> dict:
        """鍒涘缓Issue"""
        if not GITHUB_TOKEN:
            return {"ok": False, "error": "GitHub Token鏈厤缃?}
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(f"{GITHUB_API}/repos/{repo}/issues",
                    json={"title": title, "body": body},
                    headers=GitHubAgent._headers())
                if r.status_code == 201:
                    d = r.json()
                    return {"ok": True, "issue": {"number": d["number"], "url": d["html_url"]}}
                return {"ok": False, "error": f"鍒涘缓澶辫触 {r.status_code}", "detail": r.text[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def trigger_workflow(repo: str = "maopujie10-sys/mall-project", workflow_id: str = "", ref: str = "master") -> dict:
        """瑙﹀彂GitHub Actions宸ヤ綔娴?""
        if not GITHUB_TOKEN:
            return {"ok": False, "error": "GitHub Token鏈厤缃?}
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(f"{GITHUB_API}/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
                    json={"ref": ref},
                    headers=GitHubAgent._headers())
                return {"ok": r.status_code == 204, "status_code": r.status_code,
                        "note": "宸ヤ綔娴佸凡瑙﹀彂" if r.status_code == 204 else f"瑙﹀彂澶辫触 {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
