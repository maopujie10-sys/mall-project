<template>
  <div class="page-container ocr-panel">
    <div class="page-header"><h2>OCR 识别</h2><p>图片文字识别 · 表格提取 · 多语言支持 · 批量处理</p></div>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>图片输入</span></template>
          <el-upload class="ocr-upload" drag :auto-upload="false" :on-change="handleFile" accept="image/*">
            <el-icon :size="48"><svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg></el-icon>
            <div class="el-upload__text">拖拽图片或<em>点击上传</em></div>
          </el-upload>
          <div style="margin-top:12px">
            或输入图片URL：<el-input v-model="imageUrl" placeholder="https://..." clearable style="margin-top:8px" />
          </div>
          <el-select v-model="lang" style="width:100%;margin-top:12px" placeholder="选择识别语言">
            <el-option label="中文简体" value="chi_sim" /><el-option label="中文繁体" value="chi_tra" />
            <el-option label="英文" value="eng" /><el-option label="日文" value="jpn" />
            <el-option label="韩文" value="kor" /><el-option label="自动检测" value="auto" />
          </el-select>
          <el-button type="primary" @click="runOcr" :loading="running" style="width:100%;margin-top:12px">开始识别</el-button>
        </el-card>

        <el-card shadow="never" style="margin-top:16px">
          <template #header><span>批量处理</span></template>
          <el-upload class="batch-upload" drag multiple :auto-upload="false" :on-change="handleBatch" accept="image/*">
            <div class="el-upload__text">拖拽多张图片或<em>点击批量上传</em></div>
          </el-upload>
          <div v-if="batchFiles.length" style="margin-top:12px">
            <el-tag v-for="f in batchFiles" :key="f.name" closable @close="batchFiles=batchFiles.filter(x=>x.name!==f.name)" size="small" style="margin-right:6px;margin-bottom:6px">{{ f.name }}</el-tag>
          </div>
          <el-button v-if="batchFiles.length" type="primary" @click="runBatch" :loading="batching" style="width:100%;margin-top:8px">批量识别 ({{ batchFiles.length }} 张)</el-button>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" v-if="ocrText">
          <template #header>
            <div class="result-header"><span>识别结果</span><el-button link type="primary" size="small" @click="copyText">复制</el-button><el-button link type="primary" size="small" @click="exportText">导出</el-button></div>
          </template>
          <pre class="ocr-result">{{ ocrText }}</pre>
          <el-divider />
          <div class="stats-row">
            <span>字符数: {{ ocrText.length }}</span>
            <span>置信度: {{ confidence }}%</span>
            <span>耗时: {{ elapsed }}ms</span>
          </div>
        </el-card>

        <el-card shadow="never" style="margin-top:16px">
          <template #header><span>识别历史</span></template>
          <el-table :data="ocrHistory" stripe size="small" max-height="300">
            <el-table-column prop="name" label="文件" min-width="140" show-overflow-tooltip />
            <el-table-column prop="text" label="内容预览" min-width="160" show-overflow-tooltip />
            <el-table-column prop="lang" label="语言" width="80" />
            <el-table-column prop="date" label="时间" width="100" />
            <el-table-column label="操作" width="80"><template #default="{row}"><el-button link type="primary" size="small" @click="ocrText=row.text;confidence=row.confidence">查看</el-button></template></el-table-column>
          </el-table>
          <el-empty v-if="!ocrHistory.length" description="暂无记录" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
const imageUrl = ref(''); const ocrResult = ref(''); const processing = ref(false)
function runOCR() { if(!imageUrl.value) return; processing.value = true; setTimeout(function() { processing.value = false; ocrResult.value = 'OCR识别结果将在此显示'; ElMessage.success('OCR完成') }, 1500) }
</script>

<style scoped>
.ocr-panel { padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 18px; margin: 0 0 4px; }
.page-header p { color: var(--text-muted); font-size: 13px; margin: 0; }
.ocr-upload { width: 100%; }
.ocr-result { white-space: pre-wrap; font-size: 15px; line-height: 1.8; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; max-height: 400px; overflow-y: auto; }
.result-header { display: flex; justify-content: space-between; align-items: center; }
.stats-row { display: flex; justify-content: space-around; font-size: 12px; color: var(--text-muted); }
</style>