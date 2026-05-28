/**
 * 企业级两级域名轮值引擎 v3.1
 * 落地页 → 检测 → 显示按钮 → 用户点击跳转
 *
 * 粘性组逻辑：粘在当前组轮子域名，组死才切下一组
 */
(function(){'use strict';
var CONFIG_URL = '/domain-config.json';
var STORAGE_KEY = 'lr_v3';
var DEAD_TTL = 600000;
var PROBE_TIMEOUT = 3000;
var MAX_RETRIES = 3;

var state = { deadDomains: {}, groupIndex: 0, childIndex: {} };
var config = null;
var pickedTarget = null;

function loadState() {
  try {
    var raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      var parsed = JSON.parse(raw);
      state.groupIndex = parsed.groupIndex || 0;
      state.childIndex = parsed.childIndex || {};
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
      childIndex: state.childIndex,
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

    var aliveChildren = group.children.filter(function(c) { return isAlive(c.host); });
    if (!aliveChildren.length) {
      markDead(group.main, 'all_children_dead');
      state.groupIndex = (groupIdx + 1) % groups.length;
      tried++;
      saveState();
      continue;
    }

    var cid = group.id || group.main;
    if (typeof state.childIndex[cid] === 'undefined') state.childIndex[cid] = 0;
    var childIdx = state.childIndex[cid] % aliveChildren.length;
    var picked = aliveChildren[childIdx];
    state.childIndex[cid] = (childIdx + 1) % aliveChildren.length;
    saveState();
    return { group: group, child: picked };
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
  document.getElementById('targetInfo').textContent = '目标: ' + target.host + ' (' + target.group.main + ')';
  document.getElementById('targetInfo').classList.add('show');
}

function showManualLinks(targets) {
  var el = document.getElementById('fallback');
  if (!el) return;
  document.getElementById('spinner').style.display = 'none';
  document.getElementById('jumpBtn').style.display = 'none';
  if (!targets || !targets.length) {
    document.getElementById('title').textContent = '所有线路暂不可用';
    el.innerHTML = '<p style="color:#ff4d4f">请稍后重试或联系管理员</p>';
    el.style.display = 'block';
    return;
  }
  var html = '<p style="font-size:12px;color:var(--muted);margin-bottom:8px">手动选择:</p>';
  targets.slice(0, 12).forEach(function(h) {
    html += '<a href="https://' + h.host + '">' + h.host + '</a>';
  });
  el.innerHTML = html;
  el.style.display = 'block';
}

window.doJump = function() {
  if (pickedTarget) {
    window.location.replace('https://' + pickedTarget.child.host);
  }
};

async function run() {
  loadState();
  updateStep('config', 'active');

  try {
    var resp = await fetch(CONFIG_URL, { cache: 'no-store' });
    config = await resp.json();
    updateStep('config', 'done');
  } catch(e) {
    updateStep('config', 'fail');
    showManualLinks([]);
    return;
  }

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
      pickedTarget = target;
      showJumpButton({ host: target.child.host, group: { main: target.group.main } });
      return;
    }

    updateStep('probe', 'fail');
    markDead(target.child.host, 'probe_failed');
  }

  showManualLinks([]);
}

run().catch(function() { showManualLinks([]); });
})();