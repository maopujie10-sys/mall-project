''" -- : ///Telegram/Slack''"
import json, hashlib, os, httpx
from config import AGENT_TOKEN
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from tools.logger import get_logger

logger = get_logger("gateway")
router = APIRouter(prefix="/gateway", tags=["Gateway"])


PLATFORMS = {
    "wechat": {"token": os.getenv("WECHAT_TOKEN", ''), "aes_key": os.getenv("WECHAT_AES_KEY", '')},
    "wecom": {"corp_id": os.getenv("WECOM_CORP_ID", ''), "secret": os.getenv("WECOM_SECRET", ''), "agent_id": os.getenv("WECOM_AGENT_ID", '')},
    "dingtalk": {"app_key": os.getenv("DINGTALK_APP_KEY", ''), "app_secret": os.getenv("DINGTALK_APP_SECRET", '')},
    "telegram": {"bot_token": os.getenv("TELEGRAM_BOT_TOKEN", '')},
    "slack": {"bot_token": os.getenv("SLACK_BOT_TOKEN", ''), "signing_secret": os.getenv("SLACK_SIGNING_SECRET", '')},
    "line": {"channel_token": os.getenv("LINE_CHANNEL_TOKEN", ''), "channel_secret": os.getenv("LINE_CHANNEL_SECRET", '')},
}

class MessageGateway:
    ''''''

    @staticmethod
    async def handle_message(platform: str, user_id: str, text: str, extra: dict = None) -> dict:
        ''":  -> AI''"
        logger.info(f"[{platform}] {user_id}: {text[:100]}")
        try:
            # AI
            from routers.agent_chat import agent_chat as _chat
            from routers.agent_chat import ChatRequest
            #  -- HTTP
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    "http://127.0.0.1:9000/agent/chat",
                    json={"message": text, "history": []},
                    headers={"X-Agent-Token": AGENT_TOKEN or "friday-agent-token"},
                    timeout=30
                )
                if r.status_code == 200:
                    data = r.json(); reply_text = data.get("response") or data.get("reply") or str(data)[:500]; return {"ok": True, "reply": reply_text}
        except Exception as e:
            logger.info(f"Gateway AI call error: {e}")
        return {"ok": False, "reply": ","}

# =====  =====
@router.get("/wechat")
async def wechat_verify(signature: str = '', timestamp: str = '', nonce: str = '', echostr: str = ''):
    ''''''
    token = PLATFORMS["wechat"]["token"]
    if not token:
        return PlainTextResponse("not configured")
    tmp = sorted([token, timestamp, nonce])
    tmp_str = ''.join(tmp)
    if hashlib.sha1(tmp_str.encode()).hexdigest() == signature:
        return PlainTextResponse(echostr)
    return PlainTextResponse("fail")

@router.post("/wechat")
async def wechat_message(request: Request):
    ''''''
    try:
        body = await request.body()
        import xml.etree.ElementTree as ET
        root_elem = ET.fromstring(body)
        msg_type = root_elem.find("MsgType")
        from_user = root_elem.find("FromUserName")
        content = root_elem.find("Content")

        if msg_type is not None and msg_type.text == "text" and content is not None:
            result = await MessageGateway.handle_message(
                "wechat", from_user.text if from_user is not None else "unknown",
                content.text
            )
            reply_xml = f''"<xml>
<ToUserName><![CDATA[{from_user.text}]]></ToUserName>
<FromUserName><![CDATA[{root_elem.find("ToUserName").text}]]></FromUserName>
<CreateTime>{int(datetime.now().timestamp())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{result["reply"]}]]></Content>
</xml>''"
            return PlainTextResponse(reply_xml, media_type="application/xml")
    except Exception as e:
        logger.info(f"WeChat error: {e}")
    return PlainTextResponse("success")

# =====  =====
@router.post("/wecom")
async def wecom_message(request: Request):
    ''''''
    try:
        data = await request.json()
        msg_type = data.get("MsgType", '')
        if msg_type == "text":
            from_user = data.get("FromUserName", "unknown")
            content = data.get("Content", '')
            result = await MessageGateway.handle_message("wecom", from_user, content)
            return JSONResponse({
                "ToUserName": data.get("FromUserName", ''),
                "MsgType": "text",
                "Content": result["reply"]
            })
    except: pass
    return JSONResponse({"errcode": 0})

# =====  =====
@router.post("/dingtalk")
async def dingtalk_message(request: Request):
    ''''''
    try:
        data = await request.json()
        text = data.get("text", {}).get("content", '')
        sender = data.get("senderNick", "unknown")
        session = data.get("sessionWebhook", '')
        if text:
            result = await MessageGateway.handle_message("dingtalk", sender, text)
            
            if session:
                async with httpx.AsyncClient() as client:
                    await client.post(session, json={
                        "msgtype": "text",
                        "text": {"content": result["reply"]}
                    }, timeout=10)
            return JSONResponse({"ok": True, "reply": result["reply"]})
    except: pass
    return JSONResponse({"ok": True})

# ===== Telegram =====
@router.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request):
    ''"Telegram Bot Webhook''"
    if token != PLATFORMS["telegram"]["bot_token"]:
        return JSONResponse({"ok": False})
    try:
        data = await request.json()
        msg = data.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", '')
        if text and chat_id:
            result = await MessageGateway.handle_message("telegram", str(chat_id), text)
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": chat_id, "text": result["reply"]},
                    timeout=10
                )
    except: pass
    return JSONResponse({"ok": True})

# ===== Slack =====
@router.post("/slack")
async def slack_event(request: Request):
    ''"Slack Events API''"
    try:
        data = await request.json()
        # URL
        if data.get("type") == "url_verification":
            return JSONResponse({"challenge": data.get("challenge")})
        
        event = data.get("event", {})
        if event.get("type") == "app_mention":
            text = event.get("text", '').replace("<@BOT_ID>", '').strip()
            channel = event.get("channel", '')
            if text:
                result = await MessageGateway.handle_message("slack", channel, text)
                async with httpx.AsyncClient() as client:
                    await client.post(
                        "https://slack.com/api/chat.postMessage",
                        headers={"Authorization": f"Bearer {PLATFORMS['slack']['bot_token']}"},
                        json={"channel": channel, "text": result["reply"]},
                        timeout=10
                    )
    except: pass
    return JSONResponse({"ok": True})

# ===== LINE =====
@router.post("/line")
async def line_webhook(request: Request):
    ''"LINE Messaging API''"
    try:
        data = await request.json()
        for event in data.get("events", []):
            if event.get("type") == "message" and event["message"].get("type") == "text":
                reply_token = event.get("replyToken")
                text = event["message"]["text"]
                user_id = event["source"].get("userId", "unknown")
                if text:
                    result = await MessageGateway.handle_message("line", user_id, text)
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            "https://api.line.me/v2/bot/message/reply",
                            headers={"Authorization": f"Bearer {PLATFORMS['line']['channel_token']}"},
                            json={"replyToken": reply_token, "messages": [{"type":"text","text":result["reply"]}]},
                            timeout=10
                        )
    except: pass
    return JSONResponse({"ok": True})
