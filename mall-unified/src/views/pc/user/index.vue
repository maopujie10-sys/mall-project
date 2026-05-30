<template>
  <div class="pc-user fade-in">
    <!-- Layout: Sidebar + Main -->
    <div class="user-layout">
      <!-- Sidebar -->
      <aside class="user-sidebar">
        <!-- Profile Card -->
        <div class="profile-card card">
          <div class="avatar-box" @click="showAvatarDialog = true">
            <img :src="avatarUrl" class="avatar-img" />
            <div class="avatar-overlay">Change</div>
          </div>
          <h3 class="user-name">{{ userStore.userInfo?.username || 'User' }}</h3>
          <p class="user-id">
            ID: {{ userStore.userInfo?.usercode || '—' }}
            <i class="copy-icon" @click="copyId">&#128203;</i>
          </p>
        </div>

        <!-- Navigation -->
        <nav class="side-nav">
          <router-link to="/pc/user" class="nav-item" :class="{ active: currentTab === 'dashboard' }" @click="currentTab = 'dashboard'">
            Dashboard
          </router-link>
          <router-link to="/pc/order" class="nav-item" :class="{ active: currentTab === 'orders' }" @click="currentTab = 'orders'">
            My Orders
          </router-link>
          <a class="nav-item" :class="{ active: currentTab === 'collectGoods' }" @click="currentTab = 'collectGoods'">
            My Favorites
          </a>
          <a class="nav-item" :class="{ active: currentTab === 'collectShops' }" @click="currentTab = 'collectShops'">
            Followed Stores
          </a>
          <a class="nav-item" :class="{ active: currentTab === 'wallet' }" @click="currentTab = 'wallet'">
            My Wallet
          </a>
          <a class="nav-item" :class="{ active: currentTab === 'settings' }" @click="currentTab = 'settings'">
            Settings
          </a>
        </nav>

        <button class="logout-btn" @click="handleLogout">Logout</button>
      </aside>

      <!-- Main Content -->
      <div class="user-main">
        <!-- Dashboard -->
        <div v-if="currentTab === 'dashboard'" class="dashboard">
          <h2 class="page-title">Dashboard</h2>
          <div class="stats-grid">
            <div class="stat-card card">
              <div class="stat-icon">&#128722;</div>
              <div class="stat-info">
                <span class="stat-label">Total Orders</span>
                <strong class="stat-value">{{ stats.totalOrders || 0 }}</strong>
              </div>
            </div>
            <div class="stat-card card">
              <div class="stat-icon">&#10084;</div>
              <div class="stat-info">
                <span class="stat-label">Favorites</span>
                <strong class="stat-value">{{ stats.totalFavorites || 0 }}</strong>
              </div>
            </div>
            <div class="stat-card card">
              <div class="stat-icon">&#128179;</div>
              <div class="stat-info">
                <span class="stat-label">Balance</span>
                <strong class="stat-value">${{ formatPrice(stats.balance || 0) }}</strong>
              </div>
            </div>
            <div class="stat-card card">
              <div class="stat-icon">&#9733;</div>
              <div class="stat-info">
                <span class="stat-label">Points</span>
                <strong class="stat-value">{{ stats.points || 0 }}</strong>
              </div>
            </div>
          </div>

          <!-- Recent Orders -->
          <div class="card" style="margin-top:20px">
            <h3 style="margin-bottom:16px">Recent Orders</h3>
            <div v-if="recentOrders.length" class="recent-orders">
              <div v-for="order in recentOrders" :key="order.id" class="order-row">
                <img :src="order.imgUrl || order.mainImage" class="order-img" />
                <div class="order-info">
                  <p class="order-name">{{ order.name || order.goodsName }}</p>
                  <span :class="['order-status', statusClass(order.status)]">{{ orderStatusText(order.status) }}</span>
                </div>
                <span class="order-price">${{ formatPrice(order.price || order.totalAmount || 0) }}</span>
              </div>
              <router-link to="/pc/order" class="see-all-link">View All Orders &rarr;</router-link>
            </div>
            <el-empty v-else description="No orders yet" :image-size="80" />
          </div>
        </div>

        <!-- Favorites (Collect Goods) -->
        <div v-if="currentTab === 'collectGoods'">
          <h2 class="page-title">My Favorites</h2>
          <div v-loading="collectLoading" class="product-grid">
            <ProductCard v-for="item in collectGoods" :key="item.id" :item="item" />
          </div>
          <el-empty v-if="!collectGoods.length && !collectLoading" description="No favorites yet" />
        </div>

        <!-- Followed Stores (Collect Shops) -->
        <div v-if="currentTab === 'collectShops'">
          <h2 class="page-title">Followed Stores</h2>
          <div v-loading="shopLoading" class="store-grid">
            <div v-for="item in collectShops" :key="item.id" class="shop-card card card-hover" @click="$router.push({ path: '/pc/store/' + item.id, query: { storeId: item.id } })">
              <img :src="item.avatar" class="shop-logo" />
              <h4>{{ item.name }}</h4>
              <p>{{ item.sellerGoodsNum || 0 }} products</p>
              <button class="btn btn-outline btn-sm">Visit Store</button>
            </div>
          </div>
          <el-empty v-if="!collectShops.length && !shopLoading" description="No followed stores" />
        </div>

        <!-- Wallet -->
        <div v-if="currentTab === 'wallet'">
          <h2 class="page-title">My Wallet</h2>
          <div class="card wallet-card">
            <div class="balance-display">
              <span class="balance-label">Available Balance</span>
              <span class="balance-amount">${{ formatPrice(stats.balance || 0) }}</span>
            </div>
            <div class="wallet-actions">
              <router-link to="/pc/credit" class="btn btn-primary">Recharge / Withdraw</router-link>
            </div>
          </div>
        </div>

        <!-- Settings -->
        <div v-if="currentTab === 'settings'">
          <h2 class="page-title">Settings</h2>
          <div class="card">
            <div class="setting-row">
              <span>Shipping Address</span>
              <button class="btn btn-outline btn-sm">Manage</button>
            </div>
            <div class="setting-row">
              <span>Login Password</span>
              <button class="btn btn-outline btn-sm">Change</button>
            </div>
            <div class="setting-row">
              <span>Transaction Password</span>
              <button class="btn btn-outline btn-sm">Set / Change</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Avatar Change Dialog -->
    <el-dialog v-model="showAvatarDialog" title="Choose Avatar" width="420px">
      <div class="avatar-grid">
        <div v-for="i in 20" :key="i" :class="['avatar-option', { selected: selectedAvatar === i }]" @click="selectedAvatar = i">
          <img :src="'/avatars/' + i + '.png'" alt="" />
          <i v-if="selectedAvatar === i" class="check-mark">&#10003;</i>
        </div>
      </div>
      <template #footer>
        <el-button @click="showAvatarDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveAvatar">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { post } from '@/api/index'

