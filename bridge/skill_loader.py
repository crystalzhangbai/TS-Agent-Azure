"""可插拔 skill 加载器（对齐 OneVM Troubleshooter / Copilot 的 SKILL.md 模型）。

- skill = skills/<name>/SKILL.md，YAML frontmatter(name/description) + markdown 正文(SOP)。
- build_skill_index(): 把所有 skill 的 name+description 汇成索引，注入 agent 的 system prompt。
- load_skill(name): agent 判断某 skill 触发时，按需读取其正文（progressive disclosure）。

新增 skill = 往 skills/ 丢一个 <name>/SKILL.md 文件夹即可，无需改核心代码、无需重启逻辑。
"""
import glob
import os

import yaml

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 `---\\n<yaml>\\n---\\n<body>` 结构，返回 (frontmatter, body)。"""
    if text.lstrip().startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                fm = {}
            return fm, parts[2].lstrip("\n")
    return {}, text


def list_skills() -> list[dict]:
    """扫描 skills/ 下所有 SKILL.md，返回 [{name, description, path}]。"""
    skills = []
    for path in glob.glob(os.path.join(SKILLS_DIR, "*", "SKILL.md")):
        try:
            with open(path, encoding="utf-8") as f:
                fm, _ = _parse_frontmatter(f.read())
        except OSError:
            continue
        skills.append({
            "name": fm.get("name") or os.path.basename(os.path.dirname(path)),
            "description": (fm.get("description") or "").strip(),
            "path": path,
        })
    return skills


def build_skill_index() -> str:
    """生成注入 system prompt 的 skill 索引文本。"""
    skills = list_skills()
    if not skills:
        return ""
    lines = [
        "## 可用排障 Skill",
        "当用户的问题匹配下面某个 skill 的触发条件时，**先调用 load_skill(skill_name) 读取它的详细排查步骤**，再据此执行工具与分析：",
    ]
    for s in skills:
        lines.append(f"- `{s['name']}`：{s['description']}")
    return "\n".join(lines)


def load_skill(skill_name: str) -> str:
    """读取指定排障 skill 的完整操作步骤(SKILL.md 正文)。

    当用户问题匹配某个 skill 的触发条件时调用它，拿到该 skill 的详细排查 SOP/规则/查询模板。
    正文里可能引用 references/ 下的深层文件——用 read_skill_file 按需读取。
    """
    for s in list_skills():
        if s["name"] == skill_name:
            with open(s["path"], encoding="utf-8") as f:
                _, body = _parse_frontmatter(f.read())
            return body
    available = [s["name"] for s in list_skills()]
    return f"未找到 skill '{skill_name}'。当前可用: {available}"


def read_skill_file(skill_name: str, relative_path: str) -> str:
    """读取某个 skill 目录下的参考文件（如 references/xxx.md）。

    当 SKILL.md 正文或索引指向某个 companion / reference 文件时调用它按需加载深层知识。
    参数：
    - skill_name: skill 名（如 vm-kusto-query）。
    - relative_path: 相对该 skill 目录的路径（如 references/_meta/investigation-loop.md）。
    """
    skill_dir = None
    for s in list_skills():
        if s["name"] == skill_name:
            skill_dir = os.path.dirname(s["path"])
            break
    if skill_dir is None:
        return f"未找到 skill '{skill_name}'。"

    # 防路径穿越：解析后必须仍在该 skill 目录内
    target = os.path.normpath(os.path.join(skill_dir, relative_path))
    if not target.startswith(os.path.normpath(skill_dir) + os.sep):
        return "拒绝：路径越界，只能读取该 skill 目录内的文件。"
    if not os.path.isfile(target):
        return f"文件不存在：{relative_path}"
    try:
        with open(target, encoding="utf-8") as f:
            return f.read()
    except OSError as exc:
        return f"读取失败：{exc}"

