"""服务器管理 v2 — CPU/内存/磁盘/进程/文件/日志/自动治理"""
import os, psutil, shutil, subprocess
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from auth import verify_token
from risk import handle_risk
from state import state

router = APIRouter(prefix="/server", tags=["Server"])

# ===== ===== 状态监控 ===== =====
@router.get("/status")
async def server_status(_=Depends(verify_token)):
    """完整服务器状态（含内存详情+Swap+进程数+运行时间）"""
    await handle_risk("L1", "查看服务器状态")
    cpu = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage("/")
    try: load = os.getloadavg()
    except: load = [0,0,0]
    # 内存详情
    mem_detail = {k: round(v/(1024**3),1) for k,v in {"total":mem.total,"available":mem.available,"used":mem.used,"free":mem.free,"buffers":mem.buffers or 0,"cached":mem.cached or 0}.items()}
    mem_detail["percent"] = mem.percent
    # 缓存占用量（可释放部分）
    cache_gb = round((mem.cached or 0) / (1024**3), 1)
    buffer_gb = round((mem.buffers or 0) / (1024**3), 1)
    reclaimable_gb = round((mem.cached + (mem.buffers or 0)) / (1024**3), 1)
    # 保存到历史
    state.append_data("metrics_history", {"time":datetime.now().isoformat(),"cpu":cpu,"memory":mem.percent}, 2880)
    # 内存健康分级
    health = "good" if mem.percent < 70 else ("warning" if mem.percent < 85 else ("critical" if mem.percent < 95 else "danger"))
    return {
        "cpu": round(cpu,1), "cpu_count": psutil.cpu_count(),
        "memory": mem_detail, "swap": {"total_gb":round(swap.total/(1024**3),1),"used_gb":round(swap.used/(1024**3),1),"percent":swap.percent},
        "cache": {"buffers_gb":buffer_gb,"cached_gb":cache_gb,"reclaimable_gb":reclaimable_gb},
        "disk": {"total_gb":round(disk.total/(1024**3),1),"used_gb":round(disk.used/(1024**3),1),"percent":disk.percent},
        "load": {"1min":round(load[0],2),"5min":round(load[1],2),"15min":round(load[2],2)},
        "process_count": len(psutil.pids()),
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
        "health": health,
    }

# ===== ===== 内存管理 ===== =====
@router.get("/memory/top")
async def memory_top(limit: int = 20, _=Depends(verify_token)):
    """查看内存消耗最高的进程"""
    await handle_risk("L1", "查看内存TOP")
    procs = []
    for p in psutil.process_iter(["pid","name","memory_percent","memory_info","cpu_percent","create_time","cmdline"]):
        try:
            info = p.info
            info["memory_mb"] = round((info.get("memory_info") and info["memory_info"].rss or 0) / (1024**2), 1)
            info["uptime_hours"] = round((datetime.now().timestamp() - (info.get("create_time") or datetime.now().timestamp())) / 3600, 1)
            info["cmd"] = " ".join(info.get("cmdline") or [])[:100]
            procs.append(info)
        except: pass
    top_mem = sorted(procs, key=lambda x: x.get("memory_mb",0) or 0, reverse=True)[:limit]
    total_mb = sum(p.get("memory_mb",0) for p in top_mem)
    return {"processes": top_mem, "total_mb": round(total_mb,1), "count": len(top_mem)}

@router.get("/memory/trend")
async def memory_trend(hours: int = 24, _=Depends(verify_token)):
    """内存使用趋势（历史数据）"""
    await handle_risk("L1", "查看内存趋势")
    history = state._data.get("metrics_history", [])
    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
    points = [h for h in history if h.get("time","") >= cutoff]
    # 聚合为每5分钟一个点
    aggregated = []
    seen = set()
    for p in points:
        t = p.get("time","")[:16]  # 精确到分钟
        if t not in seen:
            aggregated.append({"time":t,"cpu":p.get("cpu",0),"memory":p.get("memory",0)})
            seen.add(t)
    # 预测趋势（简单线性回归）
    mem_values = [p.get("memory",0) for p in aggregated[-60:]]
    if len(mem_values) > 5:
        trend = round((mem_values[-1] - mem_values[0]) / max(len(mem_values),1), 2)
        prediction = min(100, mem_values[-1] + trend * 12) if trend > 0 else mem_values[-1]
    else:
        trend = 0; prediction = mem_values[-1] if mem_values else 0
    return {"points": aggregated[-288:], "count": len(aggregated),
            "trend_per_hour": trend, "prediction_12h": round(prediction,1),
            "current": mem_values[-1] if mem_values else 0}

