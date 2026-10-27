#!/usr/bin/env bash
# 重新生成网页版并发布到 gh-pages 分支（GitHub Pages 来源：gh-pages /）。
# 用法：在仓库根目录运行 bash tools/publish_site.sh（需要 markdown-it-py mdit-py-plugins linkify-it-py）
#
# 注意：build_site.py 是从「当前工作目录的文件」构建的（os.walk 整个仓库，包括未提交、未跟踪的 .md 和图片），
# 不是从已提交的内容构建。工作目录里有未审稿件时，请改用 bash tools/publish_clean.sh：
# 它在一个干净的 git worktree（默认检出 origin/main）里调用本脚本。
# 本脚本发现工作目录不干净（有未提交改动或未跟踪文件）时拒绝发布；确实要发布当前工作目录，设 ALLOW_DIRTY=1。
set -euo pipefail
PY=${PY:-python3}
if [ -n "$(git status --porcelain --untracked-files=normal)" ] && [ "${ALLOW_DIRTY:-0}" != 1 ]; then
  echo "工作目录有未提交或未跟踪的文件，网页会把它们一起发上去。请用 bash tools/publish_clean.sh（或设 ALLOW_DIRTY=1 强制）。" >&2
  git status --short | head -20 >&2
  exit 2
fi
rev=$(git rev-parse --short HEAD)
rm -rf _site && $PY tools/build_site.py --out _site && $PY tools/check_site_links.py _site
touch _site/.nojekyll
wt=$(mktemp -d); git fetch -q origin gh-pages; git worktree add -q -B gh-pages "$wt" origin/gh-pages
find "$wt" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -r _site/. "$wt"/
git -C "$wt" add -A && (git -C "$wt" commit -qm "site: 由 main $rev 生成" && git -C "$wt" push -q origin gh-pages || echo "网页无变化")
git worktree remove --force "$wt"
