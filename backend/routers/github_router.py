''"GitHub MCP Router -- GitHub API''"
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from agents.github_agent import GitHubAgent

router = APIRouter(prefix="/github", tags=["GitHub MCP"])

@router.get("/config")
async def check_config(_=Depends(verify_token)):
    ''"GitHub''"
    await handle_risk("L1", "GitHub")
    return await GitHubAgent.check_config()

@router.get("/repo")
async def get_repo(repo: str = "maopujie10-sys/mall-project", _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", f" {repo}")
    return await GitHubAgent.get_repo(repo)

@router.get("/issues")
async def list_issues(repo: str = "maopujie10-sys/mall-project", state: str = "open", limit: int = 10, _=Depends(verify_token)):
    ''"Issues''"
    await handle_risk("L1", f" {repo} Issues")
    return await GitHubAgent.list_issues(repo, state, limit)

@router.get("/prs")
async def list_prs(repo: str = "maopujie10-sys/mall-project", state: str = "open", limit: int = 10, _=Depends(verify_token)):
    ''"Pull Requests''"
    await handle_risk("L1", f" {repo} PRs")
    return await GitHubAgent.list_prs(repo, state, limit)

@router.get("/branches")
async def list_branches(repo: str = "maopujie10-sys/mall-project", limit: int = 20, _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", f" {repo} ")
    return await GitHubAgent.list_branches(repo, limit)

@router.get("/workflows")
async def list_workflows(repo: str = "maopujie10-sys/mall-project", limit: int = 10, _=Depends(verify_token)):
    ''"Actions''"
    await handle_risk("L1", f" {repo} ")
    return await GitHubAgent.get_workflows(repo, limit)

@router.get("/commits")
async def list_commits(repo: str = "maopujie10-sys/mall-project", branch: str = "master", limit: int = 10, _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", f" {repo} ")
    return await GitHubAgent.get_commits(repo, branch, limit)

@router.post("/issues")
async def create_issue(repo: str = "maopujie10-sys/mall-project", title: str = '', body: str = '', _=Depends(verify_token)):
    ''"Issue''"
    await handle_risk("L2", f"Issue {repo}")
    return await GitHubAgent.create_issue(repo, title, body)

@router.post("/workflows/trigger")
async def trigger_workflow(repo: str = "maopujie10-sys/mall-project", workflow_id: str = '', ref: str = "master", _=Depends(verify_token)):
    ''"Actions''"
    await handle_risk("L3", f" {repo}  {workflow_id}", need_confirm=True)
    return await GitHubAgent.trigger_workflow(repo, workflow_id, ref)
