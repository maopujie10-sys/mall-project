<template>
  <div class="gh-panel">
    <div class="page-header">
      <div><h2> GitHub MCP</h2><p> / Issues / PRs / Actions / </p></div>
      <el-tag :type="configured ? 'success' : 'danger'' size="small">{{ configured ? '? : 'oken' }}</el-tag>
    </div>

    <el-tabs v-model="tab" type="border-card">
      <el-tab-pane name="overview" :label="\('github.title')">
        <el-row :gutter="16" v-if="repo">
          <el-col :span="6" v-for="s in stats" :key="s.label">
            <div class="metric-card"><div class="metric-label">{{ s.label }}</div><div class="metric-value">{{ s.value }}</div></div>
          </el-col>
        </el-row>
        <el-card shadow="never" style="margin-top:16px" v-if="repo">
          <div class="card-tt">{{ repo.name }}</div>
          <p style="color:var(--text-muted)">{{ repo.desc || '' }}</p>
          <div style="display:flex;gap:16px;margin-top:12px;font-size:13px">
            <span>?{{ repo.stars }}</span><span>?{{ repo.forks }}</span>
            <span> {{ repo.lang }}</span><span> {{ repo.branch }}</span>
          </div>
        </el-card>
        <el-card shadow="never" style="margin-top:16px" v-else>
          <el-skeleton :rows="4" animated />
        </el-card>
      </el-tab-pane>

      <el-tab-pane name="commits" label=''>
        <el-table :data="commits" stripe size="small" height="500">
          <el-table-column prop="sha" label="SHA" width="90" />
          <el-table-column prop="message" :label="\('github.title')" min-width="300" />
          <el-table-column prop="author" label="? width="120" />
          <el-table-column prop="date" :label="\('github.title')" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="issues" label="Issues">
        <div class="tb-bar"><el-button type="primary" size="small" @click="showCreateIssue=true">Issue</el-button></div>
        <el-table :data="issues" stripe size="small" height="500">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="title" :label="\('github.title')" min-width="300" />
          <el-table-column prop="state" label="? width="80">
            <template #default="{row}"><el-tag :type="row.state==='open'?'success':'info' size="small">{{ row.state }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="user" label="? width="100" />
          <el-table-column prop="created" :label="\('github.title')" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="prs" label="PRs">
        <el-table :data="prs" stripe size="small" height="500">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="title" :label="\('github.title')" min-width="300" />
          <el-table-column prop="state" label="? width="80" />
          <el-table-column prop="user" label="? width="100" />
          <el-table-column prop="created" :label="\('github.title')" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="workflows" label="Actions">
        <el-table :data="workflows" stripe size="small" height="500">
          <el-table-column prop="name" label="? min-width="250" />
          <el-table-column prop="state" label="? width="100" />
          <el-table-column prop="path" :label="\('github.title')" min-width="200" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="branches" label=''>
        <el-table :data="branches" stripe size="small" height="500">
          <el-table-column prop="name" label="? min-width="200" />
          <el-table-column prop="sha" label="? width="100" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showCreateIssue" title=" Issue" width="500">
      <el-form label-width="60">
        <el-form-item :label="\('github.title')"><el-input v-model="issueTitle" placeholder="Issue " /></el-form-item>
        <el-form-item :label="\('github.title')"><el-input v-model="issueBody" type="textarea" :rows="4" placeholder='Enter...' /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showCreateIssue=false">OK</el-button><el-button type="primary" @click="doCreateIssue" :loading="creating">OK</el-button></template>
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
    { label: '?Stars', value: repo.value.stars },
    { label: '?Forks', value: repo.value.forks },
    { label: ' Issues', value: repo.value.issues },
    { label: '', value: repo.value.size_mb + 'MB' },
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
  } catch { ElMessage.error('GitHub APIITHUB_TOKEN') }
}

async function doCreateIssue() {
  if (!issueTitle.value) return
  creating.value = true
  try {
    const res = await createIssue('maopujie10-sys/mall-project', issueTitle.value, issueBody.value)
    if (res?.data?.ok) { ElMessage.success('Issue?); showCreateIssue.value = false; issueTitle.value = ''; issueBody.value = ''; listIssues().then(r=>issues.value=r?.data?.issues||[]) }
    else ElMessage.error('Error')
  } catch { ElMessage.error('Error') }
  creating.value = false
}

onMounted(loadAll)
</script>

<style scoped>
.gh-panel { padding: 24px; }
.page-header { display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px; }
.page-header h2 { margin:0 0 4px;font-size:20px; }
.page-header p { margin:0;font-size:13px;color:var(--text-muted); }
.metric-card { background: rgba(22,33,62,0.7);border-radius:8px;padding:18px;border:1px solid var(--border-color); }
.metric-label { font-size:12px;color:var(--text-muted);margin-bottom:6px; }
.metric-value { font-size:24px;font-weight:700; }
.card-tt { font-size:15px;font-weight:600;margin-bottom:8px; }
.tb-bar { margin-bottom:12px; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>

