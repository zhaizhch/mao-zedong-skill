#!/usr/bin/env bash
# 一键创建公开 GitHub 仓库并推送。
#
#   GITHUB_TOKEN=ghp_xxx ./publish.sh
#   GITHUB_TOKEN=ghp_xxx REPO_NAME=mao-zedong-skill ./publish.sh
#   GITHUB_TOKEN=ghp_xxx ./publish.sh --private    # 建私有库
#
# 需要：GITHUB_TOKEN（classic token 勾 repo，或 fine-grained 勾 Administration: write）
set -euo pipefail

REPO_NAME="${REPO_NAME:-mao-zedong-skill}"
DESC="毛泽东语料库收束 skill：154 条可考语料 + 文风仿写，为完成的任务写一段不空不假的总结"
VISIBILITY="public"

[[ "${1:-}" == "--private" ]] && VISIBILITY="false" || VISIBILITY="true"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  cat >&2 <<'EOF'
缺少 GITHUB_TOKEN。

获取方式：https://github.com/settings/tokens
  classic token：勾选 repo
  fine-grained：Repository permissions → Administration: Read and write

然后：
  GITHUB_TOKEN=ghp_xxx ./publish.sh
EOF
  exit 1
fi

api() { curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" "$@"; }

LOGIN="$(api https://api.github.com/user | python3 -c 'import json,sys; print(json.load(sys.stdin).get("login",""))')"
if [[ -z "$LOGIN" ]]; then
  echo "Token 无效或无法读取用户信息。" >&2
  exit 1
fi
echo "账号：${LOGIN}  仓库：${LOGIN}/${REPO_NAME}  可见性：$([[ "$VISIBILITY" == "true" ]] && echo public || echo private)"

# 创建仓库；已存在则复用
code="$(curl -sS -o /tmp/publish_repo.json -w '%{http_code}' \
  -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" \
  -X POST https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"$DESC\",\"private\":$VISIBILITY,\"has_issues\":true,\"has_wiki\":false}")"
if [[ "$code" == "201" ]]; then
  echo "已创建仓库。"
elif [[ "$code" == "422" ]]; then
  echo "仓库已存在，直接推送。"
else
  echo "创建仓库失败（HTTP $code）：" >&2
  cat /tmp/publish_repo.json >&2
  exit 1
fi

# 本地提交
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ ! -d .git ]]; then
  git init -q
  git checkout -q -b main
fi
git add -A
if ! git diff --cached --quiet; then
  git -c user.name="${GIT_NAME:-$LOGIN}" -c user.email="${GIT_EMAIL:-$LOGIN@users.noreply.github.com}" \
    commit -qm "feat: mao-zedong skill v1.0.0（154 条语料 + 收束工作流）"
fi

URL="https://github.com/$LOGIN/$REPO_NAME.git"
git remote remove origin 2>/dev/null || true
git remote add origin "$URL"

# 用请求头带凭据推送，remote 里不留 token
BASIC="$(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 | tr -d '\n')"
git -c "http.https://github.com/.extraheader=AUTHORIZATION: basic $BASIC" \
  push -u origin main 2>&1 | sed "s|$GITHUB_TOKEN|***|g"

echo
echo "完成：https://github.com/${LOGIN}/${REPO_NAME}"
echo
echo "后续（可选）——进入 skill 生态："
echo "  1. 仓库加 topic：claude-skills, agent-skills, llm, prompt-engineering, chinese"
echo "  2. 向上游清单提 PR：awesome-claude-code / awesome-agent-skills / skills.sh"
echo "  3. 在 README 顶部加一张 demo 截图或 GIF，收录率会明显提高"
