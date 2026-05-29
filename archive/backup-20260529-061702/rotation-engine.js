/**
 * 企业级两级域名轮值引擎 v4.0
 * 落地页显示按钮 → 点击按钮 → 轮值选域名 → 跳转到指定路由
 */
(function(){'use strict';
var CONFIG_URL = '/domain-config.json';
var STORAGE_KEY = 'lr_v40';
var DEAD_TTL = 600000;
var PROBE_TIMEOUT = 3000;
var MAX_RETRIES = 3;

var state = { deadDomains: {}, groupIndex: 0, usedPrefixes: {} };
var config = null;

function loadState() {
  try {
    var raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      var parsed = JSON.parse(raw);
      state.groupIndex = parsed.groupIndex || 0;
      state.usedPrefixes = parsed.usedPrefixes || {};
      var now = Date.now();
      for (var k in (parsed.deadDomains || {})) {
        if (now - parsed.deadDomains[k].time < DEAD_TTL) state.deadDomains[k] = parsed.deadDomains[k];
      }
    }
  } catch(e) {}
}
function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      groupIndex: state.groupIndex,
      usedPrefixes: state.usedPrefixes,
      deadDomains: state.deadDomains
    }));
  } catch(e) {}
}

function isAlive(host) {
  var dead = state.deadDomains[host];
  if (!dead) return true;
  if (Date.now() - dead.time > DEAD_TTL) { delete state.deadDomains[host]; saveState(); return true; }
  return false;
}
function markDead(host, reason) {
  state.deadDomains[host] = { time: Date.now(), reason: reason || 'unknown' };
  saveState();
}

function probe(host, timeout) {
  return new Promise(function(resolve) {
    var img = new Image();
    var timer = setTimeout(function() { img.src = ''; resolve(false); }, timeout);
    img.onload = function() { clearTimeout(timer); resolve(true); };
    img.onerror = function() { clearTimeout(timer); resolve(false); };
    img.src = 'https://' + host + '/favicon.ico?_r=' + Date.now();
  });
}

// 随机选前缀，避免重复（跳过最近3个）
function pickPrefix(pool, groupId) {
  if (!state.usedPrefixes[groupId]) state.usedPrefixes[groupId] = [];
  var used = state.usedPrefixes[groupId];
  var recent = used.slice(-3);
  var available = pool.filter(function(p) { return recent.indexOf(p) === -1; });
  if (!available.length) { used.length = 0; available = pool.slice(); }
  var idx = Math.floor(Math.random() * available.length);
  var picked = available[idx];
  used.push(picked);
  if (used.length > 20) state.usedPrefixes[groupId] = used.slice(-20);
  saveState();
  return picked;
}

function pickTarget() {
  var groups = config.groups.filter(function(g) { return g.enabled !== false; });
  if (!groups.length) return null;
  var tried = 0;
  while (tried < groups.length) {
    var groupIdx = state.groupIndex % groups.length;
    var group = groups[groupIdx];
    if (!isAlive(group.main)) {
      markDead(group.main, 'group_down');
      state.groupIndex = (groupIdx + 1) % groups.length;
      tried++;
      saveState();
      continue;
    }
    var prefix = pickPrefix(group.pool || ['www'], group.id);
    var host = prefix + '.' + group.main;
    return { group: group, host: host, prefix: prefix };
  }
  return null;
}

function updateStep(name, status) {
  var el = document.querySelector('[data-step=' + name + ']');
  if (el) el.className = 'step ' + status;
}

// === 点击按钮：开始轮值 + 跳转到指定路由 ===
window.doJump = async function(targetPath) {
  targetPath = targetPath || '/home';
  var spinner = document.getElementById('spinner');
  var titleEl = document.getElementById('title');
  var allBtns = document.querySelectorAll('.jump-btn');
  
  // 显示加载状态
  if (spinner) spinner.style.display = 'block';
  if (titleEl) titleEl.textContent = '正在连接最优线路...';
  allBtns.forEach(function(b) { b.disabled = true; b.style.opacity = '0.6'; });
  
  if (!config) {
    try {
      updateStep('config', 'active');
      var resp = await fetch(CONFIG_URL, { cache: 'no-store' });
      config = await resp.json();
      updateStep('config', 'done');
    } catch(e) {
      updateStep('config', 'fail');
      showError('配置加载失败');
      return;
    }
  }
  
  for (var retry = 0; retry < MAX_RETRIES; retry++) {
    updateStep('group', 'active'); updateStep('child', 'active');
    var target = pickTarget();
    if (!target) { updateStep('group', 'fail'); showError('所有线路暂不可用'); return; }
    updateStep('group', 'done'); updateStep('child', 'done');
    updateStep('probe', 'active');
    if (titleEl) titleEl.textContent = '检测: ' + target.host + '...';
    var ok = await probe(target.host, PROBE_TIMEOUT);
    if (ok) {
      updateStep('probe', 'done');
      if (titleEl) titleEl.textContent = '连接成功，正在跳转...';
      window.location.replace('https://' + target.host + targetPath);
      return;
    }
    updateStep('probe', 'fail');
    markDead(target.host, 'probe_failed');
  }
  showError('连接失败，请重试');
};

function showError(msg) {
  var spinner = document.getElementById('spinner');
  var titleEl = document.getElementById('title');
  if (spinner) spinner.style.display = 'none';
  if (titleEl) titleEl.textContent = msg || '暂不可用';
  var allBtns = document.querySelectorAll('.jump-btn');
  allBtns.forEach(function(b) { b.disabled = false; b.style.opacity = '1'; });
}

// === 页面加载：预加载配置（后台静默，不执行轮值）===
loadState();
fetch(CONFIG_URL, { cache: 'no-store' }).then(function(resp) {
  return resp.json();
}).then(function(cfg) {
  config = cfg;
  updateStep('config', 'done');
}).catch(function() {
  updateStep('config', 'fail');
});

})();