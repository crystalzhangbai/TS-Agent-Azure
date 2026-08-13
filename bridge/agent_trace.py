"""工具调用链追踪 —— 局部可观测性。

给每个工具函数包一层，记录本轮对话里"工具/skill 被按什么顺序调用、参数是什么"，
并把这条链路附在回复末尾（Teams 里可见）。用 ContextVar，跨 async/线程安全、按会话隔离。

用 SHOW_TRACE=false 关闭链路展示（默认展示，方便调试）。
"""
import contextvars
import functools
import logging
import os

logger = logging.getLogger("sre.trace")

_trace: contextvars.ContextVar = contextvars.ContextVar("sre_trace", default=None)
_SHOW = os.environ.get("SHOW_TRACE", "true").lower() != "false"


def start_trace() -> None:
    """在一轮 agent.run 前调用，开启本轮追踪。"""
    _trace.set([])


def get_trace() -> list:
    return _trace.get() or []


def traced(fn):
    """包裹工具函数：调用时记录顺序+参数，并原样执行。保留签名/注解/docstring 供 MAF 生成 schema。"""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t = _trace.get()
        seq = (len(t) + 1) if t is not None else 0
        brief = {k: (str(v)[:80]) for k, v in kwargs.items()}
        logger.info("[trace] #%s -> %s %s", seq, fn.__name__, brief)
        if t is not None:
            t.append({"seq": seq, "tool": fn.__name__, "args": brief})
        return fn(*args, **kwargs)

    return wrapper


def format_trace() -> str:
    """把本轮调用链格式化成附在回复末尾的文本。"""
    if not _SHOW:
        return ""
    t = get_trace()
    if not t:
        return ""
    lines = ["", "", "【排查链路（工具调用顺序）】"]
    for e in t:
        a = ", ".join(f"{k}={v}" for k, v in e["args"].items())
        lines.append(f"{e['seq']}. {e['tool']}({a})")
    return "\n".join(lines)
