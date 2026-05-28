<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label="轮播图">
        <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showBannerForm(null)">新增轮播</el-button></div>
        <el-table :data="banners" stripe size="small" v-loading="bl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="title" label="标题" width="150" />
          <el-table-column prop="url" label="链接" show-overflow-tooltip />
          <el-table-column label="操作" width="200">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showBannerForm(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="delBanner(row.uuid)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="新闻">
        <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showNewsForm(null)">新增新闻</el-button></div>
        <el-table :data="news" stripe size="small" v-loading="nl">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="create_time" label="时间" width="160" />
          <el-table-column label="操作" width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showNewsForm(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="delNews(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="通知">
        <el-table :data="notifs" stripe size="small" v-loading="nfl">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="create_time" label="时间" width="160" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
    <el-dialog :title="editingBanner?.uuid?'编辑轮播':'新增轮播'" v-model="bannerDialog" width="400px">
      <el-form :model="bannerForm" label-width="80px">
        <el-form-item label="标题"><el-input v-model="bannerForm.title" /></el-form-item>
        <el-form-item label="图片URL"><el-input v-model="bannerForm.image_url" /></el-form-item>
        <el-form-item label="链接"><el-input v-model="bannerForm.url" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="bannerDialog=false">取消</el-button><el-button type="primary" @click="saveBanner">保存</el-button></template>
    </el-dialog>
    <el-dialog :title="editingNews?.id?'编辑新闻':'新增新闻'" v-model="newsDialog" width="400px">
      <el-form :model="newsForm" label-width="80px">
        <el-form-item label="标题"><el-input v-model="newsForm.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="newsForm.content" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="newsDialog=false">取消</el-button><el-button type="primary" @click="saveNews">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getBannerList, saveBanner, updateBanner, deleteBanner, getNewsList, saveNews, updateNews, deleteNews, getNotificationList } from '@/api/mall'
import { ElMessage, ElMessageBox } from 'element-plus'

const banners = ref([]); const bl = ref(false)
const news = ref([]); const nl = ref(false)
const notifs = ref([]); const nfl = ref(false)
const bannerDialog = ref(false); const newsDialog = ref(false)
const editingBanner = ref(null); const editingNews = ref(null)
const bannerForm = ref({ title: '', image_url: '', url: '' })
const newsForm = ref({ title: '', content: '' })

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
    ElMessage.success('成功'); bannerDialog.value = false; loadAll()
  } catch { ElMessage.error('失败') }
}
async function delBanner(uuid) { await ElMessageBox.confirm('确认删除?'); try { await deleteBanner(uuid); ElMessage.success('成功'); loadAll() } catch { ElMessage.error('失败') } }
function showNewsForm(row) { editingNews.value = row; newsForm.value = row ? { ...row } : { title: '', content: '' }; newsDialog.value = true }
async function saveNews() {
  try {
    if (editingNews.value) await updateNews(editingNews.value.id, newsForm.value)
    else await saveNews(newsForm.value)
    ElMessage.success('成功'); newsDialog.value = false; loadAll()
  } catch { ElMessage.error('失败') }
}
async function delNews(id) { await ElMessageBox.confirm('确认删除?'); try { await deleteNews(id); ElMessage.success('成功'); loadAll() } catch { ElMessage.error('失败') } }
onMounted(loadAll)
</script>