"""GitHub MCP Router -- GitHub API路由"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from agents.github_agent import GitHubAgent

router = APIRouter(prefix="/github", tags=["GitHub MCP"])

@router.get("/config")
async def check_config(_=Depends(verify_token)):
    """检查GitHub配置状态"""
    await handle_risk("L1", "查看GitHub配置")
    return await GitHubAgent.check_config()

@router.get("/repo")
async def get_repo(repo: str = "maopujie10-sys/mall-project", _=Depends(verify_token)):
    """获取仓库信息"""
    await handle_risk("L1", f"查看仓库 {repo}")
    return await GitHubAgent.get_repo(repo)

@router.get("/issues")
async def list_issues(repo: str = "maopujie10-sys/mall-project", state: str = "open", limit: int = 10, _=Depends(verify_token)):
    """列出Issues"""
    await handle_risk("L1", f"查看 {repo} Issues")
    return await GitHubAgent.list_issues(repo, state, limit)

@router.get("/prs")
async def list_prs(repo: str = "maopujie10-sys/mall-project", state: str = "open", limit: int = 10, _=Depends(verify_token)):
    """列出Pull Requests"""
    await handle_risk("L1", f"查看 {repo} PRs")
    return await GitHubAgent.list_prs(repo, state, limit)

@router.get("/branches")
async def list_branches(repo: str = "maopujie10-sys/mall-project", limit: int = 20, _=Depends(verify_token)):
    """列出分支"""
    await handle_risk("L1", f"查看 {repo} 分支")
    return await GitHubAgent.list_branches(repo, limit)

@router.get("/workflows")
async def list_workflows(repo: str = "maopujie10-sys/mall-project", limit: int = 10, _=Depends(verify_token)):
    """列出Actions工作流"""
    await handle_risk("L1", f"查看 {repo} 工作流")
    return await GitHubAgent.get_workflows(repo, limit)

@router.get("/commits")
async def list_commits(repo: str = "maopujie10-sys/mall-project", branch: str = "master", limit: int = 10, _=Depends(verify_token)):
    """列出最近提交"""
    await handle_risk("L1", f"查看 {repo} 提交")
    return await GitHubAgent.get_commits(repo, branch, limit)

@router.post("/issues")
async def create_issue(repo: str = "maopujie10-sys/mall-project", title: str = "", body: str = "", _=Depends(verify_token)):
    """创建Issue"""
    await handle_risk("L2", f"创建Issue到 {repo}")
    return await GitHubAgent.create_issue(repo, title, body)

@router.post("/workflows/trigger")
async def trigger_workflow(repo: str = "maopujie10-sys/mall-project", workflow_id: str = "", ref: str = "master", _=Depends(verify_token)):
    """触发Actions工作流"""
    await handle_risk("L3", f"触发 {repo} 工作流 {workflow_id}", need_confirm=True)
    return await GitHubAgent.trigger_workflow(repo, workflow_id, ref)