@router.get("/memory/leaks")
async def memory_leaks(_=Depends(verify_token)):
    """检测内存泄漏（持续增长的进程）"""
    await handle_risk("L1", "内存泄漏检测")
    history = state._data.get("process_memory_history", [])[-10:]
    if len(history) < 2: return {"leaks": [], "note": "需运行一段时间后检测"}
    leaks = []
    # 比较最近两次快照
    old = history[0] if history else {}
    new = history[-1] if history else {}
    for pid_str, old_mb in old.items():
        new_mb = new.get(pid_str, 0)
        if new_mb > old_mb * 1.3 and new_mb > 100:  # 增长>30%且>100MB
            try:
                p = psutil.Process(int(pid_str))
                leaks.append({"pid": int(pid_str), "name": p.name(), "growth_pct": round((new_mb-old_mb)/old_mb*100,1),
                              "old_mb": round(old_mb,1), "new_mb": round(new_mb,1)})
            except: pass
    # 保存当前快照
    snapshot = {}
    for p in psutil.process_iter(["pid","memory_info"]):
        try: snapshot[str(p.info["pid"])] = round((p.info["memory_info"].rss or 0)/(1024**2), 1)
        except: pass
    state._data["process_memory_history"] = (history + [snapshot])[-20:]
    return {"leaks": sorted(leaks, key=lambda x: x["growth_pct"], reverse=True), "count": len(leaks)}

# ===== ===== 内存自动释放 ===== =====
@router.post("/memory/release")
async def memory_release(mode: str = "safe", _=Depends(verify_token)):
    """释放内存（safe=只清缓存, aggressive=清缓存+杀空闲进程, max=清缓存+杀进程+停服务）"""
    await handle_risk("L2" if mode=="safe" else "L3", f"释放内存[{mode}]")
    before = psutil.virtual_memory()
    results = []; freed_mb = 0
    # 1. sync + drop_caches
    os.system("sync")
    try:
        with open("/proc/sys/vm/drop_caches","w") as f: f.write("3")
        results.append("✅ 清理缓存(pagecache+dentries+inodes)")
    except: results.append("⚠️ drop_caches需root权限")
    after_drop = psutil.virtual_memory()
    freed_mb += max(0, before.used - after_drop.used)
    # 2. aggressive: 杀空闲进程
    if mode in ("aggressive","max"):
        killed = 0
        for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent","create_time"]):
            try:
                info = p.info
                idle_hours = (datetime.now().timestamp() - (info.get("create_time") or 0))/3600
                mem_mb = round((p.memory_info().rss or 0)/(1024**2),1)
                # 杀：CPU<1% + 内存>100MB + 运行>24h
                if info.get("cpu_percent",0) < 1 and mem_mb > 100 and idle_hours > 24 and info.get("name") not in ("systemd","sshd","nginx"):
                    p.terminate()
                    killed += 1
                    results.append(f"✅ 终止空转进程 {info['name']}(PID={info['pid']}) 释放{mem_mb}MB")
                    freed_mb += mem_mb
            except: pass
        results.append(f"共终止{killed}个空转进程")
    # 3. max: 重启Docker/Nginx
    if mode == "max":
        subprocess.run(["systemctl","restart","nginx"], capture_output=True, timeout=10)
        results.append("✅ 重启Nginx释放内存")
        subprocess.run(["docker","system","prune","-f"], capture_output=True, timeout=30)
        results.append("✅ 清理Docker无用资源")
    after = psutil.virtual_memory()
    freed_mb = round(freed_mb/(1024**2),1)
    return {"ok": True, "freed_mb": freed_mb, "before_percent": before.percent, "after_percent": after.percent,
            "mode": mode, "actions": results}

