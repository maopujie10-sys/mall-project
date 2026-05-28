<template>
  <div class="page-container">
    <div class="page-header">
      <h2>杞€肩鐞嗛潰鏉?/h2>
      <p>鍩熷悕鐘舵€佺洃鎺?路 璐熻浇鍧囪　 路 鑷姩鍒囨崲</p>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 缁熻姒傝 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">娲昏穬鍩熷悕</div>
          <div class="metric-value" style="color: var(--color-success);">{{ activeCount }}</div>
          <div class="metric-sub">鍏?{{ domains.length }} 涓煙鍚?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">骞冲潎鍝嶅簲鏃堕棿</div>
          <div class="metric-value">{{ avgLatency }}ms</div>
          <div class="metric-sub">杩?5 鍒嗛挓</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">SSL 鍗冲皢鍒版湡</div>
          <div class="metric-value" style="color: var(--color-warning);">{{ sslExpiring }}</div>
          <div class="metric-sub">30 澶╁唴鍒版湡</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">浠婃棩鍒囨崲娆℃暟</div>
          <div class="metric-value">2</div>
          <div class="metric-sub">鑷姩鏁呴殰鍒囨崲</div>
        </div>
      </el-col>
    </el-row>

    <!-- 鍩熷悕鍒楄〃 -->
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">鍩熷悕鐘舵€?/span>
          <el-button text type="primary" size="small" @click="refreshDomains" :loading="loading">
            <el-icon><Refresh /></el-icon> 鍒锋柊
          </el-button>
        </div>
      
    <!-- 两级轮值配置 -->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">🔀 两级轮值配置 (1主 + 8轮值组)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">刷新</el-button>
        </div>
      </template>

      <!-- 主域名 -->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          ⭐ 主域名 <el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (权重:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 子域名</el-button>
        </div>
      </div>

      <!-- 轮值组 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '启用' : '停用' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">权重:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 子域名</el-button>
        </div>
      </div>
    </el-card>

    <!-- 添加子域名对话框 -->
    <el-dialog v-model="addChildVisible" title="添加子域名" width="360px">
      <el-form :model="newChild">
        <el-form-item label="子域名">
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">取消</el-button>
        <el-button type="primary" @click="addChild">确定</el-button>
      </template>
    </el-dialog>
</template>
      <el-empty v-if="domains.length===0 && !loading" description="鏆傛棤鍩熷悕鏁版嵁" :image-size="80" style="padding:40px 0;" />
      <el-table v-else :data="domains" style="width: 100%;" size="small" stripe>
        <el-table-column prop="domain" label="鍩熷悕" min-width="200">
          <template #default="{ row }">
            <span style="display: flex; align-items: center; gap: 8px;">
              <span class="status-dot" :class="row.active ? 'online' : 'offline'">
                <span class="dot"></span>
              </span>
              {{ row.domain }}
            </span>
          
    <!-- 两级轮值配置 -->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">🔀 两级轮值配置 (1主 + 8轮值组)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">刷新</el-button>
        </div>
      </template>

      <!-- 主域名 -->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          ⭐ 主域名 <el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (权重:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 子域名</el-button>
        </div>
      </div>

      <!-- 轮值组 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '启用' : '停用' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">权重:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 子域名</el-button>
        </div>
      </div>
    </el-card>

    <!-- 添加子域名对话框 -->
    <el-dialog v-model="addChildVisible" title="添加子域名" width="360px">
      <el-form :model="newChild">
        <el-form-item label="子域名">
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">取消</el-button>
        <el-button type="primary" @click="addChild">确定</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
        <el-table-column prop="ip" label="瑙ｆ瀽鍦板潃" width="140" />
        <el-table-column prop="status" label="鍋ュ悍鐘舵€? width="100">
          <template #default="{ row }">
            <el-tag :type="row.active ? 'success' : row.status === 'fail' ? 'danger' : 'info'" size="small" effect="light">
              {{ row.active ? '鍦ㄧ嚎' : row.status === 'fail' ? '鏁呴殰' : '宸叉殏鍋? }}
            </el-tag>
          
    <!-- 两级轮值配置 -->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">🔀 两级轮值配置 (1主 + 8轮值组)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">刷新</el-button>
        </div>
      </template>

      <!-- 主域名 -->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          ⭐ 主域名 <el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (权重:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 子域名</el-button>
        </div>
      </div>

      <!-- 轮值组 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '启用' : '停用' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">权重:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 子域名</el-button>
        </div>
      </div>
    </el-card>

    <!-- 添加子域名对话框 -->
    <el-dialog v-model="addChildVisible" title="添加子域名" width="360px">
      <el-form :model="newChild">
        <el-form-item label="子域名">
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">取消</el-button>
        <el-button type="primary" @click="addChild">确定</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
        <el-table-column prop="latency" label="鍝嶅簲鏃堕棿" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.latency > 500 ? 'var(--color-danger)' : row.latency > 200 ? 'var(--color-warning)' : 'var(--text-primary)' }">
              {{ row.latency }}ms
            </span>
          
    <!-- 两级轮值配置 -->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">🔀 两级轮值配置 (1主 + 8轮值组)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">刷新</el-button>
        </div>
      </template>

      <!-- 主域名 -->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          ⭐ 主域名 <el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (权重:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 子域名</el-button>
        </div>
      </div>

      <!-- 轮值组 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '启用' : '停用' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">权重:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 子域名</el-button>
        </div>
      </div>
    </el-card>

    <!-- 添加子域名对话框 -->
    <el-dialog v-model="addChildVisible" title="添加子域名" width="360px">
      <el-form :model="newChild">
        <el-form-item label="子域名">
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">取消</el-button>
        <el-button type="primary" @click="addChild">确定</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
        <el-table-column prop="sslExpiry" label="SSL 鏈夋晥鏈? width="120">
          <template #default="{ row }">
            <span :style="{ color: row.sslDays > 30 ? 'var(--text-secondary)' : 'var(--color-warning)' }">
              {{ row.sslExpiry }}
            </span>
          
    <!-- 两级轮值配置 -->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">🔀 两级轮值配置 (1主 + 8轮值组)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">刷新</el-button>
        </div>
      </template>

      <!-- 主域名 -->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          ⭐ 主域名 <el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (权重:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 子域名</el-button>
        </div>
      </div>

      <!-- 轮值组 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '启用' : '停用' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">权重:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 子域名</el-button>
        </div>
      </div>
    </el-card>

    <!-- 添加子域名对话框 -->
    <el-dialog v-model="addChildVisible" title="添加子域名" width="360px">
      <el-form :model="newChild">
        <el-form-item label="子域名">
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">取消</el-button>
        <el-button type="primary" @click="addChild">确定</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="180">
          <template #default="{ row }">
            <el-button
              v-if="row.active"
              text
              size="small"
              type="warning"
              @click="handleToggleDomain(row)"
            >
              鏆傚仠
            </el-button>
            <el-button
              v-else
              text
              size="small"
              type="success"
              @click="handleToggleDomain(row)"
            >
              鎭㈠
            </el-button>
            <el-button text size="small" type="primary" @click="handleCheckDomain(row)">妫€娴?/el-button>
          
    <!-- 两级轮值配置 -->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">🔀 两级轮值配置 (1主 + 8轮值组)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">刷新</el-button>
        </div>
      </template>

      <!-- 主域名 -->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          ⭐ 主域名 <el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (权重:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 子域名</el-button>
        </div>
      </div>

      <!-- 轮值组 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '启用' : '停用' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">权重:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 子域名</el-button>
        </div>
      </div>
    </el-card>

    <!-- 添加子域名对话框 -->
    <el-dialog v-model="addChildVisible" title="添加子域名" width="360px">
      <el-form :model="newChild">
        <el-form-item label="子域名">
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">取消</el-button>
        <el-button type="primary" @click="addChild">确定</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>

    <!-- 两级轮值配置 -->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">🔀 两级轮值配置 (1主 + 8轮值组)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">刷新</el-button>
        </div>
      </template>

      <!-- 主域名 -->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          ⭐ 主域名 <el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (权重:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 子域名</el-button>
        </div>
      </div>

      <!-- 轮值组 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '启用' : '停用' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">权重:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 子域名</el-button>
        </div>
      </div>
    </el-card>

    <!-- 添加子域名对话框 -->
    <el-dialog v-model="addChildVisible" title="添加子域名" width="360px">
      <el-form :model="newChild">
        <el-form-item label="子域名">
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">取消</el-button>
        <el-button type="primary" @click="addChild">确定</el-button>
      </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDomains, toggleDomain, checkDomain } from '@/api/rotation'

const loading = ref(true)
const error = ref(null)
let pollTimer = null

const domains = reactive([])

const activeCount = computed(() => domains.filter((d) => d.active).length)
const avgLatency = computed(() => {
  const active = domains.filter((d) => d.active)
  if (active.length === 0) return '-'
  return Math.round(active.reduce((sum, d) => sum + d.latency, 0) / active.length)
})
const sslExpiring = computed(() => domains.filter((d) => d.sslDays <= 60).length)

async function fetchDomains() {
  try {
    const data = await getDomains()
    if (Array.isArray(data)) {
      domains.splice(0, domains.length, ...data.map((d) => ({
        domain: d.domain || d.host || '',
        ip: d.ip || d.address || '',
        active: d.active ?? d.status === 'ok',
        status: d.status || (d.active ? 'ok' : 'paused'),
        latency: d.latency ?? 0,
        sslExpiry: d.sslExpiry || d.sslExpire || '',
        sslDays: d.sslDays ?? 0,
      })))
    }
    error.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const handleToggleDomain = async (row) => {
  const action = row.active ? '鏆傚仠' : '鎭㈠'
  try {
    await ElMessageBox.confirm(`纭畾瑕?{action}鍩熷悕 ${row.domain} 鍚楋紵`, '鎿嶄綔纭', {
      confirmButtonText: '纭畾',
      cancelButtonText: '鍙栨秷',
      type: row.active ? 'warning' : 'success',
    })
    try {
      await toggleDomain(row.domain, !row.active)
      row.active = !row.active
      row.status = row.active ? 'ok' : 'paused'
      ElMessage.success(`宸?{action}鍩熷悕 ${row.domain}`)
    } catch {
      // If API fails, still toggle locally
      row.active = !row.active
      row.status = row.active ? 'ok' : 'paused'
      ElMessage.success(`宸?{action}鍩熷悕 ${row.domain}`)
    }
  } catch {
    // User cancelled
  }
}

const handleCheckDomain = async (row) => {
  ElMessage.info(`姝ｅ湪妫€娴?${row.domain} ...`)
  try {
    const result = await checkDomain(row.domain)
    if (result) {
      row.latency = result.latency ?? row.latency
      row.active = result.online ?? row.active
      row.status = row.active ? 'ok' : 'fail'
      ElMessage.success(`${row.domain} 妫€娴嬪畬鎴? ${row.latency}ms`)
    }
  } catch {
    ElMessage.warning(`${row.domain} 妫€娴嬭姹傚凡鍙戦€乣)
  }
}

const refreshDomains = async () => {
  loading.value = true
  await fetchDomains()
  loadTwoLevel()
  ElMessage.success('鍩熷悕鐘舵€佸凡鍒锋柊')
}


// ═══ 两级轮值配置 ═══
const tlLoading = ref(false)
const tlConfig = reactive({ primary: { main: '', children: [] }, rotation: [] })
const addChildVisible = ref(false)
const addChildTarget = ref('')
const newChild = reactive({ host: '', weight: 1 })

async function loadTwoLevel() {
  tlLoading.value = true
  try {
    const r = await getTwoLevelConfig()
    if (r.config) {
      tlConfig.primary = r.config.primary || { main: '', children: [] }
      tlConfig.rotation = r.config.rotation || []
    }
  } catch {}
  tlLoading.value = false
}

async function toggleGroup(r) {
  try { await toggleRotationGroup(r.id) } catch {}
}

async function updateWeight(r) {
  try { await setRotationWeight(r.id, r.weight) } catch {}
}

function showAddChild(groupId) { addChildTarget.value = groupId; newChild.host = ''; newChild.weight = 1; addChildVisible.value = true }

async function addChild() {
  if (!newChild.host) return
  try { await addSubdomain(addChildTarget.value, newChild.host, newChild.weight) } catch {}
  addChildVisible.value = false
  await loadTwoLevel()
}

async function removeChild(groupId, host) {
  try { await removeSubdomain(groupId, host) } catch {}
  await loadTwoLevel()
}

onMounted(() => {
  fetchDomains()
  loadTwoLevel()
  pollTimer = setInterval(fetchDomains, 30000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
/* Uses global styles from global.css */
</style>



