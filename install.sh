#!/usr/bin/env bash
# 把本目录安装（软链）到常见 Agent Skill 根目录。
#
#   ./install.sh                 # ~/.dsh/skills + ~/.agents/skills
#   ./install.sh --claude        # 额外装到 ~/.claude/skills
#   ./install.sh --target DIR    # 只装到指定目录
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="mao-zedong"
TARGETS=()
WITH_CLAUDE=0
CUSTOM=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude) WITH_CLAUDE=1; shift ;;
    --target) CUSTOM="${2:?--target 需要一个目录}"; shift 2 ;;
    -h|--help) sed -n '1,8p' "$0"; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 2 ;;
  esac
done

if [[ -n "$CUSTOM" ]]; then
  TARGETS=("$CUSTOM")
else
  TARGETS=("$HOME/.dsh/skills" "$HOME/.agents/skills")
  [[ $WITH_CLAUDE -eq 1 ]] && TARGETS+=("$HOME/.claude/skills")
fi

for root in "${TARGETS[@]}"; do
  mkdir -p "$root"
  ln -sfn "$SRC" "$root/$NAME"
  echo "已链接：$root/$NAME -> $SRC"
done

echo
echo "验证："
printf '  python3 %s/scripts/validate.py\n' "$SRC"
