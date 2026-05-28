/**
 * 企业级两级域名轮值引擎 v2.1
 * 主域名优先 + 8轮值降级, 配置从AI后台API拉取
 */
(function(){'use strict';
const API_URL='/ai/api/rotation/two-level/public-config';
const STORAGE_KEY='lr_v2';
const DEAD_TTL=600000;
const PROBE_TIMEOUT=3000;
const MAX_RETRIES=3;
let state={deadDomains:{},groupIndex:0,childIndex:{}};
let config=null,startTime=Date.now();

function loadState(){try{const r=localStorage.getItem(STORAGE_KEY);if(r){const p=JSON.parse(r);state={...state,...p};const n=Date.now();for(const[k,v]of Object.entries(state.deadDomains)){if(n-v.time>DEAD_TTL)delete state.deadDomains[k]}}}catch(e){}}
function saveState(){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(state))}catch(e){}}
function isAlive(d){const dead=state.deadDomains[d];if(!dead)return true;if(Date.now()-dead.time>DEAD_TTL){delete state.deadDomains[d];saveState();return true}return false}
function markDead(d,r){state.deadDomains[d]={time:Date.now(),reason:r||'unknown'};saveState()}
function probe(host,timeout){return new Promise(r=>{const img=new Image();const t=setTimeout(()=>{img.src='';r(false)},timeout);img.onload=()=>{clearTimeout(t);r(true)};img.onerror=()=>{clearTimeout(t);r(false)};img.src='https://'+host+'/favicon.ico?_r='+Date.now()})}

function pickChild(group){
  const alive=group.children.filter(c=>isAlive(c.host));
  if(!alive.length)return null;
  const id=group.id||'primary';
  if(!state.childIndex[id])state.childIndex[id]=0;
  const idx=state.childIndex[id]%alive.length;
  const picked=alive[idx];
  state.childIndex[id]=(idx+1)%alive.length;
  saveState();
  return picked;
}

function pickTarget(){
  // 1. 主域名优先
  const p=config.primary;
  if(p&&isAlive(p.main)){
    const alive=p.children.filter(c=>isAlive(c.host));
    if(alive.length>0){const child=pickChild(p);if(child)return child}
  }
  // 2. 轮值域名降级(按权重)
  const rotation=(config.rotation||[]).filter(r=>r.enabled!==false).sort((a,b)=>(b.weight||1)-(a.weight||1));
  for(const r of rotation){
    if(!isAlive(r.main))continue;
    const alive=r.children.filter(c=>isAlive(c.host));
    if(!alive.length){markDead(r.main,'all_children_dead');continue}
    const child=pickChild(r);if(child)return child;
  }
  return null;
}

function showManualLinks(hosts){
  const el=document.getElementById('fallback');if(!el)return;
  document.getElementById('spinner').style.display='none';
  if(!hosts||!hosts.length){el.innerHTML='<p style=color:#ff4d4f;font-size:13px>所有线路暂不可用</p>';el.style.display='block';return}
  el.innerHTML='<p style=font-size:12px;color:rgba(255,255,255,.5);margin-bottom:8px>手动选择线路:</p>'+hosts.slice(0,12).map(h=>'<a href=https://'+h.host+'>'+h.host+'</a>').join('');
  el.style.display='block';
}

function updateStep(name,status){
  const el=document.querySelector('[data-step='+name+']');
  if(el)el.className='step '+status;
}

async function run(){
  startTime=Date.now();loadState();updateStep('config','active');
  try{
    const r=await fetch(API_URL,{cache:'no-store'});config=await r.json();
    updateStep('config','done');
  }catch(e){updateStep('config','fail');showManualLinks([]);return}

  for(let retry=0;retry<MAX_RETRIES;retry++){
    updateStep('group','active');updateStep('child','active');
    const target=pickTarget();
    if(!target){updateStep('group','fail');showManualLinks([]);return}
    updateStep('group','done');updateStep('child','done');

    updateStep('probe','active');
    const ok=await probe(target.host,PROBE_TIMEOUT);
    if(ok){updateStep('probe','done');updateStep('redirect','active');
      document.getElementById('title').textContent='跳转中...';
      setTimeout(()=>{window.location.replace('https://'+target.host)},200);
      setTimeout(()=>{if(document.visibilityState==='visible')showManualLinks([target])},5000);
      return}
    updateStep('probe','fail');markDead(target.host,'probe_failed');retry++;
  }
  updateStep('redirect','fail');showManualLinks([]);
}
run().catch(()=>showManualLinks([]));
})();
