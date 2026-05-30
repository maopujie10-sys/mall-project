''"GitHub MCP Agent -- GitHub API 
:/Issues/PRs/Workflows/''"
import os
import httpx
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", '')
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
    ''"GitHub Agent -- API''"

    @staticmethod
    def _headers():
        h = {"Accept": "application/vnd.github.v3+json", "User-Agent": "FridayAI-OS"}
        if GITHUB_TOKEN:
            h["Authorization"] = f"token {GITHUB_TOKEN}"
        return h

    @staticmethod
    async def check_config() -> dict:
        ''"GitHub''"
        return {
            "configured": bool(GITHUB_TOKEN),
            "has_token": bool(GITHUB_TOKEN),
            "api_url": GITHUB_API,
        }

    @staticmethod
    async def get_repo(repo: str = "maopujie10-sys/mall-project") -> dict:
        ''''''
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
                return {"ok": False, "error": f"GitHub {r.status_code}", "detail": r.text[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def list_issues(repo: str = "maopujie10-sys/mall-project", state: str = "open", limit: int = 10) -> dict:
        ''"Issues''"
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{GITHUB_API}/repos/{repo}/issues",
                    params={"state": state, "per_page": limit, "sort": "updated"},
                    headers=GitHubAgent._headers())
                if r.status_code == 200:
                    issues = []
                    for i in r.json():
                        if "pull_request" not in i:  # PR
                            issues.append({
                                "number": i["number"], "title": i["title"],
                                "state": i["state"], "user": i["user"]["login"],
                                "created": i["created_at"][:10],
                                "labels": [l["name"] for l in i["labels"]],
                                "url": i["html_url"],
                            })
                    return {"ok": True, "issues": issues, "count": len(issues)}
                return {"ok": False, "error": f"GitHub {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def list_prs(repo: str = "maopujie10-sys/mall-project", state: str = "open", limit: int = 10) -> dict:
        ''"Pull Requests''"
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
                return {"ok": False, "error": f"GitHub {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def list_branches(repo: str = "maopujie10-sys/mall-project", limit: int = 20) -> dict:
        ''''''
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{GITHUB_API}/repos/{repo}/branches",
                    params={"per_page": limit},
                    headers=GitHubAgent._headers())
                if r.status_code == 200:
                    branches = [{"name": b["name"], "sha": b["commit"]["sha"][:7]} for b in r.json()]
                    return {"ok": True, "branches": branches, "count": len(branches)}
                return {"ok": False, "error": f"GitHub {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def get_workflows(repo: str = "maopujie10-sys/mall-project", limit: int = 10) -> dict:
        ''"GitHub Actions''"
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
                return {"ok": False, "error": f"GitHub {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def get_commits(repo: str = "maopujie10-sys/mall-project", branch: str = "master", limit: int = 10) -> dict:
        ''''''
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
                return {"ok": False, "error": f"GitHub {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def create_issue(repo: str = "maopujie10-sys/mall-project", title: str = '', body: str = '') -> dict:
        ''"Issue''"
        if not GITHUB_TOKEN:
            return {"ok": False, "error": "GitHub Token"}
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(f"{GITHUB_API}/repos/{repo}/issues",
                    json={"title": title, "body": body},
                    headers=GitHubAgent._headers())
                if r.status_code == 201:
                    d = r.json()
                    return {"ok": True, "issue": {"number": d["number"], "url": d["html_url"]}}
                return {"ok": False, "error": f" {r.status_code}", "detail": r.text[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def trigger_workflow(repo: str = "maopujie10-sys/mall-project", workflow_id: str = '', ref: str = "master") -> dict:
        ''"GitHub Actions''"
        if not GITHUB_TOKEN:
            return {"ok": False, "error": "GitHub Token"}
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(f"{GITHUB_API}/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
                    json={"ref": ref},
                    headers=GitHubAgent._headers())
                return {"ok": r.status_code == 204, "status_code": r.status_code,
                        "note": '' if r.status_code == 204 else f" {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
