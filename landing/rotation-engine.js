/**
 * 企业级两级域名轮值引擎 v3.4
 * 粘组 + 随机前缀 + 按钮跳转
 * a1.A.com → a2.A.com → a3.A.com（随机不重复）→ A死 → B组
 */
(function(){'use strict';
var CONFIG_URL = '/domain-config.json';
var STORAGE_KEY = 'lr_v34';
var DEAD_TTL = 600000;
var PROBE_TIMEOUT = 3000;
var MAX_RETRIES = 3;

var state = { deadDomains: {}, groupIndex: 0, usedPrefixes: {} };
var config = null;
var pickedTarget = null;

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

function showJumpButton(target) {
  document.getElementById('spinner').style.display = 'none';
  document.getElementById('title').textContent = '线路已就绪';
  document.getElementById('jumpBtn').classList.add('show');
  document.getElementById('targetInfo').textContent = '目标: ' + target.host;
  document.getElementById('targetInfo').classList.add('show');
}

function showManualLinks() {
  var el = document.getElementById('fallback');
  if (!el) return;
  document.getElementById('spinner').style.display = 'none';
  document.getElementById('jumpBtn').style.display = 'none';
  document.getElementById('title').textContent = '所有线路暂不可用';
  el.innerHTML = '<p style="color:#ff4d4f">请稍后重试</p>';
  el.style.display = 'block';
}

window.doJump = function() {
  if (pickedTarget) window.location.replace('https://' + pickedTarget.host + '/');
};

async function run() {
  loadState();
  updateStep('config', 'active');
  try {
    var resp = await fetch(CONFIG_URL, { cache: 'no-store' });
    config = await resp.json();
    updateStep('config', 'done');
  } catch(e) { updateStep('config', 'fail'); showManualLinks(); return; }

  for (var retry = 0; retry < MAX_RETRIES; retry++) {
    updateStep('group', 'active'); updateStep('child', 'active');
    var target = pickTarget();
    if (!target) { updateStep('group', 'fail'); showManualLinks(); return; }
    updateStep('group', 'done'); updateStep('child', 'done');
    updateStep('probe', 'active');
    var ok = await probe(target.host, PROBE_TIMEOUT);
    if (ok) { updateStep('probe', 'done'); pickedTarget = target; showJumpButton(target); return; }
    updateStep('probe', 'fail'); markDead(target.host, 'probe_failed');
  }
  showManualLinks();
}
run().catch(function() { showManualLinks(); });
})();