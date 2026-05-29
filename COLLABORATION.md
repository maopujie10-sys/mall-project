# COLLABORATION.md — Codex + Claude Code 协作规范

## 角色分工

### Codex（Windows 桌面）
- `mall-project` 仓库 — AI 源码开发
- 数据库表设计、迁移脚本
- 代码审查、架构设计
- Git 分支管理与 PR 发起

### Claude Code（服务器 45.192.97.37）
- `/home/data/projects/mall/` — 商城部署运维（Docker、Nginx）
- `/root/codex-review-package-20260527.tar.gz` — 审计包处理
- 线上数据库迁移执行
- 服务器监控与故障排查
- 商城运行环境维护

### 冲突区域
- 根目录 `docker-compose.yml`、`nginx.conf` — 两人都能改，改动前在 Issue 知会

## 仓库

| 仓库 | 用途 | 负责人 |
|------|------|--------|
| `maopujie10-sys/maopujie10` | 全量源码归档（只读） | Codex |
| `maopujie10-sys/mall-project` | AI 源码开发主仓库 | Codex |

## 分支策略

- `main` — 稳定，PR 合入
- `dev` — 开发主线
- Codex 分支：`codex/功能名`
- Claude Code 分支：`claude/功能名`

## 提交规范

```
[Codex] AI Agent 新增订单查询接口
[Claude] 修复 Nginx SSL 证书路径
```

- 不跨模块混提交
- force push 禁用于 `main` / `dev`

## 沟通约定

- 重大改动先开 Issue，标题加 `[协作]`
- Issue 内 @ 对方确认再动手
- 本文件修改需两人确认

---

最后更新：2026-05-27
