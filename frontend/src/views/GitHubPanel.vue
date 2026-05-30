<template>
  <div class="gh-panel">
    <div class="page-header">
      <div><h2>馃悪 GitHub MCP</h2><p>浠撳簱绠＄悊 / Issues / PRs / Actions / 鎻愪氦</p></div>
      <el-tag :type="configured ? 'success' : 'danger'" size="small">{{ configured ? '宸查厤缃' : '鏈厤缃甌oken' }}</el-tag>
    </div>

    <el-tabs v-model="tab" type="border-card">
      <el-tab-pane name="overview" label="姒傝">
        <el-row :gutter="16" v-if="repo">
          <el-col :span="6" v-for="s in stats" :key="s.label">
            <div class="metric-card"><div class="metric-label">{{ s.label }}</div><div class="metric-value">{{ s.value }}</div></div>
          </el-col>
        </el-row>
        <el-card shadow="never" style="margin-top:16px" v-if="repo">
          <div class="card-tt">{{ repo.name }}</div>
          <p style="color:var(--text-muted)">{{ repo.desc || '鏆傛棤鎻忚堪' }}</p>
          <div style="display:flex;gap:16px;margin-top:12px;font-size:13px">
            <span>猸?{{ repo.stars }}</span><span>鈶?{{ repo.forks }}</span>
            <span>馃搨 {{ repo.lang }}</span><span>馃尶 {{ repo.branch }}</span>
          </div>
        </el-card>
        <el-card shadow="never" style="margin-top:16px" v-else>
          <el-skeleton :rows="4" animated />
        </el-card>
      </el-tab-pane>

      <el-tab-pane name="commits" label="鎻愪氦璁板綍">
        <el-table :data="commits" stripe size="small" height="500">
          <el-table-column prop="sha" label="SHA" width="90" />
          <el-table-column prop="message" label="鎻愪氦淇℃伅" min-width="300" />
          <el-table-column prop="author" label="浣滆€? width="120" />
          <el-table-column prop="date" label="鏃ユ湡" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="issues" label="Issues">
        <div class="tb-bar"><el-button type="primary" size="small" @click="showCreateIssue=true">鍒涘缓Issue</el-button></div>
        <el-table :data="issues" stripe size="small" height="500">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="title" label="鏍囬" min-width="300" />
          <el-table-column prop="state" label="鐘舵€? width="80">
            <template #default="{row}"><el-tag :type="row.state==='open'?'success':'info'" size="small">{{ row.state }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="user" label="鍒涘缓鑰? width="100" />
          <el-table-column prop="created" label="鏃ユ湡" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="prs" label="PRs">
        <el-table :data="prs" stripe size="small" height="500">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="title" label="鏍囬" min-width="300" />
          <el-table-column prop="state" label="鐘舵€? width="80" />
          <el-table-column prop="user" label="鍒涘缓鑰? width="100" />
          <el-table-column prop="created" label="鏃ユ湡" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="workflows" label="Actions">
        <el-table :data="workflows" stripe size="small" height="500">
          <el-table-column prop="name" label="宸ヤ綔娴佸悕绉? min-width="250" />
          <el-table-column prop="state" label="鐘舵€? width="100" />
          <el-table-column prop="path" label="璺緞" min-width="200" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane name="branches" label="鍒嗘敮">
        <el-table :data="branches" stripe size="small" height="500">
          <el-table-column prop="name" label="鍒嗘敮鍚? min-width="200" />
          <el-table-column prop="sha" label="鏈€鏂版彁浜? width="100" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showCreateIssue" title="鍒涘缓 Issue" width="500">
      <el-form label-width="60">
        <el-form-item label="鏍囬"><el-input v-model="issueTitle" placeholder="Issue 鏍囬" /></el-form-item>
        <el-form-item label="鍐呭"><el-input v-model="issueBody" type="textarea" :rows="4" placeholder="鎻忚堪" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showCreateIssue=false">鍙栨秷</el-button><el-button type="primary" @click="doCreateIssue" :loading="creating">鍒涘缓</el-button></template>
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
    { label: '猸?Stars', value: repo.value.stars },
    { label: '鈶?Forks', value: repo.value.forks },
    { label: '馃搨 Issues', value: repo.value.issues },
    { label: '馃摝 澶у皬', value: repo.value.size_mb + 'MB' },
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
  } catch { ElMessage.error('GitHub API ITHUB_TOKEN') }
}

async function doCreateIssue() {
  if (!issueTitle.value) return
  creating.value = true
  try {
    const res = await createIssue('maopujie10-sys/mall-project', issueTitle.value, issueBody.value)
    if (res?.data?.ok) { ElMessage.success('Issue宸插垱寤?); showCreateIssue.value = false; issueTitle.value = ''; issueBody.value = ''; listIssues().then(r=>issues.value=r?.data?.issues||[]) }
    else ElMessage.error('鍒涘缓澶辫触')
  } catch { ElMessage.error('鍒涘缓澶辫触') }
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

