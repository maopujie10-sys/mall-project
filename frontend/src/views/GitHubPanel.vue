<template>
  <div class="gh-panel">
    <div class="page-header">
      <div><h2>🐙 GitHub MCP</h2><p>仓库管理 / Issues / PRs / Actions / 提交</p></div>
      <el-tag :type="configured ? 'success' : 'danger'" size="small">{{ configured ? '已配置' : '未配置Token' }}</el-tag>
    </div>

    <el-tabs v-model="tab" type="border-card">
      <el-tab-pane name="overview" label="概览">
        <el-row :gutter="16" v-if="repo">
          <el-col :span="6" v-for="s in stats" :key="s.label">
            <div class="metric-card"><div class="metric-label">{{ s.label }}</div><div class="metric-value">{{ s.value }}</div></div>
          </el-col>
        </el-row>
        <el-card shadow="never" style="margin-top:16px" v-if="repo">
          <div class="card-tt">{{ repo.name }}</div>
          <p style="color:var(--text-muted)">{{ repo.desc || '暂无描述' }}</p>
          <div style="display:flex;gap:16px;margin-top:12px;font-size:13px">
            <span>⭐ {{ repo.stars }}</span><span>⑂ {{ repo.forks }}</span>
            <span>📂 {{ repo.lang }}</span><span>🌿 {{ repo.branch }}</span>
          </div>
        </el-card>
        <el-card shadow="never" style="margin-top:16px" v-else>
          <el-skeleton :rows="4" animated />
        </el-card>
      </el-tab-pane>

      <el-tab-pane name="commits" label="提交记录">
        <el-table :data="commits" stripe size="small" height="500">
          <el-table-column prop="sha" label="SHA" width="90" />
          <el-table-column prop="message" label="提交信息" min-width="300" />
          <el-table-column prop="author" label="作者" width="120" />
          <el-table-column prop="date" label="日期" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="issues" label="Issues">
        <div class="tb-bar"><el-button type="primary" size="small" @click="showCreateIssue=true">创建Issue</el-button></div>
        <el-table :data="issues" stripe size="small" height="500">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="title" label="标题" min-width="300" />
          <el-table-column prop="state" label="状态" width="80">
            <template #default="{row}"><el-tag :type="row.state==='open'?'success':'info'" size="small">{{ row.state }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="user" label="创建者" width="100" />
          <el-table-column prop="created" label="日期" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="prs" label="PRs">
        <el-table :data="prs" stripe size="small" height="500">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="title" label="标题" min-width="300" />
          <el-table-column prop="state" label="状态" width="80" />
          <el-table-column prop="user" label="创建者" width="100" />
          <el-table-column prop="created" label="日期" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="workflows" label="Actions">
        <el-table :data="workflows" stripe size="small" height="500">
          <el-table-column prop="name" label="工作流名称" min-width="250" />
          <el-table-column prop="state" label="状态" width="100" />
          <el-table-column prop="path" label="路径" min-width="200" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="branches" label="分支">
        <el-table :data="branches" stripe size="small" height="500">
          <el-table-column prop="name" label="分支名" min-width="200" />
          <el-table-column prop="sha" label="最新提交" width="100" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showCreateIssue" title="创建 Issue" width="500">
      <el-form label-width="60">
        <el-form-item label="标题"><el-input v-model="issueTitle" placeholder="Issue 标题" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="issueBody" type="textarea" :rows="4" placeholder="描述" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showCreateIssue=false">取消</el-button><el-button type="primary" @click="doCreateIssue" :loading="creating">创建</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getGitHubConfig, getRepo, listCommits, listIssues, listPRs, listWorkflows, listBranches, createIssue } from '@/api/github'

const tab = ref('overview')
const configured = ref(false)
const repo = ref(null)
const commits = ref([])
const issues = ref([])
const prs = ref([])
const workflows = ref([])
const branches = ref([])
const showCreateIssue = ref(false)
const issueTitle = ref('')
const issueBody = ref('')
const creating = ref(false)

const stats = computed(() => {
  if (!repo.value) return []
  return [
    { label: '⭐ Stars', value: repo.value.stars },
    { label: '⑂ Forks', value: repo.value.forks },
    { label: '📂 Issues', value: repo.value.issues },
    { label: '📦 大小', value: repo.value.size_mb + 'MB' },
  ]
})

async function loadAll() {
  try {
    const cfg = await getGitHubConfig()
    configured.value = cfg?.data?.configured || false
    const [r, c, is, pr, wf, br] = await Promise.all([
      getRepo(), listCommits(), listIssues(), listPRs(), listWorkflows(), listBranches()
    ])
    if (r?.data?.repo) repo.value = r.data.repo
    if (c?.data?.commits) commits.value = c.data.commits
    if (is?.data?.issues) issues.value = is.data.issues
    if (pr?.data?.prs) prs.value = pr.data.prs
    if (wf?.data?.workflows) workflows.value = wf.data.workflows
    if (br?.data?.branches) branches.value = br.data.branches
  } catch { ElMessage.error('GitHub API调用失败，请检查GITHUB_TOKEN配置') }
}

async function doCreateIssue() {
  if (!issueTitle.value) return
  creating.value = true
  try {
    const res = await createIssue('maopujie10-sys/mall-project', issueTitle.value, issueBody.value)
    if (res?.data?.ok) { ElMessage.success('Issue已创建'); showCreateIssue.value = false; issueTitle.value = ''; issueBody.value = ''; listIssues().then(r=>issues.value=r?.data?.issues||[]) }
    else ElMessage.error('创建失败')
  } catch { ElMessage.error('创建失败') }
  creating.value = false
}

onMounted(loadAll)
</script>

<style scoped>
.gh-panel { padding: 24px; }
.page-header { display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px; }
.page-header h2 { margin:0 0 4px;font-size:20px; }
.page-header p { margin:0;font-size:13px;color:var(--text-muted); }
.metric-card { background:var(--bg-card);border-radius:8px;padding:18px;border:1px solid var(--border-color); }
.metric-label { font-size:12px;color:var(--text-muted);margin-bottom:6px; }
.metric-value { font-size:24px;font-weight:700; }
.card-tt { font-size:15px;font-weight:600;margin-bottom:8px; }
.tb-bar { margin-bottom:12px; }
</style>

