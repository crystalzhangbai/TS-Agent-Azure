"""aiohttp 服务端，暴露 /api/messages 给 Bot Framework / Teams。"""
import sys
import traceback
from datetime import datetime

from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import TurnContext
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import (
    CloudAdapter,
    ConfigurationBotFrameworkAuthentication,
)
from botbuilder.schema import Activity, ActivityTypes

from bot import SreBridgeBot
from config import DefaultConfig

CONFIG = DefaultConfig()

ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))


async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("抱歉，机器人内部出错了。")
    # 便于 Bot Framework Emulator 调试
    if context.activity.channel_id == "emulator":
        await context.send_activity(
            Activity(
                label="TurnError",
                name="on_turn_error Trace",
                timestamp=datetime.utcnow(),
                type=ActivityTypes.trace,
                value=f"{error}",
                value_type="https://www.botframework.com/schemas/error",
            )
        )


ADAPTER.on_turn_error = on_error

BOT = SreBridgeBot()


async def messages(req: Request) -> Response:
    return await ADAPTER.process(req, BOT)


async def health(_req: Request) -> Response:
    return web.Response(text="ok")


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/", health)


if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as exc:  # noqa: BLE001
        raise exc
