<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label=''>
        <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showBannerForm(null)">OK</el-button></div>
        <el-table :data="banners" stripe size="small" v-loading="bl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="title" label='' width="150" />
          <el-table-column prop="url" label='' show-overflow-tooltip />
          <el-table-column label='' width="200">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showBannerForm(row)">OK</el-button>
              <el-button size="small" link type="danger" @click="delBanner(row.uuid)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showNewsForm(null)">OK</el-button></div>
        <el-table :data="news" stripe size="small" v-loading="nl">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label='' />
          <el-table-column prop="create_time" label='' width="160" />
          <el-table-column label='' width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showNewsForm(row)">OK</el-button>
              <el-button size="small" link type="danger" @click="delNews(row.id)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label='通知'>
        <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showNotifForm">发送通知</el-button></div>
        <el-table :data="notifs" stripe size="small" v-loading="nfl">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label='标题' />
          <el-table-column prop="create_time" label='时间' width="160" />
          <el-table-column label='操作' width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showNotifForm(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="delNotif(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    <el-dialog :title="editingBanner?.uuid?'':''" v-model="bannerDialog" width="400px">
      <el-form :model="bannerForm" label-width="80px">
        <el-form-item label=''><el-input v-model="bannerForm.title" /></el-form-item>
        <el-form-item label="URL"><el-input v-model="bannerForm.image_url" /></el-form-item>
        <el-form-item label=''><el-input v-model="bannerForm.url" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="bannerDialog=false">OK</el-button><el-button type="primary" @click="saveBanner">OK</el-button></template>
    </el-dialog>
    <el-dialog :title="editingNews?.id?'':''" v-model="newsDialog" width="400px">
      <el-form :model="newsForm" label-width="80px">
        <el-form-item label=''><el-input v-model="newsForm.title" /></el-form-item>
        <el-form-item label=''><el-input v-model="newsForm.content" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="newsDialog=false">OK</el-button><el-button type="primary" @click="saveNews">OK</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getBannerList, saveBanner, updateBanner, deleteBanner, getNewsList, saveNews, updateNews, deleteNews, getNotificationList, saveNotification, updateNotification, deleteNotification } from '@/api/mall'
import { ElMessage, ElMessageBox } from 'element-plus'

const banners = ref([]); const bl = ref(false)
const news = ref([]); const nl = ref(false)
const notifs = ref([]); const nfl = ref(false)
const bannerDialog = ref(false); const newsDialog = ref(false); const notifDialog = ref(false)
const editingBanner = ref(null); const editingNews = ref(null); const editingNotif = ref(null)
const bannerForm = ref({ title: '', image_url: '', url: '' })
const newsForm = ref({ title: '', content: '' })
const notifForm = ref({ title: '', content: '' })

async function loadAll() {
  bl.value = nl.value = nfl.value = true
  try { const r = await getBannerList(); banners.value = r.list || r.records || [] } catch { }
  try { const r = await getNewsList(); news.value = r.list || r.records || [] } catch { }
  try { const r = await getNotificationList(); notifs.value = r.list || r.records || [] } catch { }
  bl.value = nl.value = nfl.value = false
}
function showBannerForm(row) { editingBanner.value = row; bannerForm.value = row ? { ...row } : { title: '', image_url: '', url: '' }; bannerDialog.value = true }
async function saveBanner() {
  try {
    if (editingBanner.value) await updateBanner(editingBanner.value.uuid, bannerForm.value)
    else await saveBanner(bannerForm.value)
    ElMessage.success('OK'); bannerDialog.value = false; loadAll()
  } catch { ElMessage.error('Error') }
}
async function delBanner(uuid) { await ElMessageBox.confirm('?'); try { await deleteBanner(uuid); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
function showNewsForm(row) { editingNews.value = row; newsForm.value = row ? { ...row } : { title: '', content: '' }; newsDialog.value = true }
async function saveNews() {
  try {
    if (editingNews.value) await updateNews(editingNews.value.id, newsForm.value)
    else await saveNews(newsForm.value)
    ElMessage.success('OK'); newsDialog.value = false; loadAll()
  } catch { ElMessage.error('Error') }
}
async function delNews(id) { await ElMessageBox.confirm('?'); try { await deleteNews(id); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
// 通知
function showNotifForm(row) { editingNotif.value = row; notifForm.value = row ? { ...row } : { title: '', content: '' }; notifDialog.value = true }
async function saveNotif() {
  try {
    if (editingNotif.value?.id) await updateNotification(editingNotif.value.id, notifForm.value)
    else await saveNotification(notifForm.value)
    ElMessage.success('OK'); notifDialog.value = false; loadAll()
  } catch { ElMessage.error('Error') }
}
async function delNotif(id) { await ElMessageBox.confirm('确认删除?'); try { await deleteNotification(id); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
onMounted(loadAll)
</script>