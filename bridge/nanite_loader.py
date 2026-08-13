"""Nanite agent adapter.

Keeps naniteagent as an independent expert package (agent profile + MCP config + hooks + skills)
while exposing read-only helper tools to the main MAF runtime.
"""

import glob
import json
import os
from typing import Any

import yaml

_BRIDGE_DIR = os.path.dirname(__file__)
_NANITE_ROOT = os.path.join(_BRIDGE_DIR, "naniteagent-playground", "naniteagent")
_NANITE_AGENT_FILE = os.path.join(_NANITE_ROOT, "agents", "nanite-agent.md")
_NANITE_MCP_FILE = os.path.join(_NANITE_ROOT, ".mcp.json")
_NANITE_HOOKS_FILE = os.path.join(_NANITE_ROOT, "hooks", "hooks.json")
_NANITE_SKILLS_DIR = os.path.join(_NANITE_ROOT, "skills")


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if text.lstrip().startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                fm = {}
            return fm, parts[2].lstrip("\n")
    return {}, text


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _read_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_nanite_skills() -> list[dict[str, str]]:
    skills: list[dict[str, str]] = []
    pattern = os.path.join(_NANITE_SKILLS_DIR, "*", "SKILL.md")
    for path in glob.glob(pattern):
        try:
            fm, _ = _parse_frontmatter(_read_text(path))
        except OSError:
            continue
        skills.append(
            {
                "name": fm.get("name") or os.path.basename(os.path.dirname(path)),
                "description": (fm.get("description") or "").strip(),
                "path": path,
            }
        )
    return skills


def build_nanite_skill_index() -> str:
    skills = list_nanite_skills()
    if not skills:
        return ""
    lines = [
        "## Nanite Expert Skills",
        "When deep-mode is enabled, load the matching skill before deep investigation:",
    ]
    for s in skills:
        lines.append(f"- {s['name']}: {s['description']}")
    return "\n".join(lines)


def load_nanite_skill(skill_name: str) -> str:
    """Load a nanite skill body by name."""
    for s in list_nanite_skills():
        if s["name"] == skill_name:
            _, body = _parse_frontmatter(_read_text(s["path"]))
            return body
    available = [s["name"] for s in list_nanite_skills()]
    return f"nanite skill not found: {skill_name}. available={available}"


def read_nanite_skill_file(skill_name: str, relative_path: str) -> str:
    """Read a file under nanite skill directory with path traversal protection."""
    skill_dir = ""
    for s in list_nanite_skills():
        if s["name"] == skill_name:
            skill_dir = os.path.dirname(s["path"])
            break
    if not skill_dir:
        return f"nanite skill not found: {skill_name}"

    target = os.path.normpath(os.path.join(skill_dir, relative_path))
    if not target.startswith(os.path.normpath(skill_dir) + os.sep):
        return "refused: path outside nanite skill directory"
    if not os.path.isfile(target):
        return f"file not found: {relative_path}"
    try:
        return _read_text(target)
    except OSError as exc:
        return f"read failed: {exc}"


def load_nanite_agent_instructions() -> str:
    """Load independent nanite expert-agent instruction profile."""
    return _read_text(_NANITE_AGENT_FILE)


def get_nanite_profile() -> str:
    """Return nanite independent-agent profile summary (agent/mcp/hooks/skills)."""
    mcp = _read_json(_NANITE_MCP_FILE) if os.path.exists(_NANITE_MCP_FILE) else {}
    hooks = _read_json(_NANITE_HOOKS_FILE) if os.path.exists(_NANITE_HOOKS_FILE) else {}
    skills = list_nanite_skills()
    payload = {
        "nanite_root": _NANITE_ROOT,
        "agent_file": _NANITE_AGENT_FILE,
        "mcp_configured": bool(mcp.get("mcpServers")),
        "mcp_servers": sorted(list((mcp.get("mcpServers") or {}).keys())),
        "hooks_configured": bool(hooks.get("hooks")),
        "hook_events": sorted(list((hooks.get("hooks") or {}).keys())),
        "skill_count": len(skills),
        "skills": [s["name"] for s in skills],
    }
    return json.dumps(payload, ensure_ascii=False)
