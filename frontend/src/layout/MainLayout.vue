<template>
      <div class="sidebar-overlay" :class="{show:mobileMenuOpen}" @click="mobileMenuOpen=false"></div>
  <div class="app-shell" :class="{ collapsed: sidebarCollapsed, dark: theme.isDark.value }">
    <!-- Electron 绐楀彛鏍囬鏍?-->
    <header v-if="isElectron" class="electron-titlebar">
      <div class="titlebar-drag">
        <span class="titlebar-text">馃幆 Friday AI OS</span>
      </div>
      <div class="titlebar-actions">
        <button class="tb-btn" @click="minimizeWin" title="鏈€灏忓寲">鈹€</button>
        <button class="tb-btn" @click="maximizeWin" title="鏈€澶у寲">鈻?/button>
        <button class="tb-btn tb-close" @click="closeWin" title="鍏抽棴">鉁?/button>
      </div>
    </header>
    <aside class="sidebar" :class="{'mobile-open':mobileMenuOpen}">
      <div class="sidebar-brand" @click="$router.push('/friday')">
        <div class="brand-icon">
          <svg viewBox="0 0 40 40" width="32" height="32">
            <defs>
              <linearGradient id="fridayGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea"/>
                <stop offset="100%" style="stop-color:#13c2c2"/>
              </linearGradient>
            </defs>
            <rect width="40" height="40" rx="10" fill="url(#fridayGrad)"/>
            <circle cx="20" cy="20" r="14" fill="none" stroke="white" stroke-width="1.5" opacity="0.6"/>
            <circle cx="20" cy="20" r="6" fill="white" opacity="0.9"/>
            <line x1="20" y1="6" x2="20" y2="14" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <line x1="20" y1="26" x2="20" y2="34" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <line x1="6" y1="20" x2="14" y2="20" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <line x1="26" y1="20" x2="34" y2="20" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="brand-text" v-show="!sidebarCollapsed">
          <span class="brand-title">Friday AI OS</span>
          <span class="brand-sub">瓒呯骇AI鏁板瓧鐢熷懡浣?/span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">🧠</span> AI 智能</div>
          <router-link to="/friday" class="nav-item" :class="{ active: isActive('/friday') }"><span class="nav-icon">🧠</span><span>Friday 大脑</span></router-link>
          <router-link to="/dashboard" class="nav-item" :class="{ active: isActive('/dashboard') }"><span class="nav-icon">📊</span><span>仪表盘</span></router-link>
          <router-link to="/chat" class="nav-item" :class="{ active: isActive('/chat') }"><span class="nav-icon">💬</span><span>AI 对话</span></router-link>
          <router-link to="/agents" class="nav-item" :class="{ active: isActive('/agents') }"><span class="nav-icon">🤖</span><span>Agent 列表</span></router-link>
          <router-link to="/models" class="nav-item" :class="{ active: isActive('/models') }"><span class="nav-icon">🔬</span><span>模型中心</span></router-link>
          <router-link to="/memory" class="nav-item" :class="{ active: isActive('/memory') }"><span class="nav-icon">💾</span><span>记忆中心</span></router-link>
          <router-link to="/trends" class="nav-item" :class="{ active: isActive('/trends') }"><span class="nav-icon">📈</span><span>趋势监控</span></router-link>
          <router-link to="/evolution" class="nav-item" :class="{ active: isActive('/evolution') }"><span class="nav-icon">🌱</span><span>进化报告</span></router-link>
          <router-link to="/video" class="nav-item" :class="{ active: isActive('/video') }"><span class="nav-icon">🎬</span><span>视频分析</span></router-link>
          <router-link to="/ocr" class="nav-item" :class="{ active: isActive('/ocr') }"><span class="nav-icon">🔍</span><span>OCR 识别</span></router-link>
          <router-link to="/plugins" class="nav-item" :class="{ active: isActive('/plugins') }"><span class="nav-icon">🧩</span><span>技能市场</span></router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">🏬</span> 商城运营</div>
          <router-link to="/mall" class="nav-item" :class="{ active: isActive('/mall') }"><span class="nav-icon">🏬</span><span>商城管理</span></router-link>
          <router-link to="/customer" class="nav-item" :class="{ active: isActive('/customer') }"><span class="nav-icon">💬</span><span>客服系统</span></router-link>
          <router-link to="/site" class="nav-item" :class="{ active: isActive('/site') }"><span class="nav-icon">🌐</span><span>落地页检测</span></router-link>
          <router-link to="/image-process" class="nav-item" :class="{ active: isActive('/image-process') }"><span class="nav-icon">🖼️</span><span>商品图处理</span></router-link>
          <router-link to="/multilang" class="nav-item" :class="{ active: isActive('/multilang') }"><span class="nav-icon">🌍</span><span>多语言发布</span></router-link>
          <router-link to="/batch-upload" class="nav-item" :class="{ active: isActive('/batch-upload') }"><span class="nav-icon">📋</span><span>批量上架</span></router-link>
          <router-link to="/auto-reply" class="nav-item" :class="{ active: isActive('/auto-reply') }"><span class="nav-icon">🤖</span><span>自动回复</span></router-link>
          <router-link to="/order-alert" class="nav-item" :class="{ active: isActive('/order-alert') }"><span class="nav-icon">🔔</span><span>订单预警</span></router-link>
          <router-link to="/virtual" class="nav-item" :class="{ active: isActive('/virtual') }"><span class="nav-icon">🎮</span><span>虚拟数据</span></router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">🖥️</span> 运维监控</div>
          <router-link to="/server" class="nav-item" :class="{ active: isActive('/server') }"><span class="nav-icon">🖥️</span><span>服务器</span></router-link>
          <router-link to="/docker" class="nav-item" :class="{ active: isActive('/docker') }"><span class="nav-icon">🐳</span><span>Docker</span></router-link>
          <router-link to="/nginx" class="nav-item" :class="{ active: isActive('/nginx') }"><span class="nav-icon">🔧</span><span>Nginx</span></router-link>
          <router-link to="/network" class="nav-item" :class="{ active: isActive('/network') }"><span class="nav-icon">🌐</span><span>网络工具</span></router-link>
          <router-link to="/github" class="nav-item" :class="{ active: isActive('/github') }"><span class="nav-icon">🐙</span><span>GitHub MCP</span></router-link>
          <router-link to="/rotation" class="nav-item" :class="{ active: isActive('/rotation') }"><span class="nav-icon">🔄</span><span>域名轮值</span></router-link>
          <router-link to="/rollback" class="nav-item" :class="{ active: isActive('/rollback') }"><span class="nav-icon">⏪</span><span>备份回滚</span></router-link>
          <router-link to="/files" class="nav-item" :class="{ active: isActive('/files') }"><span class="nav-icon">📁</span><span>文件管理</span></router-link>
          <router-link to="/database" class="nav-item" :class="{ active: isActive('/database') }"><span class="nav-icon">🗄️</span><span>数据库</span></router-link>
          <router-link to="/log-viewer" class="nav-item" :class="{ active: isActive('/log-viewer') }"><span class="nav-icon">📋</span><span>日志中心</span></router-link>
          <router-link to="/scraper" class="nav-item" :class="{ active: isActive('/scraper') }"><span class="nav-icon">🕷️</span><span>采集中心</span></router-link>
          <router-link to="/audit" class="nav-item" :class="{ active: isActive('/audit') }"><span class="nav-icon">📋</span><span>审计日志</span></router-link>
          <router-link to="/self-service" class="nav-item" :class="{ active: isActive('/self-service') }"><span class="nav-icon">🔧</span><span>自助服务</span></router-link>
          <router-link to="/weekly-report" class="nav-item" :class="{ active: isActive('/weekly-report') }"><span class="nav-icon">📊</span><span>运营周报</span></router-link>
          <router-link to="/tasks" class="nav-item" :class="{ active: isActive('/tasks') }"><span class="nav-icon">📋</span><span>任务中心</span></router-link>
        </div>
        <div class="nav-section">
          <div class="nav-section-label" v-show="!sidebarCollapsed"><span class="sec-icon">🛡️</span> 安全告警</div>
          <router-link to="/security" class="nav-item" :class="{ active: isActive('/security') }"><span class="nav-icon">🔒</span><span>安全中心</span></router-link>
          <router-link to="/alert" class="nav-item" :class="{ active: isActive('/alert') }"><span class="nav-icon">🔔</span><span>告警中心</span></router-link>
          <router-link to="/approval" class="nav-item" :class="{ active: isActive('/approval') }"><span class="nav-icon">✅</span><span>审批中心</span></router-link>
          <router-link to="/self-healing" class="nav-item" :class="{ active: isActive('/self-healing') }"><span class="nav-icon">🩺</span><span>异常自愈</span></router-link>
          <router-link to="/emergency" class="nav-item" :class="{ active: isActive('/emergency') }"><span class="nav-icon">🚨</span><span>急救面板</span></router-link>
          <router-link to="/phone" class="nav-item" :class="{ active: isActive('/phone') }"><span class="nav-icon">📞</span><span>AI电话助理</span></router-link>
        </div>