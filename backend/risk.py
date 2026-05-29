閿?""妞嬪酣娅撶粵澶岄獓閹貉冨煑 閳?L1閼奉亜濮?/ L2鐠佹澘缍?闁氨鐓?/ L3闂団偓鐎光剝澹?/ L4瀵搫鍩楅幒銉ь吀"""
import httpx
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from state import state

RISK_LEVELS = {"L1", "L2", "L3", "L4"}


async def handle_risk(level: str, action_name: str, detail: str = "") -> dict:
    """
    妞嬪酣娅撶粵澶岄獓閹凤附鍩呴崳銊ｂ偓?    - L1: 閼奉亜濮╅弨鎹愵攽閿涘奔绮庨幍鎾冲祪閺冦儱绻?    - L2: 閺€鎹愵攽 + 鐠佹澘缍嶆禒璇插 + 閹恒劑鈧?Telegram 闁氨鐓?    - L3: 閸掓稑缂撳鍛吀閹靛綊銆嶉敍宀€鐡戝鍛暏閹撮鈥樼拋銈呮倵閺傜懓褰查幍褑顢?    - L4: 瀵搫鍩楅崚鍥ㄥ床娴滃搫浼愰幒銉ь吀濡€崇础閿涘瞼顩﹀銏ｅ殰閸斻劍澧界悰?
    鏉╂柨娲?
      L1/L2: {"allowed": True, "risk": level, "task_id": "..."}
      L3:    {"allowed": False, "risk": "L3", "approval_id": "...", "message": "闂団偓鐎光剝澹掔涵顔款吇"}
      L4:    {"allowed": False, "risk": "L4", "message": "妤傛﹢顥撻梽鈺傛惙娴ｆ粣绱濆鎻掑繁閸掓湹姹夊銉﹀复缁?}
    """
    if level not in RISK_LEVELS:
        level = "L1"

    if level == "L1":
        print(f"[Risk] L1 | {action_name} | {detail or '-'}")
        return {"allowed": True, "risk": "L1", "task_id": ""}

    if level == "L2":
        task = state.add_task(name=action_name, risk="L2")
        _send_notification(action_name, detail)
        return {"allowed": True, "risk": "L2", "task_id": task["id"]}

    if level == "L3":
        task_id = f"approval_{int(datetime.now().timestamp())}"
        state.add_approval(task_id=task_id, risk="L3", name=action_name, description=detail)
        _send_notification(f"棣冪厸 L3 闂団偓鐎光剝澹? {action_name}", detail)
        return {
            "allowed": False,
            "risk": "L3",
            "approval_id": task_id,
            "message": "濮濄倖鎼锋担婊堟付鐟曚礁顓搁幍鍦€樼拋銈忕礉鐠囧嘲澧犲鈧€光剝澹掓稉顓炵妇婢跺嫮鎮?,
        }

    if level == "L4":
        state.mode = "human_control"
        state.add_emergency("human_control", f"L4妤傛﹢顥撻梽鈺傛惙娴? {action_name}")
        state.add_task(name=action_name, risk="L4", status="瀹稿弶瀚嗙紒?娴滃搫浼愰幒銉ь吀")
        _send_notification(f"棣冩暥 L4 瀵搫鍩楅幒銉ь吀: {action_name}", f"{detail}\n缁崵绮哄鑼跺殰閸斻劌鍨忛幑顫礋娴滃搫浼愰幒銉ь吀濡€崇础")
        return {
            "allowed": False,
            "risk": "L4",
            "message": "妤傛﹢顥撻梽鈺傛惙娴ｆ粣绱濆鎻掑繁閸掕泛鍨忛幑顫礋娴滃搫浼愰幒銉ь吀濡€崇础閿涘矁鍤滈崝銊﹀⒔鐞涘苯鍑￠崑婊勵剾",
            "mode": "human_control",
        }


def _send_notification(action_name: str, detail: str):
    """閸欐垿鈧線鈧氨鐓￠崚?Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    import asyncio

    text = (
        f"\u2699\ufe0f <b>TikTokMall Agent</b>\n"
        f"<b>閹垮秳缍?/b>: {action_name}\n"
        f"<b>鐠囷附鍎?/b>: {detail or '-'}\n"
        f"<b>閺冨爼妫?/b>: {datetime.now().strftime('%H:%M:%S')}"
    )

    async def _send():
        try:
            async with httpx.AsyncClient(timeout=5) as c:
                await c.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
                )
        except Exception:
            pass

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(_send())
        else:
            loop.run_until_complete(_send())
    except Exception:
        pass
