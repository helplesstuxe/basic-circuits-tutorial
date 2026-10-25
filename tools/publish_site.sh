#!/usr/bin/env bash
# 重新生成网页版并发布到 gh-pages 分支（GitHub Pages 来源：gh-pages /）。
# 用法：在仓库根目录运行 bash tools/publish_site.sh（需要 markdown-it-py mdit-py-plugins linkify-it-py）
set -euo pipefail
PY=${PY:-python3}
rev=$(git rev-parse --short HEAD)
rm -rf _site && $PY tools/build_site.py --out _site && $PY tools/check_site_links.py _site
touch _site/.nojekyll
wt=$(mktemp -d); git fetch -q origin gh-pages; git worktree add -q "$wt" gh-pages
find "$wt" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -r _site/. "$wt"/
git -C "$wt" add -A && (git -C "$wt" commit -qm "site: 由 main $rev 生成" && git -C "$wt" push -q origin gh-pages || echo "网页无变化")
git worktree remove --force "$wt"
