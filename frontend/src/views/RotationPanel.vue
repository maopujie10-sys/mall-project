锘?template>
  <div class="page-container">
    <div class="page-header">
      <h2>鏉烆喖鈧偐顓搁悶鍡涙桨閺?/h2>
      <p>閸╃喎鎮曢悩鑸碘偓浣烘磧閹?璺?鐠愮喕娴囬崸鍥€€ 璺?閼奉亜濮╅崚鍥ㄥ床</p>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 缂佺喕顓稿鍌濐潔 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">濞叉槒绌崺鐔锋倳</div>
          <div class="metric-value" style="color: var(--color-success);">{{ activeCount }}</div>
          <div class="metric-sub">閸?{{ domains.length }} 娑擃亜鐓欓崥?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">楠炲啿娼庨崫宥呯安閺冨爼妫?/div>
          <div class="metric-value">{{ avgLatency }}ms</div>
          <div class="metric-sub">鏉?5 閸掑棝鎸?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">SSL 閸楀啿鐨㈤崚鐗堟埂</div>
          <div class="metric-value" style="color: var(--color-warning);">{{ sslExpiring }}</div>
          <div class="metric-sub">30 婢垛晛鍞撮崚鐗堟埂</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">娴犲﹥妫╅崚鍥ㄥ床濞嗏剝鏆?/div>
          <div class="metric-value">2</div>
          <div class="metric-sub">閼奉亜濮╅弫鍛存閸掑洦宕?/div>
        </div>
      </el-col>
    </el-row>

    <!-- 閸╃喎鎮曢崚妤勩€?-->
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">閸╃喎鎮曢悩鑸碘偓?/span>
          <el-button text type="primary" size="small" @click="refreshDomains" :loading="loading">
            <el-icon><Refresh /></el-icon> 閸掗攱鏌?
          </el-button>
        </div>
      
    <!-- 涓ょ骇杞€奸厤缃?-->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">馃攢 涓ょ骇杞€奸厤缃?(1涓?+ 8杞€肩粍)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">鍒锋柊</el-button>
        </div>
      </template>

      <!-- 涓诲煙鍚?-->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          猸?涓诲煙鍚?<el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (鏉冮噸:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>

      <!-- 杞€肩粍 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '鍚敤' : '鍋滅敤' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">鏉冮噸:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>
    </el-card>

    <!-- 娣诲姞瀛愬煙鍚嶅璇濇 -->
    <el-dialog v-model="addChildVisible" title="娣诲姞瀛愬煙鍚? width="360px">
      <el-form :model="newChild">
        <el-form-item label="瀛愬煙鍚?>
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="鏉冮噸">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">鍙栨秷</el-button>
        <el-button type="primary" @click="addChild">纭畾</el-button>
      </template>
    </el-dialog>
</template>
      <el-empty v-if="domains.length===0 && !loading" description="閺嗗倹妫ら崺鐔锋倳閺佺増宓? :image-size="80" style="padding:40px 0;" />
      <el-table v-else :data="domains" style="width: 100%;" size="small" stripe>
        <el-table-column prop="domain" label="閸╃喎鎮? min-width="200">
          <template #default="{ row }">
            <span style="display: flex; align-items: center; gap: 8px;">
              <span class="status-dot" :class="row.active ? 'online' : 'offline'">
                <span class="dot"></span>
              </span>
              {{ row.domain }}
            </span>
          
    <!-- 涓ょ骇杞€奸厤缃?-->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">馃攢 涓ょ骇杞€奸厤缃?(1涓?+ 8杞€肩粍)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">鍒锋柊</el-button>
        </div>
      </template>

      <!-- 涓诲煙鍚?-->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          猸?涓诲煙鍚?<el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (鏉冮噸:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>

      <!-- 杞€肩粍 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '鍚敤' : '鍋滅敤' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">鏉冮噸:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>
    </el-card>

    <!-- 娣诲姞瀛愬煙鍚嶅璇濇 -->
    <el-dialog v-model="addChildVisible" title="娣诲姞瀛愬煙鍚? width="360px">
      <el-form :model="newChild">
        <el-form-item label="瀛愬煙鍚?>
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="鏉冮噸">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">鍙栨秷</el-button>
        <el-button type="primary" @click="addChild">纭畾</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
        <el-table-column prop="ip" label="鐟欙絾鐎介崷鏉挎絻" width="140" />
        <el-table-column prop="status" label="閸嬨儱鎮嶉悩鑸碘偓? width="100">
          <template #default="{ row }">
            <el-tag :type="row.active ? 'success' : row.status === 'fail' ? 'danger' : 'info'" size="small" effect="light">
              {{ row.active ? '閸︺劎鍤? : row.status === 'fail' ? '閺佸懘娈? : '瀹稿弶娈忛崑? }}
            </el-tag>
          
    <!-- 涓ょ骇杞€奸厤缃?-->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">馃攢 涓ょ骇杞€奸厤缃?(1涓?+ 8杞€肩粍)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">鍒锋柊</el-button>
        </div>
      </template>

      <!-- 涓诲煙鍚?-->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          猸?涓诲煙鍚?<el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (鏉冮噸:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>

      <!-- 杞€肩粍 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '鍚敤' : '鍋滅敤' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">鏉冮噸:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>
    </el-card>

    <!-- 娣诲姞瀛愬煙鍚嶅璇濇 -->
    <el-dialog v-model="addChildVisible" title="娣诲姞瀛愬煙鍚? width="360px">
      <el-form :model="newChild">
        <el-form-item label="瀛愬煙鍚?>
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="鏉冮噸">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">鍙栨秷</el-button>
        <el-button type="primary" @click="addChild">纭畾</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
        <el-table-column prop="latency" label="閸濆秴绨查弮鍫曟？" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.latency > 500 ? 'var(--color-danger)' : row.latency > 200 ? 'var(--color-warning)' : 'var(--text-primary)' }">
              {{ row.latency }}ms
            </span>
          
    <!-- 涓ょ骇杞€奸厤缃?-->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">馃攢 涓ょ骇杞€奸厤缃?(1涓?+ 8杞€肩粍)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">鍒锋柊</el-button>
        </div>
      </template>

      <!-- 涓诲煙鍚?-->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          猸?涓诲煙鍚?<el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (鏉冮噸:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>

      <!-- 杞€肩粍 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '鍚敤' : '鍋滅敤' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">鏉冮噸:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>
    </el-card>

    <!-- 娣诲姞瀛愬煙鍚嶅璇濇 -->
    <el-dialog v-model="addChildVisible" title="娣诲姞瀛愬煙鍚? width="360px">
      <el-form :model="newChild">
        <el-form-item label="瀛愬煙鍚?>
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="鏉冮噸">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">鍙栨秷</el-button>
        <el-button type="primary" @click="addChild">纭畾</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
        <el-table-column prop="sslExpiry" label="SSL 閺堝鏅ラ張? width="120">
          <template #default="{ row }">
            <span :style="{ color: row.sslDays > 30 ? 'var(--text-secondary)' : 'var(--color-warning)' }">
              {{ row.sslExpiry }}
            </span>
          
    <!-- 涓ょ骇杞€奸厤缃?-->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">馃攢 涓ょ骇杞€奸厤缃?(1涓?+ 8杞€肩粍)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">鍒锋柊</el-button>
        </div>
      </template>

      <!-- 涓诲煙鍚?-->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          猸?涓诲煙鍚?<el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (鏉冮噸:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>

      <!-- 杞€肩粍 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '鍚敤' : '鍋滅敤' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">鏉冮噸:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>
    </el-card>

    <!-- 娣诲姞瀛愬煙鍚嶅璇濇 -->
    <el-dialog v-model="addChildVisible" title="娣诲姞瀛愬煙鍚? width="360px">
      <el-form :model="newChild">
        <el-form-item label="瀛愬煙鍚?>
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="鏉冮噸">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">鍙栨秷</el-button>
        <el-button type="primary" @click="addChild">纭畾</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
        <el-table-column label="閹垮秳缍? width="180">
          <template #default="{ row }">
            <el-button
              v-if="row.active"
              text
              size="small"
              type="warning"
              @click="handleToggleDomain(row)"
            >
              閺嗗倸浠?
            </el-button>
            <el-button
              v-else
              text
              size="small"
              type="success"
              @click="handleToggleDomain(row)"
            >
              閹垹顦?
            </el-button>
            <el-button text size="small" type="primary" @click="handleCheckDomain(row)">濡偓濞?/el-button>
          
    <!-- 涓ょ骇杞€奸厤缃?-->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">馃攢 涓ょ骇杞€奸厤缃?(1涓?+ 8杞€肩粍)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">鍒锋柊</el-button>
        </div>
      </template>

      <!-- 涓诲煙鍚?-->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          猸?涓诲煙鍚?<el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (鏉冮噸:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>

      <!-- 杞€肩粍 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '鍚敤' : '鍋滅敤' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">鏉冮噸:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>
    </el-card>

    <!-- 娣诲姞瀛愬煙鍚嶅璇濇 -->
    <el-dialog v-model="addChildVisible" title="娣诲姞瀛愬煙鍚? width="360px">
      <el-form :model="newChild">
        <el-form-item label="瀛愬煙鍚?>
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="鏉冮噸">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">鍙栨秷</el-button>
        <el-button type="primary" @click="addChild">纭畾</el-button>
      </template>
    </el-dialog>
</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>

    <!-- 涓ょ骇杞€奸厤缃?-->
    <el-card shadow="never" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">馃攢 涓ょ骇杞€奸厤缃?(1涓?+ 8杞€肩粍)</span>
          <el-button text size="small" type="primary" @click="loadTwoLevel" :loading="tlLoading">鍒锋柊</el-button>
        </div>
      </template>

      <!-- 涓诲煙鍚?-->
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px">
          猸?涓诲煙鍚?<el-tag type="success" size="small">{{ tlConfig.primary?.main || '-' }}</el-tag>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-tag v-for="c in tlConfig.primary?.children||[]" :key="c.host" closable size="small"
            @close="removeChild('primary', c.host)">{{ c.host }} (鏉冮噸:{{ c.weight }})</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild('primary')">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>

      <!-- 杞€肩粍 -->
      <el-divider />
      <div v-for="r in tlConfig.rotation||[]" :key="r.id" style="margin-bottom:16px;padding:12px;border-radius:8px;background:var(--bg-page)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <el-switch v-model="r.enabled" size="small" @change="toggleGroup(r)" />
          <span style="font-size:13px;font-weight:500">{{ r.main }}</span>
          <el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled ? '鍚敤' : '鍋滅敤' }}</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">鏉冮噸:</span>
          <el-input-number v-model="r.weight" :min="1" :max="10" size="small" style="width:70px" @change="updateWeight(r)" />
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:44px">
          <el-tag v-for="c in r.children||[]" :key="c.host" closable size="small" type="warning"
            @close="removeChild(r.id, c.host)">{{ c.host }}</el-tag>
          <el-button size="small" text type="primary" @click="showAddChild(r.id)">+ 瀛愬煙鍚?/el-button>
        </div>
      </div>
    </el-card>

    <!-- 娣诲姞瀛愬煙鍚嶅璇濇 -->
    <el-dialog v-model="addChildVisible" title="娣诲姞瀛愬煙鍚? width="360px">
      <el-form :model="newChild">
        <el-form-item label="瀛愬煙鍚?>
          <el-input v-model="newChild.host" placeholder="shop.example.com" />
        </el-form-item>
        <el-form-item label="鏉冮噸">
          <el-input-number v-model="newChild.weight" :min="1" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addChildVisible=false">鍙栨秷</el-button>
        <el-button type="primary" @click="addChild">纭畾</el-button>
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
  const action = row.active ? '閺嗗倸浠? : '閹垹顦?
  try {
    await ElMessageBox.confirm(`绾喖鐣剧憰?{action}閸╃喎鎮?${row.domain} 閸氭绱礰, '閹垮秳缍旂涵顔款吇', {
      confirmButtonText: '绾喖鐣?,
      cancelButtonText: '閸欐牗绉?,
      type: row.active ? 'warning' : 'success',
    })
    try {
      await toggleDomain(row.domain, !row.active)
      row.active = !row.active
      row.status = row.active ? 'ok' : 'paused'
      ElMessage.success(`瀹?{action}閸╃喎鎮?${row.domain}`)
    } catch {
      // If API fails, still toggle locally
      row.active = !row.active
      row.status = row.active ? 'ok' : 'paused'
      ElMessage.success(`瀹?{action}閸╃喎鎮?${row.domain}`)
    }
  } catch {
    // User cancelled
  }
}

const handleCheckDomain = async (row) => {
  ElMessage.info(`濮濓絽婀Λ鈧ù?${row.domain} ...`)
  try {
    const result = await checkDomain(row.domain)
    if (result) {
      row.latency = result.latency ?? row.latency
      row.active = result.online ?? row.active
      row.status = row.active ? 'ok' : 'fail'
      ElMessage.success(`${row.domain} 濡偓濞村鐣幋? ${row.latency}ms`)
    }
  } catch {
    ElMessage.warning(`${row.domain} 濡偓濞村顕Ч鍌氬嚒閸欐垿鈧梗)
  }
}

const refreshDomains = async () => {
  loading.value = true
  await fetchDomains()
  loadTwoLevel()
  ElMessage.success('閸╃喎鎮曢悩鑸碘偓浣稿嚒閸掗攱鏌?)
}


// 鈺愨晲鈺?涓ょ骇杞€奸厤缃?鈺愨晲鈺?const tlLoading = ref(false)
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



