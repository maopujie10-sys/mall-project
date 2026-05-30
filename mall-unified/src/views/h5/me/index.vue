<template>
  <div class="me-page">
    <!-- 头部信息 -->
    <div class="profile-header">
      <div class="profile-bg"></div>
      <div class="profile-content">
        <template v-if="userStore.userInfo">
          <div class="avatar-wrap">
            <img :src="avatarSrc" class="avatar-img" />
          </div>
          <div class="user-detail">
            <span class="username">{{ userStore.userInfo.username }}</span>
            <span class="usercode" @click="copyId(userStore.userInfo.usercode)">
              ID: {{ userStore.userInfo.usercode }}
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" stroke-width="2"/>
              </svg>
            </span>
          </div>
        </template>
        <template v-else>
          <div class="avatar-wrap">
            <div class="avatar-placeholder">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="4" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
                <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="rgba(255,255,255,0.6)" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
          </div>
          <div class="login-row">
            <span @click="openWin('/m/login', false)">{{ $t('common.login') }}</span>
            <span class="sep">/</span>
            <span @click="openWin('/m/register', false)">{{ $t('common.register') }}</span>
          </div>
        </template>

        <div class="collect-row">
          <div class="collect-item" @click="openWin('/m/me', true)">
            <span class="collect-num">{{ goodNumber }}</span>
            <span class="collect-label">{{ $t('user.favorites') }}</span>
          </div>
          <div class="collect-item" @click="openWin('/m/me', true)">
            <span class="collect-num">{{ shopNumber }}</span>
            <span class="collect-label">{{ $t('user.followed') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 余额 -->
    <div class="card-section" v-if="isShelves">
      <div class="balance-header">
        <span class="balance-label">{{ $t('user.balance') }} <small>(USD)</small></span>
        <span class="balance-toggle" @click="banClose = !banClose">
          <svg v-if="banClose" width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M3 3l18 18M12 5a7 7 0 0 1 7 7M5 12a7 7 0 0 1 7-7" stroke="var(--text-muted)" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z" stroke="var(--text-muted)" stroke-width="2"/>
            <circle cx="12" cy="12" r="3" stroke="var(--text-muted)" stroke-width="2"/>
          </svg>
        </span>
      </div>
      <div class="balance-amount" :class="{ masked: banClose }">
        {{ banClose ? '******' : '$' + (userMoney && formatMoney(userMoney.money)) }}
      </div>
      <div class="balance-actions">
        <button class="act-btn" @click="openWin('/m/me', true)">{{ $t('user.withdraw') }}</button>
        <button class="act-btn primary" @click="openWin('/m/invest', true)">{{ $t('user.recharge') }}</button>
      </div>
    </div>

    <!-- 订单 -->
    <div class="card-section">
      <div class="section-title-row">
        <span class="section-title">{{ $t('orders') }}</span>
        <span class="section-link" @click="openOrder(false)">{{ $t('common.total') }} &rsaquo;</span>
      </div>
      <div class="order-icons">
        <div v-for="(item, index) in orderNav" :key="index" class="order-icon-item" @click="openOrder(item.type)">
          <div class="order-icon-wrap">
            <span v-if="+item.count > 0" class="order-badge">{{ item.count > 9 ? '9+' : item.count }}</span>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path :d="item.iconPath" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="order-label">{{ item.title }}</span>
        </div>
      </div>
    </div>

    <!-- 商家入驻 -->
    <div class="card-section clickable" @click="merchantJump">
      <div class="menu-row">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <rect x="3" y="3" width="18" height="18" rx="2" stroke="var(--color-primary)" stroke-width="2"/>
          <path d="M8 12h8M12 8v8" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span class="menu-label">{{ userStore.userInfo?.roletype == 1 ? $t('user.merchantLogin') : $t('user.merchantSettle') }}</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" class="ml-auto">
          <path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
    </div>

    <!-- 贷款 -->
    <div class="card-section clickable" @click="$router.push('/m/loan')" v-if="isShelves">
      <div class="menu-row">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="var(--color-accent)" stroke-width="2"/>
          <circle cx="12" cy="7" r="1.5" fill="var(--color-accent)"/>
          <path d="M12 10.5v7" stroke="var(--color-accent)" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span class="menu-label">{{ $t('user.loanApply') }}</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" class="ml-auto">
          <path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
    </div>

    <!-- 功能菜单 -->
    <div class="card-section">
      <div v-for="(item, index) in navData" :key="index" class="nav-item" @click="openWin(item.path, item.needLogin)">
        <div class="nav-item-left">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path :d="item.iconPath" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ item.name }}</span>
        </div>
        <div class="nav-item-right">
          <span v-if="item.tips" class="nav-tip">{{ item.tips }}</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M9 6l6 6-6 6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 退出登录 -->
    <div class="card-section" v-if="userStore.isLoggedIn">
      <div class="nav-item logout-btn" @click="handleLogout">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" stroke="var(--color-danger)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span style="color:var(--color-danger)">{{ $t('common.logout') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showNotify } from 'vant'
import { useUserStore } from '@/stores/user'
import { keepGoodsCount, focusSellerCount, apicCuntOrderStatus } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

// ===== State (preserved from original) =====
const goodNumber = ref(0)
const shopNumber = ref(0)
const isShelves = ref(true)
const banClose = ref(localStorage.getItem('banClose') === 'true')

const userMoney = computed(() => userStore.userMoney || null)

const avatarSrc = computed(() => {
  const avatar = userStore.userInfo?.avatar || 1
  return `/assets/avatar/${avatar}.png`
})

const orderNav = ref([
  { count: '0', title: '待付款', type: '0', name: 'waitPayCount', iconPath: 'M3 6h18v14H3zM3 6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2' },
  { count: '0', title: '待发货', type: '1', name: 'waitDeliverCount', iconPath: 'M12 2l10 6-10 6L2 8l10-6zM2 8v10l10 6 10-6V8' },
  { count: '0', title: '待收货', type: '3', name: 'waitReceiptCount', iconPath: 'M3 6h18M3 12h18M3 18h18M13 3v18' },
  { count: '0', title: '待评价', type: '4', name: 'waitEvaluateCount', iconPath: 'M11 4h2v2h-2zM11 10h2v6h-2zM12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z' },
  { count: '0', title: '退款/售后', type: '6', name: 'refundCount', iconPath: 'M19 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zM9 9h6M9 13h6' }
])

const navData = ref([
  { iconPath: 'M3 5h12M9 3v2m1 9.5A18 18 0 0 1 12 13a18 18 0 0 1 5.7 2.5', name: '语言', tips: '简体中文', path: '/m/settings', needLogin: false },
  { iconPath: 'M10.3 4.3a1.7 1.7 0 0 1 3.4 0 1.7 1.7 0 0 0 2.6 1.1 1.7 1.7 0 0 1 2.3 2.4 1.7 1.7 0 0 0 1.1 2.6 1.7 1.7 0 0 1 0 3.3 1.7 1.7 0 0 0-1.1 2.6 1.7 1.7 0 0 1-2.4 2.3 1.7 1.7 0 0 0-2.6 1 1.7 1.7 0 0 1-3.3 0 1.7 1.7 0 0 0-2.6-1.1 1.7 1.7 0 0 1-2.3-2.4 1.7 1.7 0 0 0-1.1-2.6 1.7 1.7 0 0 1 0-3.3 1.7 1.7 0 0 0 1.1-2.6 1.7 1.7 0 0 1 2.4-2.3', name: '设置', needLogin: true, path: '/m/settings' }
])

// ===== Utility =====
function _toFixed(num, decimal) {
  num = num.toString()
  const i = num.indexOf('.')
  if (i !== -1) num = num.substring(0, decimal + i + 1)
  else num = num.substring(0)
  return parseFloat(num).toFixed(decimal)
}

function formatMoney(num) {
  if (num && Number(num)) {
    const s = _toFixed(num, 2)
    const pre = s.slice(0, s.indexOf('.'))
    const ri = s.slice(s.indexOf('.') + 1)
    return `${pre.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')}.${ri.length < 2 ? ri + '0' : ri}`
  }
  return '0.00'
}

function isLoginFn() {
  return !!(userStore.token || localStorage.getItem('token'))
}

// ===== Lifecycle (preserved from original) =====
onMounted(async () => {
  userStore.fetchUserInfo()
  getCounts()
  if (isLoginFn()) {
    apicCuntOrderStatus().then((res) => {
      orderNav.value.forEach((item) => {
        item.count = res?.[item.name] || '0'
      })
    }).catch(() => {})
  }
})

// ===== Methods (preserved from original) =====
async function getCounts() {
  try {
    const [gRes, sRes] = await Promise.allSettled([keepGoodsCount(), focusSellerCount()])
    if (gRes.status === 'fulfilled') goodNumber.value = gRes.value?.count || gRes.value || 0
    if (sRes.status === 'fulfilled') shopNumber.value = sRes.value?.count || sRes.value || 0
  } catch (e) {}
}

function copyId(usercode) {
  if (!usercode) return
  navigator.clipboard?.writeText(usercode).then(() => {
    showToast('ID 已复制')
  }).catch(() => {})
}

function openWin(path, needLogin) {
  if (needLogin && !isLoginFn()) {
    showNotify({ type: 'warning', message: '请先登录' })
    router.push('/m/login')
    return
  }
  router.push(path)
}

function openOrder(type) {
  if (!isLoginFn()) {
    showNotify({ type: 'warning', message: '请先登录' })
    router.push('/m/login')
    return
  }
  const query = type !== undefined && type !== false ? { type } : {}
  router.push({ path: '/m/order', query })
}

function merchantJump() {
  if (userStore.userInfo?.roletype == 1) {
    router.push('/seller/')
  } else {
    router.push('/m/invest')
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/m')
}
</script>

<style scoped>
.me-page { padding-bottom: 24px; min-height: 100vh; background: var(--bg-secondary); }

/* 头部 */
.profile-header { position: relative; overflow: hidden; }
.profile-bg {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, var(--color-primary), #818cf8);
  border-radius: 0 0 32px 32px;
  height: 220px;
}
.profile-content { position: relative; padding: 44px 20px 28px; color: #fff; }

.avatar-wrap {
  width: 60px; height: 60px; border-radius: 50%; overflow: hidden;
  border: 3px solid rgba(255,255,255,0.4); box-shadow: var(--shadow-md);
  margin-bottom: 12px; cursor: pointer;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-placeholder {
  width: 100%; height: 100%; background: rgba(255,255,255,0.15);
  display: flex; align-items: center; justify-content: center;
}

.user-detail { display: flex; flex-direction: column; gap: 4px; margin-bottom: 24px; }
.username { font-size: 18px; font-weight: 600; }
.usercode { font-size: 12px; opacity: 0.8; display: flex; align-items: center; gap: 4px; cursor: pointer; }

.login-row { font-size: 16px; font-weight: 500; margin-bottom: 24px; }
.login-row span { cursor: pointer; }
.sep { margin: 0 4px; opacity: 0.6; }

.collect-row { display: flex; gap: 40px; }
.collect-item { display: flex; flex-direction: column; gap: 4px; cursor: pointer; }
.collect-num { font-size: 20px; font-weight: 700; }
.collect-label { font-size: 12px; opacity: 0.8; }

/* 卡片 */
.card-section {
  background: var(--bg-primary); border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm); margin: 10px 14px; padding: 16px;
}
.card-section.clickable { cursor: pointer; transition: box-shadow var(--transition-fast); }
.card-section.clickable:hover { box-shadow: var(--shadow-md); }

.section-title-row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 14px; font-weight: 500; margin-bottom: 18px;
}
.section-link { font-size: 12px; color: var(--color-primary); cursor: pointer; }

/* 余额 */
.balance-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.balance-label { font-size: 13px; color: var(--text-secondary); }
.balance-label small { color: var(--text-muted); }
.balance-toggle { cursor: pointer; }
.balance-amount { font-size: 26px; font-weight: 700; margin-bottom: 16px; }
.balance-amount.masked { letter-spacing: 8px; }
.balance-actions { display: flex; gap: 10px; }
.act-btn {
  flex: 1; height: 36px; border-radius: 18px;
  border: 1.5px solid var(--border-color); background: transparent;
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: all var(--transition-fast);
}
.act-btn.primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff; border: none;
}

/* 订单 */
.order-icons { display: flex; justify-content: space-around; }
.order-icon-item { display: flex; flex-direction: column; align-items: center; gap: 8px; cursor: pointer; }
.order-icon-wrap { position: relative; }
.order-badge {
  position: absolute; top: -6px; right: -12px; min-width: 16px; height: 16px;
  line-height: 16px; text-align: center; background: #ef4444; color: #fff;
  border-radius: 8px; font-size: 10px; padding: 0 5px;
}
.order-label { font-size: 11px; color: var(--text-secondary); }

/* 菜单行 */
.menu-row { display: flex; align-items: center; gap: 12px; }
.menu-label { font-size: 14px; color: var(--text-primary); font-weight: 500; }
.ml-auto { margin-left: auto; }

/* 导航项 */
.nav-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 0; cursor: pointer;
}
.nav-item:not(:last-child) { border-bottom: 1px solid var(--border-color); }
.nav-item-left { display: flex; align-items: center; gap: 12px; font-size: 14px; }
.nav-item-right { display: flex; align-items: center; gap: 8px; }
.nav-tip { font-size: 12px; color: var(--text-muted); }

.logout-btn { border-bottom: none !important; }
</style>