const router = useRouter()
const userStore = useUserStore()
const currentTab = ref('dashboard')

// Profile
const avatarUrl = ref('')
const showAvatarDialog = ref(false)
const selectedAvatar = ref(1)

// Stats
const stats = reactive({ totalOrders: 0, totalFavorites: 0, balance: 0, points: 0 })
const recentOrders = ref([])

// Collect
const collectGoods = ref([])
const collectLoading = ref(false)
const collectShops = ref([])
const shopLoading = ref(false)

// ===== Methods =====
function formatPrice(n) {
  const val = Number(n)
  if (!val) return '0.00'
  return val.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

function formatNum(n) {
  if (!n) return '0'
  return Number(n).toLocaleString()
}

function copyId() {
  if (userStore.userInfo?.usercode) {
    navigator.clipboard?.writeText(userStore.userInfo.usercode)
    ElMessage.success('Copied')
  }
}

function orderStatusText(status) {
  const map = { '-1': 'Cancelled', '0': 'Pending', '1': 'Shipped', '2': 'Confirmed', '3': 'Received', '4': 'Rated' }
  return map[String(status)] || 'Unknown'
}

function statusClass(status) {
  const map = { '-1': 'cancelled', '0': 'pending', '1': 'shipped', '2': 'confirmed', '3': 'received', '4': 'rated' }
  return map[String(status)] || ''
}

async function fetchDashboard() {
  try {
    const res = await post('/api/user!info.action')
    if (res.data || res) {
      const u = res.data || res
      avatarUrl.value = '/avatars/' + (u.avatar || '1') + '.png'
      selectedAvatar.value = Number(u.avatar || 1)
    }
    // Fetch balance
    try {
      const balRes = await post('/api/wallet!getUsdt.action')
      stats.balance = balRes.data?.money || balRes.data?.balance || 0
    } catch {}
    // Fetch recent orders
    try {
      const orderRes = await post('/api/order!list.action', { pageNum: 1, pageSize: 5 })
      recentOrders.value = (orderRes.data?.pageList || []).slice(0, 5)
    } catch {}
  } catch {}
}

async function fetchCollectGoods() {
  try {
    collectLoading.value = true
    const res = await post('/api/keepGoods!list.action', { pageNum: 1, pageSize: 20 })
    collectGoods.value = res.data?.pageList || res.data?.result || []
  } catch {}
  finally { collectLoading.value = false }
}

async function fetchCollectShops() {
  try {
    shopLoading.value = true
    const res = await post('/api/focusSeller!list.action', { pageNum: 1, pageSize: 20 })
    collectShops.value = res.data?.pageList || res.data?.result || []
  } catch {}
  finally { shopLoading.value = false }
}

async function saveAvatar() {
  try {
    await post('/api/user!changeAvatar.action', { idx: selectedAvatar.value })
    avatarUrl.value = '/avatars/' + selectedAvatar.value + '.png'
    ElMessage.success('Avatar updated')
    showAvatarDialog.value = false
    await userStore.fetchUserInfo()
  } catch { ElMessage.error('Failed to update') }
}

async function handleLogout() {
  await ElMessageBox.confirm('Are you sure you want to logout?', 'Confirm', { type: 'warning' })
  userStore.logout()
  router.push('/pc')
}

// ===== Lifecycle =====
onMounted(() => {
  fetchDashboard()
  // Pre-fetch on mount
  fetchCollectGoods()
  fetchCollectShops()
})
</script>

<style scoped>
.pc-user { padding: 24px 0; }
.user-layout { display: grid; grid-template-columns: 250px 1fr; gap: 24px; align-items: flex-start; }

/* Sidebar */
.user-sidebar { position: sticky; top: 80px; }
.profile-card { text-align: center; padding: 28px 20px; margin-bottom: 16px; }
.avatar-box { width: 72px; height: 72px; border-radius: 50%; overflow: hidden; margin: 0 auto 12px; position: relative; cursor: pointer; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); color: white; font-size: 11px; display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity var(--transition-fast); }
.avatar-box:hover .avatar-overlay { opacity: 1; }
.user-name { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.user-id { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; justify-content: center; gap: 4px; }
.copy-icon { cursor: pointer; font-size: 14px; }

.side-nav { display: flex; flex-direction: column; gap: 2px; }
.nav-item { display: block; padding: 12px 16px; border-radius: var(--border-radius-sm); font-size: 14px; color: var(--text-secondary); transition: all var(--transition-fast); cursor: pointer; text-decoration: none; }
.nav-item:hover { background: var(--bg-tertiary); color: var(--color-primary); }
.nav-item.active { background: rgba(99,102,241,0.08); color: var(--color-primary); font-weight: 600; }

.logout-btn { width: 100%; margin-top: 20px; padding: 10px; border-radius: var(--border-radius-sm); background: none; color: var(--color-danger); font-size: 14px; border: 1px solid var(--color-danger); cursor: pointer; }
.logout-btn:hover { background: rgba(239,68,68,0.08); }

/* Main */
.user-main { min-height: 400px; }
.page-title { font-size: 24px; font-weight: 700; margin-bottom: 20px; color: var(--text-primary); }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.stat-card { display: flex; align-items: center; gap: 14px; padding: 20px; }
.stat-icon { font-size: 28px; width: 48px; height: 48px; background: rgba(99,102,241,0.08); border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-label { font-size: 12px; color: var(--text-muted); display: block; }
.stat-value { font-size: 20px; font-weight: 700; color: var(--text-primary); }

/* Orders */
.recent-orders { }
.order-row { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border-color); }
.order-row:last-child { border-bottom: none; }
.order-img { width: 48px; height: 48px; border-radius: 6px; object-fit: cover; }
.order-info { flex: 1; }
.order-name { font-size: 14px; margin-bottom: 4px; }
.order-status { font-size: 11px; padding: 1px 8px; border-radius: 10px; }
.order-status.pending { background: rgba(245,158,11,0.1); color: var(--color-warning); }
.order-status.shipped { background: rgba(59,130,246,0.1); color: var(--color-info); }
.order-status.received, .order-status.rated { background: rgba(16,185,129,0.1); color: var(--color-success); }
.order-status.cancelled { background: rgba(239,68,68,0.1); color: var(--color-danger); }
.order-price { font-weight: 600; }
.see-all-link { display: block; text-align: center; font-size: 14px; color: var(--color-primary); padding: 12px 0; }

/* Product Grid */
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }
.product-grid :deep(.product-card) { border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); overflow: hidden; padding: 0; cursor: pointer; position: relative; transition: all var(--transition-fast); background: var(--bg-primary); }
.product-grid :deep(.product-card:hover) { border-color: var(--color-primary); box-shadow: var(--shadow-lg); transform: translateY(-2px); }
.product-grid :deep(.prod-img) { width: 100%; aspect-ratio: 1; overflow: hidden; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); }
.product-grid :deep(.prod-img img) { width: 100%; height: 100%; object-fit: contain; transition: transform 0.3s; }
.product-grid :deep(.product-card:hover .prod-img img) { transform: scale(1.05); }
.product-grid :deep(.prod-tag) { position: absolute; top: 6px; left: 6px; background: var(--color-danger); color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.product-grid :deep(.prod-info) { padding: 10px; }
.product-grid :deep(.prod-price) { font-size: 16px; font-weight: 600; color: var(--color-danger); margin-bottom: 4px; }
.product-grid :deep(.prod-sold) { font-size: 10px; color: var(--text-muted); margin-bottom: 6px; }
.product-grid :deep(.prod-name) { font-size: 13px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height: 1.4; margin-bottom: 8px; min-height: 36px; }
.product-grid :deep(.prod-actions) { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 8px; }
.product-grid :deep(.buy-btn) { font-size: 12px; font-weight: 600; color: var(--color-primary); cursor: pointer; }
.product-grid :deep(.star-icon) { font-size: 18px; cursor: pointer; color: var(--text-muted); }
.product-grid :deep(.star-icon.filled) { color: var(--color-accent); }

/* Store Grid */
.store-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; }
.shop-card { display: flex; flex-direction: column; align-items: center; padding: 24px; text-align: center; cursor: pointer; }
.shop-logo { width: 64px; height: 64px; border-radius: 16px; object-fit: cover; margin-bottom: 10px; }
.shop-card h4 { font-size: 14px; margin-bottom: 4px; }
.shop-card p { font-size: 12px; color: var(--text-muted); margin-bottom: 10px; }

/* Wallet */
.wallet-card { padding: 32px; text-align: center; }
.balance-display { margin-bottom: 24px; }
.balance-label { font-size: 14px; color: var(--text-muted); display: block; margin-bottom: 8px; }
.balance-amount { font-size: 36px; font-weight: 700; color: var(--color-primary); }

/* Settings */
.setting-row { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid var(--border-color); font-size: 14px; }
.setting-row:last-child { border-bottom: none; }

/* Avatar Dialog */
.avatar-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; padding: 10px 0; }
.avatar-option { width: 60px; height: 60px; border-radius: 50%; overflow: hidden; position: relative; cursor: pointer; border: 2px solid transparent; }
.avatar-option.selected { border-color: var(--color-primary); }
.avatar-option img { width: 100%; height: 100%; object-fit: cover; }
.check-mark { position: absolute; bottom: 0; right: 0; background: var(--color-primary); color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; }

@media (max-width: 768px) {
  .user-layout { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