# ===== ===== 磁盘管理 ===== =====
@router.get("/disk")
async def server_disk(_=Depends(verify_token)):
    """磁盘使用详情"""
    await handle_risk("L1", "查看磁盘详情")
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({"device":part.device,"mount":part.mountpoint,"fstype":part.fstype,
                          "total_gb":round(usage.total/(1024**3),1),"used_gb":round(usage.used/(1024**3),1),
                          "free_gb":round(usage.free/(1024**3),1),"percent":usage.percent})
        except: pass
    return {"disks": disks}

@router.get("/disk/large-files")
async def large_files(path: str = "/", min_mb: int = 100, _=Depends(verify_token)):
    """查找大文件"""
    await handle_risk("L1", f"查找大文件 {path}>{min_mb}MB")
    result = subprocess.run(["find",path,"-type","f","-size",f"+{min_mb}M","-exec","ls","-lh","{}",";"], capture_output=True,text=True,timeout=30)
    lines = result.stdout.strip().split("\n")[:50] if result.stdout else []
    return {"files": [{"path":l.split()[-1],"size":l.split()[4] if len(l.split())>4 else "?"} for l in lines if l.strip()], "count": len(lines)}

@router.post("/disk/clean-temp")
async def clean_temp(days: int = 7, _=Depends(verify_token)):
    """清理临时文件"""
    await handle_risk("L2", f"清理{days}天前的临时文件")
    freed_mb = 0; count = 0
    for d in ["/tmp","/var/tmp"]:
        try:
            for f in os.listdir(d):
                fp = os.path.join(d,f)
                if os.path.isfile(fp) and (datetime.now()-datetime.fromtimestamp(os.path.getmtime(fp))).days > days:
                    sz = os.path.getsize(fp)
                    os.remove(fp); freed_mb += sz; count += 1
        except: pass
    return {"ok": True, "freed_mb": round(freed_mb/(1024**2),1), "deleted": count}

# ===== ===== 原有端点 ===== =====
@router.get("/ports")
async def server_ports(_=Depends(verify_token)):
    await handle_risk("L1","查看服务器端口")
    data = []
    for conn in psutil.net_connections():
        if conn.status=="LISTEN": data.append({"port":conn.laddr.port,"pid":conn.pid})
    return {"listening":data}

@router.get("/processes")
async def server_processes(_=Depends(verify_token)):
    """进程列表（Top20 CPU）"""
    await handle_risk("L1","查看进程")
    procs = []
    for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent"]):
        try: procs.append(p.info)
        except: pass
    return {"top20":sorted(procs,key=lambda x:x.get("cpu_percent",0)or 0,reverse=True)[:20]}

@router.post("/kill-process")
async def server_kill_process(pid:int, _=Depends(verify_token)):
    await handle_risk("L3",f"终止进程 PID={pid}")
    try:
        p = psutil.Process(pid); name = p.name(); p.terminate()
        return {"ok":True,"pid":pid,"name":name,"status":"terminated"}
    except psutil.NoSuchProcess: raise HTTPException(404,"进程不存在")
    except Exception as e: raise HTTPException(500,f"终止失败:{e}")

@router.get("/files")
async def server_files(path:str="/", _=Depends(verify_token)):
    if not os.path.exists(path): raise HTTPException(404,"目录不存在")
    entries = []
    for name in sorted(os.listdir(path)):
        fp=os.path.join(path,name)
        try:
            st=os.stat(fp)
            entries.append({"name":name,"size":st.st_size,"is_dir":os.path.isdir(fp),
                           "modified":datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")})
        except: pass
    return {"path":path,"entries":entries}

@router.post("/files/upload")
async def server_file_upload(path:str="/tmp", file:UploadFile=File(...), _=Depends(verify_token)):
    os.makedirs(path,exist_ok=True)
    dest=os.path.join(path,file.filename or "upload")
    content=await file.read()
    with open(dest,"wb") as f: f.write(content)
    return {"ok":True,"path":dest,"size":len(content)}

@router.delete("/files")
async def server_file_delete(path:str, _=Depends(verify_token)):
    if not os.path.exists(path): raise HTTPException(404,"不存在")
    if os.path.isdir(path): os.rmdir(path)
    else: os.remove(path)
    return {"ok":True,"path":path}
