#!/usr/bin/env bash
# cowork-skills-cn-pack 一键安装脚本
# 把 skills/ 下所有 skill 安装到本地 Cowork / Claude Code 环境

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$REPO_DIR/skills"

echo "==> cowork-skills-cn-pack installer"
echo "    source: $SKILLS_SRC"
echo

# 探测目标目录
detect_target() {
    # macOS Cowork
    local cowork_mac="$HOME/Library/Application Support/Claude/skills"
    # Linux Cowork
    local cowork_linux="$HOME/.config/Claude/skills"
    # Claude Code 标准位置
    local cc_home="$HOME/.claude/skills"
    local cc_proj="$REPO_DIR/.claude/skills"

    if [[ -d "$HOME/Library/Application Support/Claude" ]]; then
        echo "$cowork_mac"
    elif [[ -d "$HOME/.config/Claude" ]]; then
        echo "$cowork_linux"
    elif [[ -d "$HOME/.claude" ]]; then
        echo "$cc_home"
    else
        echo "$cc_home"  # 默认创建 Claude Code 用户目录
    fi
}

TARGET="$(detect_target)"
mkdir -p "$TARGET"

echo "==> target: $TARGET"
echo

# 拷贝每个 skill
for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name="$(basename "$skill_dir")"
    if [[ ! -f "$skill_dir/SKILL.md" ]]; then
        echo "    [skip] $skill_name (no SKILL.md)"
        continue
    fi
    rm -rf "$TARGET/$skill_name"
    cp -R "$skill_dir" "$TARGET/$skill_name"
    echo "    [ok]   $skill_name"
done

echo
echo "==> done. 重启 Cowork / Claude Code 后即可在新会话中触发这些 skill。"
echo "    试试: \"帮我评审 PR #123 的 diff\""
