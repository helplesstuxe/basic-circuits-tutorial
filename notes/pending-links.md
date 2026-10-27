# 待恢复的链接（指向尚未发布节点的链接）

第二部分（30–45）按批上线。已发布的页面里不能有指向未发布节点的链接（网站上是死链，`check_site_links.py` 也会报 broken）。
所以发布前把这类链接**临时改成纯文字**，原链接记在下表；对应节点上线的那一批，再按下表原样恢复。

## 做法（每批发布都照做）

1. 找死链：本批节点目录一起列出，它们之间的互链不算死链：

   ```bash
   python tools/find_pending_links.py --ref origin/main 30-instrumentation-amp [本批其他节点目录 …]
   ```

   退出码 1 表示有指向未发布节点的链接，逐条列出「文件:行号: 原链接」。
2. 改成纯文字：`[38 同步检波（电磁流量计） · 直觉篇](../38-synchronous-demod/page1.md)` → `38 节同步检波（电磁流量计）（即将上线）`；
   导航里的「下一页」→ `下一页：31 节跨阻放大器（TIA）（即将上线）`。统一用「NN 节…（即将上线）」的写法，方便以后 `rg "即将上线"` 一次找全。
3. 在下表「待恢复」里加一行：文件、改后的行内容（能 rg 到的片段）、原链接（原样 Markdown）。
4. 对应节点上线的那一批：先 `rg "（即将上线）"` 和本表，把属于本批节点的行恢复成原链接，再把这一行移到「已恢复」并写上批次/提交。
   恢复后重新跑 `find_pending_links.py`，应为 pending=0（或只剩更后面节点的）。
5. 本文件和改动一起提交。

## 每批发布的完整流程（第二部分分批上线时）

1. 只改本批节点自己的文件；共享文件（README 目录表与阅读顺序、AUTHOR_GUIDE、上一节 page4 的「下一页」、`code/figs/00_figs.py` 的 DAG、`code/figs/lab_schem.py` 的 NODES、`spice/models/`）由发布者改。
2. 按上面的做法处理死链，登记到本表；把以前登记、这一批上线的节点对应的链接恢复。
3. 检查（全部要过）：`count_cjk`、`run_blocks`（页面）、`run_blocks --scripts`（在副本 worktree 里跑，脚本会重写 img/）、`check_figs`、
   `check_github_math --repo helplesstuxe/basic-circuits-tutorial`、`fix_inline_math_spacing --check`；再在副本里 `build_site.py` + `check_site_links.py`，要 broken=0、raw_dollar_lines=0。
   做法：`git worktree add --detach /tmp/bct-stage HEAD`，把要提交的路径复制进去，在里面跑。
4. 密钥扫描：`git diff --cached` 里 rg `ghp_|gho_|github_pat_|password` 等，有可疑内容就停。
5. 只 `git add` 明确列出的路径（不要 `git add -A`），提交，`git push origin main`。
6. 发布：`PY=/workspace/venv/bin/python bash tools/publish_clean.sh`（在 /tmp/bct-publish 干净检出 origin/main 再构建；
   工作目录里未审的稿件不会上网）。直接运行 `tools/publish_site.sh` 时，工作目录不干净会被拒绝。
   Pages 没重建就 `gh api -X POST repos/helplesstuxe/basic-circuits-tutorial/pages/builds`。
7. 验证：curl 本批每页线上 URL 为 200，上一节 page4 的「下一页」指向本批，首页目录有本批，未发布节点的 URL 为 404。

## 待恢复

| 文件 | 现在的行内容（片段） | 原链接 | 等哪节上线 | 记录批次 |
|---|---|---|---|---|
| `30-instrumentation-amp/page1.md`（第 84 行，图 30-p1-5 说明段） | `再交给后面的滤波和 38 节同步检波（电磁流量计）（即将上线）。下一行，差压流量计…` | `[38 同步检波（电磁流量计） · 直觉篇](../38-synchronous-demod/page1.md)` | 38 | 第 1 批（30） |
| `30-instrumentation-amp/page4.md`（第 3 行，页首导航） | `本页：动手实验篇 · 下一页：31 节跨阻放大器（TIA）（即将上线） · 前置节点：…` | `[下一页：31 跨阻放大器（TIA） · 直觉篇](../31-transimpedance-amp/page1.md)` | 31 | 第 1 批（30） |

## 已恢复

| 文件 | 原链接 | 恢复批次 / 提交 |
|---|---|---|
| （暂无） | | |
