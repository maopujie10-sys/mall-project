''" -- //''"
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state

router = APIRouter(prefix="/notifications", tags=["Notifications"])

MAX_NOTIFICATIONS = 200


def push_notification(title: str, message: str, ntype: str = "info", link: str = ''):
    ''"()''"
    notif = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3],
        "time": datetime.now().isoformat(),
        "title": title,
        "message": message[:200],
        "type": ntype,
        "link": link,
        "read": False,
    }
    notes = state._data.setdefault("notifications_list", [])
    notes.insert(0, notif)
    if len(notes) > MAX_NOTIFICATIONS:
        state._data["notifications_list"] = notes[:MAX_NOTIFICATIONS]
    state._save()
    return notif


@router.get('')
async def list_notifications(unread_only: bool = False, limit: int = 50, _=Depends(verify_token)):
    ''''''
    notes = state._data.get("notifications_list", [])
    if unread_only:
        notes = [n for n in notes if not n.get("read")]
    return {"ok": True, "notifications": notes[:limit], "total": len(notes), "unread": sum(1 for n in notes if not n.get("read"))}


@router.post("/read")
async def mark_read(notification_id: str = '', all: bool = False, _=Depends(verify_token)):
    ''''''
    notes = state._data.get("notifications_list", [])
    if all:
        for n in notes:
            n["read"] = True
    else:
        for n in notes:
            if n["id"] == notification_id:
                n["read"] = True
    state._save()
    return {"ok": True}


@router.post("/clear")
async def clear_notifications(_=Depends(verify_token)):
    ''''''
    await handle_risk("L2", '')
    state._data["notifications_list"] = []
    state._save()
    return {"ok": True}
