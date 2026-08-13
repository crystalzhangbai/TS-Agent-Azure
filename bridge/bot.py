"""Teams Bot 消息处理。支持 1:1、群聊(groupChat)、频道(team)。

多用户/群组：同一个会话(conversation.id)共享一份多轮上下文；群聊里用户需要
@提及机器人，remove_recipient_mention 会把 @机器人 前缀去掉，只留真正的指令。
"""
import logging

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ActionTypes, Activity, ActivityTypes, CardAction, ChannelAccount, HeroCard

from brain_maf import classify_user_intent, clear_conversation_sessions, run_brain, run_smalltalk
from delegated_auth import DelegatedAuthRequiredError, clear_auth_state, get_auth_status, start_device_login
from runtime_event_logger import log_event
from session_environment import (
    clear_conversation_environment,
    format_environment,
    get_conversation_environment,
    list_environment_profiles,
    set_conversation_environment,
)

logger = logging.getLogger(__name__)


class SreBridgeBot(ActivityHandler):
    def __init__(self):
        pass

    async def _handle_smalltalk(self, turn_context: TurnContext, conv_id: str, text: str) -> bool:
        current_env = get_conversation_environment(conv_id)
        reply = await run_smalltalk(text, conv_id, session_environment=current_env)
        await turn_context.send_activity(reply)
        return True

    async def _send_environment_picker(self, turn_context: TurnContext):
        profiles = list_environment_profiles()
        if not profiles:
            await turn_context.send_activity(
                "当前没有可选环境。请先在 customers.json 或 session_environments.json 中配置环境。"
            )
            return

        buttons = [
            CardAction(
                title=f"{p['name']} ({p['auth_mode']})",
                type=ActionTypes.im_back,
                value=f"/env {p['name']}",
            )
            for p in profiles[:8]
        ]
        buttons.append(CardAction(title="清空环境", type=ActionTypes.im_back, value="/env clear"))
        card = HeroCard(
            title="请选择会话环境",
            text="查询类问题会按该环境上下文执行；非查询类会先主agent定位再进入nanite深度模式。",
            buttons=buttons,
        )
        await turn_context.send_activity(Activity(type=ActivityTypes.message, attachments=[card.to_attachment()]))

    async def _handle_env_command(self, turn_context: TurnContext, text: str, conv_id: str) -> bool:
        normalized = (text or "").strip()
        if not normalized:
            return False
        lower = normalized.lower()

        if lower in {"当前环境", "/env current", "env current", "/env status", "env status"}:
            current = get_conversation_environment(conv_id)
            await turn_context.send_activity(format_environment(current))
            return True

        if lower in {"/env", "env", "选择环境", "切换环境", "设置环境"}:
            await self._send_environment_picker(turn_context)
            return True

        if lower.startswith("/env "):
            arg = normalized[5:].strip()
            if not arg:
                await self._send_environment_picker(turn_context)
                return True
            if arg.lower() in {"current", "status", "当前"}:
                current = get_conversation_environment(conv_id)
                await turn_context.send_activity(format_environment(current))
                return True
            if arg.lower() in {"clear", "none", "reset", "清空"}:
                clear_conversation_environment(conv_id)
                clear_conversation_sessions(conv_id)
                clear_auth_state(conv_id)
                await turn_context.send_activity("已清空当前会话环境，并重置该会话记忆。")
                return True
            ok, msg = set_conversation_environment(conv_id, arg)
            if ok:
                clear_conversation_sessions(conv_id)
                clear_auth_state(conv_id)
                current = get_conversation_environment(conv_id)
                await turn_context.send_activity("已设置会话环境，并重置该会话记忆。\n" + format_environment(current))
            else:
                await turn_context.send_activity(msg)
                try:
                    await self._send_environment_picker(turn_context)
                except Exception:  # noqa: BLE001
                    logger.exception("send environment picker failed")
            return True

        return False

    async def _handle_auth_command(self, turn_context: TurnContext, text: str, conv_id: str) -> bool:
        normalized = (text or "").strip()
        lower = normalized.lower()
        if lower not in {"/auth", "/auth login", "/auth status", "auth", "auth login", "auth status"}:
            return False

        if lower in {"/auth", "auth", "/auth status", "auth status"}:
            st = get_auth_status(conv_id)
            if st.get("status") == "authenticated":
                await turn_context.send_activity(
                    f"认证状态: authenticated\n环境: {st.get('profile_name', '')}\ntenant: {st.get('tenant_id', '')}"
                )
            elif st.get("status") == "pending":
                await turn_context.send_activity(
                    "认证状态: pending\n"
                    f"verification_uri: {st.get('verification_uri', '')}\n"
                    f"user_code: {st.get('user_code', '')}\n"
                    "请先完成浏览器登录，再重试查询或再次执行 /auth status。"
                )
            elif st.get("status") == "failed":
                await turn_context.send_activity(f"认证状态: failed\n错误: {st.get('message', '')}\n请重新执行 /auth login")
            elif st.get("status") == "expired":
                await turn_context.send_activity(
                    f"认证状态: expired\n{st.get('message', '认证已过期')}\n"
                    "请重新执行 /auth login"
                )
            else:
                await turn_context.send_activity("认证状态: not_started\n请先选择 delegated 环境，然后执行 /auth login")
            return True

        current_env = get_conversation_environment(conv_id)
        if not current_env:
            await turn_context.send_activity("请先选择会话环境（/env）。")
            return True

        auth_mode = (current_env.get("auth_mode") or "").strip().lower()
        if auth_mode != "delegated":
            await turn_context.send_activity("当前环境不是 delegated 模式，无需执行 /auth login。")
            return True

        try:
            st = start_device_login(conv_id, current_env)
            await turn_context.send_activity(
                "请先完成 delegated 登录：\n"
                f"verification_uri: {st.get('verification_uri', '')}\n"
                f"user_code: {st.get('user_code', '')}\n"
                "完成后输入 /auth status 查看结果。"
            )
        except Exception as exc:  # noqa: BLE001
            await turn_context.send_activity(f"启动 delegated 登录失败: {exc}")
        return True

    async def on_message_activity(self, turn_context: TurnContext):
        # 群聊中去掉 @机器人 前缀
        text = TurnContext.remove_recipient_mention(turn_context.activity)
        text = (text or turn_context.activity.text or "").strip()
        conv_id = turn_context.activity.conversation.id

        log_event(
            "bot_user_message",
            status="received",
            inputs={"text": text},
            metadata={
                "conversation_id": conv_id,
                "channel_id": turn_context.activity.channel_id,
                "from_id": getattr(turn_context.activity.from_property, "id", ""),
            },
        )

        if not text:
            await turn_context.send_activity("请告诉我要排查的虚拟机内网IP和时间，例如：帮我看下 10.94.109.31 在 5/19 8:50 有没有问题")
            return

        if await self._handle_env_command(turn_context, text, conv_id):
            return

        if await self._handle_auth_command(turn_context, text, conv_id):
            return

        # Hybrid routing: deterministic commands first, then model intent routing.
        current_env = get_conversation_environment(conv_id)
        intent = await classify_user_intent(text, conv_id, session_environment=current_env)
        if intent == "smalltalk":
            await self._handle_smalltalk(turn_context, conv_id, text)
            return

        # 先发一个"正在处理"，长查询时给用户反馈
        await turn_context.send_activity(Activity(type=ActivityTypes.typing))

        try:
            current_env = get_conversation_environment(conv_id)
            reply = await run_brain(text, conv_id, session_environment=current_env)
        except DelegatedAuthRequiredError as exc:
            st = get_auth_status(conv_id)
            uri = st.get("verification_uri", "")
            code = st.get("user_code", "")
            if (not uri or not code) and current_env and (current_env.get("auth_mode") or "").lower() == "delegated":
                try:
                    started = start_device_login(conv_id, current_env)
                    uri = started.get("verification_uri", "")
                    code = started.get("user_code", "")
                except Exception:  # noqa: BLE001
                    pass
            reply = (
                "当前请求需要 delegated 认证。\n"
                "请先完成登录：\n"
                f"verification_uri: {uri}\n"
                f"user_code: {code}\n"
                "完成后重试原问题，或输入 /auth status 查看状态。"
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("brain error")
            err = str(exc)
            if "DelegatedAuthRequiredError" in type(exc).__name__ or "delegated" in err.lower():
                st = get_auth_status(conv_id)
                uri = st.get("verification_uri", "")
                code = st.get("user_code", "")
                reply = (
                    "当前请求需要 delegated 认证。\n"
                    "请先执行 /auth login，并按提示在浏览器完成登录。\n"
                    f"verification_uri: {uri}\n"
                    f"user_code: {code}"
                )
            else:
                reply = f"处理时出错：{exc}"
            log_event(
                "bot_brain_error",
                status="error",
                inputs={"text": text},
                error=str(exc),
                metadata={"conversation_id": conv_id},
            )

        log_event(
            "bot_reply",
            status="ok",
            outputs={"reply": reply},
            metadata={"conversation_id": conv_id},
        )
        await turn_context.send_activity(reply)

    async def on_members_added_activity(
        self, members_added: list[ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "👋 我是 SRE Bridge，可以帮你排查 Azure 虚拟机问题。\n"
                    "先设置环境：/env prod 或 /env delegated（不区分大小写），查看当前环境：/env current。\n"
                    "在群里 @我 并描述问题，例如：`@SRE Bridge 帮我看下 10.94.109.31 在 5/19 8:50 有没有问题`"
                )
