/**
 * 企业级两级域名轮值引擎 v3.0
 * ┌─ 8个主域名组（平等轮值）
 * │  ├── 组1: chxhx.eu.cc → www/shop/mall.chxhx.eu.cc
 * │  ├── 组2: drrgr.eu.cc → www/shop/mall.drrgr.eu.cc
 * │  └── ...
 * └─ 每组内二级域名池循环轮值
 *
 * 逻辑：
 *  1. 从上次使用的组的下一个开始
 *  2. 从该组的二级域名池选下一个
 *  3. 健康探测通过 → 跳转
 *  4. 当前组挂了 → 标记死亡 → 切下一组
 *  5. 全部组死亡 → 显示手动选择
 */
(function(){'use strict';
const CONFIG_URL = '/domain-config.json';
const STORAGE_KEY = 'lr_v3';
const DEAD_TTL = 600000;
const PROBE_TIMEOUT = 3000;
const MAX_RETRIES = 3;

let state = { deadDomains: {}, groupIndex: 0, childIndex: {} };
let config = null;

// === 状态持久化 ===
function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      state.groupIndex = parsed.groupIndex || 0;
      state.childIndex = parsed.childIndex || {};
      // 清理过期死亡记录
      const now = Date.now();
      for (const [k, v] of Object.entries(parsed.deadDomains || {})) {
        if (now - v.time < DEAD_TTL) state.deadDomains[k] = v;
      }
    }
  } catch(e) {}
}
function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      groupIndex: state.groupIndex,
      childIndex: state.childIndex,
      deadDomains: state.deadDomains
    }));
  } catch(e) {}
}

// === 健康检测 ===
function isAlive(host) {
  const dead = state.deadDomains[host];
  if (!dead) return true;
  if (Date.now() - dead.time > DEAD_TTL) {
    delete state.deadDomains[host];
    saveState();
    return true;
  }
  return false;
}
function markDead(host, reason) {
  state.deadDomains[host] = { time: Date.now(), reason: reason || 'unknown' };
  saveState();
}

// === 探测 ===
function probe(host, timeout) {
  return new Promise(function(resolve) {
    var img = new Image();
    var timer = setTimeout(function() { img.src = ''; resolve(false); }, timeout);
    img.onload = function() { clearTimeout(timer); resolve(true); };
    img.onerror = function() { clearTimeout(timer); resolve(false); };
    img.src = 'https://' + host + '/favicon.ico?_r=' + Date.now();
  });
}

// === 核心：粘性组轮值 ===
// 粘在当前组，只轮二级域名；当前组死了才切下一组
function pickTarget() {
  var groups = config.groups.filter(function(g) { return g.enabled !== false; });
  if (!groups.length) return null;

  var tried = 0;
  while (tried < groups.length) {
    var groupIdx = state.groupIndex % groups.length;
    var group = groups[groupIdx];

    if (!isAlive(group.main)) {
      // 组死了，标记并切下一组
      markDead(group.main, 'group_down');
      state.groupIndex = (groupIdx + 1) % groups.length;
      tried++;
      saveState();
      continue;
    }

    // 筛选存活的二级域名
    var aliveChildren = group.children.filter(function(c) { return isAlive(c.host); });
    if (!aliveChildren.length) {
      markDead(group.main, 'all_children_dead');
      state.groupIndex = (groupIdx + 1) % groups.length;
      tried++;
      saveState();
      continue;
    }

    // 轮值选取下一个二级域名
    var cid = group.id || group.main;
    if (typeof state.childIndex[cid] === 'undefined') state.childIndex[cid] = 0;
    var childIdx = state.childIndex[cid] % aliveChildren.length;
    var picked = aliveChildren[childIdx];
    state.childIndex[cid] = (childIdx + 1) % aliveChildren.length;
    // 组不变（粘住），下次继续用这个组
    saveState();
    return { group: group, child: picked };
  }
  return null;
}

// === UI ===
function updateStep(name, status) {
  var el = document.querySelector('[data-step=' + name + ']');
  if (el) el.className = 'step ' + status;
}
function showManualLinks(targets) {
  var el = document.getElementById('fallback');
  if (!el) return;
  document.getElementById('spinner').style.display = 'none';
  if (!targets || !targets.length) {
    el.innerHTML = '<p style="color:#ff4d4f;font-size:13px">⚠️ 所有线路暂不可用</p>';
    el.style.display = 'block';
    return;
  }
  var html = '<p style="font-size:12px;color:rgba(255,255,255,.5);margin-bottom:8px">手动选择线路:</p>';
  targets.slice(0, 12).forEach(function(h) {
    html += '<a href="https://' + h.host + '" style="display:block;padding:6px 12px;color:#fff;text-decoration:none;background:rgba(255,255,255,.1);border-radius:6px;margin-bottom:4px">' + h.host + '</a>';
  });
  el.innerHTML = html;
  el.style.display = 'block';
}

// === 主流程 ===
async function run() {
  loadState();
  updateStep('config', 'active');

  // 加载配置
  try {
    var resp = await fetch(CONFIG_URL, { cache: 'no-store' });
    config = await resp.json();
    updateStep('config', 'done');
  } catch(e) {
    updateStep('config', 'fail');
    showManualLinks([]);
    return;
  }

  // 多轮尝试
  for (var retry = 0; retry < MAX_RETRIES; retry++) {
    updateStep('group', 'active');
    updateStep('child', 'active');

    var target = pickTarget();
    if (!target) {
      updateStep('group', 'fail');
      showManualLinks([]);
      return;
    }
    updateStep('group', 'done');
    updateStep('child', 'done');

    updateStep('probe', 'active');
    var ok = await probe(target.child.host, PROBE_TIMEOUT);

    if (ok) {
      updateStep('probe', 'done');
      updateStep('redirect', 'active');
      document.getElementById('title').textContent = '跳转中 → ' + target.child.host;
      setTimeout(function() {
        window.location.replace('https://' + target.child.host);
      }, config.settings.redirectDelay || 200);

      // 兜底：5秒后还没跳转就显示手动链接
      setTimeout(function() {
        if (document.visibilityState === 'visible') showManualLinks([target.child]);
      }, 5000);
      return;
    }

    updateStep('probe', 'fail');
    markDead(target.child.host, 'probe_failed');
  }

  updateStep('redirect', 'fail');
  showManualLinks([]);
}

run().catch(function() { showManualLinks([]); });
})();