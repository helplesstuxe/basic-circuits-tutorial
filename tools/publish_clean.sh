#!/usr/bin/env bash
# 从「已推送的提交」发布网页版：在干净的 git worktree 里运行 tools/publish_site.sh，工作目录里未提交的稿件不会上网。
# 用法（在仓库根目录）：PY=/workspace/venv/bin/python bash tools/publish_clean.sh [提交或分支，默认 origin/main]
#   WT=/tmp/bct-publish  worktree 位置（默认 /tmp/bct-publish；已存在会先删掉再建）
# 步骤：git fetch → 在 $WT 检出（detached）指定提交 → 在 $WT 里运行 publish_site.sh（构建、check_site_links、推 gh-pages）→ 删除 $WT。
# 先把要发布的内容 commit 并 push 到 origin main，再运行本脚本。
set -euo pipefail
PY=${PY:-python3}
REF=${1:-origin/main}
WT=${WT:-/tmp/bct-publish}
git fetch -q origin
if [ "$REF" = origin/main ] && [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
  echo "提示：本地 HEAD $(git rev-parse --short HEAD) 与 origin/main $(git rev-parse --short origin/main) 不同；发布的是 origin/main。" >&2
fi
git worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
git worktree prune
git worktree add -q --detach "$WT" "$REF"
trap 'git worktree remove --force "$WT" 2>/dev/null || true' EXIT
echo "在干净 worktree $WT 发布 $(git -C "$WT" log --oneline -1)"
( cd "$WT" && PY="$PY" bash tools/publish_site.sh )
