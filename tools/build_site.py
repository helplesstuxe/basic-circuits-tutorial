#!/usr/bin/env python3
"""把仓库里的 Markdown 教程生成静态网站（GitHub Pages 用）。

用法：python tools/build_site.py [--out _site] [--repo owner/name] [--branch main]

做法：
  * 公式定位直接复用 tools/check_github_math.py 的 spans()（它与 GitHub 的渲染逐页对过数），
    先把每个 $…$ / $$…$$ 换成纯字母数字占位符，再交给 markdown-it-py（CommonMark + 表格 + 删除线 + 脚注 +
    允许 HTML）渲染，最后把占位符换回 \\( … \\) / \\[ … \\]（HTML 转义后）交给 MathJax 3。
    这样 Markdown 的 _ * \\ 转义、表格的 | 都碰不到公式内容。
  * 内链 .md → .html（保留 #锚点），README.md → index.html；指向目录的链接 → 该目录 page1.html；
    指向代码、SPICE 等非 Markdown 非图片文件的链接 → GitHub 上的 blob 页面。
  * 标题 id 按 GitHub（github-slugger）规则生成：小写、去掉标点符号、空格变 -、重复加 -1/-2，中文保留。
  * GitHub 提示框 > [!NOTE] / [!TIP] / [!IMPORTANT] / [!WARNING] / [!CAUTION] 转成带标题的提示框。
  * 复制仓库中所有图片。
  * 每页顶栏有「☰ 目录」折叠面板（原生 <details>，少量 CSS/JS，无外部库）：列出仓库里所有 NN-slug/ 节点目录
    （有 page1.md 的才算，按编号排；30 起归第二部分），每节可展开看 page1–4（用各页 H1 里「 · 」后的篇名），
    当前节自动展开、当前页高亮；点按钮或面板外收起。新增节点目录不用改本脚本。
只依赖 markdown-it-py、mdit-py-plugins（linkify-it-py 可选）。
"""
import argparse, html, os, posixpath, re, shutil, subprocess, sys, unicodedata
from urllib.parse import unquote, quote

from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_github_math import spans  # noqa: E402

SKIP_DIRS = {".git", ".github", "_site", "node_modules", "__pycache__", ".venv", "venv"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
ALERTS = {"NOTE": "说明", "TIP": "提示", "IMPORTANT": "重要", "WARNING": "警告", "CAUTION": "注意"}
PH = re.compile(r"MJXPH(\d+)Z")

CSS = r"""
:root{--fg:#1f2328;--muted:#59636e;--bg:#fff;--line:#d1d9e0;--soft:#f6f8fa;--link:#0969da}
@media (prefers-color-scheme:dark){:root{--fg:#e6edf3;--muted:#9198a1;--bg:#0d1117;--line:#3d444d;--soft:#151b23;--link:#4493f8}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.75 system-ui,-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC","Source Han Sans SC",sans-serif;word-wrap:break-word}
.topbar{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line);font-size:14px}
.topbar>div{max-width:820px;margin:0 auto;padding:8px 16px;display:flex;gap:16px;justify-content:space-between}
main{max-width:820px;margin:0 auto;padding:12px 16px 48px}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
h1,h2,h3,h4{line-height:1.35;margin:1.6em 0 .6em}h1{font-size:1.6em;margin-top:.6em}h2{font-size:1.35em;border-bottom:1px solid var(--line);padding-bottom:.25em}h3{font-size:1.15em}
img{max-width:100%;height:auto;display:block;margin:8px auto;background:#fff}
p img{display:inline-block}
table{display:block;max-width:100%;overflow-x:auto;border-collapse:collapse;margin:1em 0;font-size:.95em}
th,td{border:1px solid var(--line);padding:6px 10px;vertical-align:top}th{background:var(--soft)}
pre{background:var(--soft);padding:12px;border-radius:6px;overflow-x:auto;font-size:13.5px;line-height:1.5}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-size:.9em}
:not(pre)>code{background:var(--soft);padding:.1em .35em;border-radius:4px}
blockquote{margin:1em 0;padding:.2em 1em;color:var(--muted);border-left:4px solid var(--line)}
blockquote.alert{color:var(--fg)}blockquote.alert::before{display:block;font-weight:600;margin-top:.4em}
blockquote.alert-note{border-color:#0969da}blockquote.alert-note::before{content:"ⓘ 说明";color:#0969da}
blockquote.alert-tip{border-color:#1a7f37}blockquote.alert-tip::before{content:"💡 提示";color:#1a7f37}
blockquote.alert-important{border-color:#8250df}blockquote.alert-important::before{content:"❗ 重要";color:#8250df}
blockquote.alert-warning{border-color:#9a6700}blockquote.alert-warning::before{content:"⚠ 警告";color:#9a6700}
blockquote.alert-caution{border-color:#d1242f}blockquote.alert-caution::before{content:"⛔ 注意";color:#d1242f}
details{border:1px solid var(--line);border-radius:6px;padding:.3em .9em;margin:1em 0;background:var(--soft)}
summary{cursor:pointer;font-weight:600}
hr{border:0;border-top:1px solid var(--line);margin:2em 0}
.math-display{overflow-x:auto;overflow-y:hidden;margin:.8em 0;padding:2px 0}
mjx-container[display="true"]{overflow-x:auto;overflow-y:hidden;max-width:100%;padding:2px 0}
mjx-container{max-width:100%}
.topbar .bar{position:relative;align-items:center}
.navpanel{margin:0;padding:0;border:0;background:none;border-radius:0}
.navpanel>summary{list-style:none;display:inline-block;padding:4px 12px;border:1px solid var(--line);border-radius:6px;background:var(--soft);font-weight:600;user-select:none;-webkit-user-select:none}
.navpanel>summary::-webkit-details-marker{display:none}
.navpanel[open]>summary{background:var(--link);color:#fff;border-color:var(--link)}
.navbox{position:absolute;left:8px;right:8px;top:calc(100% + 2px);max-width:440px;max-height:calc(100vh - 130px);max-height:calc(100dvh - 130px);overflow-y:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;background:var(--bg);border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.18);padding:8px 10px 12px;z-index:20;font-size:15px;line-height:1.5}
.navbox .navhome{display:block;padding:8px 6px;font-weight:600;border-bottom:1px solid var(--line);margin-bottom:4px}
.navbox .navpart{margin:10px 6px 4px;font-size:13px;color:var(--muted);font-weight:600}
.navbox details{margin:0;padding:0;border:0;border-radius:0;background:none}
.navbox details>summary{font-weight:400;padding:7px 6px;border-radius:6px}
.navbox details>summary:hover{background:var(--soft)}
.navbox details.cur>summary{font-weight:600;color:var(--link)}
.navbox ol{list-style:none;margin:0 0 4px;padding:0 0 0 22px}
.navbox ol a{display:block;padding:6px 8px;border-radius:6px;color:var(--fg)}
.navbox ol a:hover{background:var(--soft);text-decoration:none}
.navbox ol a[aria-current="page"]{background:var(--link);color:#fff;font-weight:600}
@media (min-width:860px){.navbox{left:16px;right:auto;width:420px}}
.footer{max-width:820px;margin:0 auto;padding:16px;color:var(--muted);font-size:13px;border-top:1px solid var(--line)}
"""

MATHJAX = r"""<script>
window.MathJax={tex:{inlineMath:[['\\(','\\)']],displayMath:[['\\[','\\]']],processEscapes:false,
packages:{'[+]':['ams']}},
options:{ignoreHtmlClass:'tex2jax_ignore',processHtmlClass:'math'},
chtml:{matchFontHeight:false},startup:{typeset:true}};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script>"""

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
{mathjax}
</head>
<body class="tex2jax_ignore">
<nav class="topbar"><div class="bar"><details class="navpanel" id="navpanel"><summary aria-label="展开/收起目录">☰ 目录</summary><div class="navbox">{navmenu}</div></details><a href="{src}">GitHub 源文件</a></div></nav>
<main>
{body}
</main>
<div class="footer"><a href="{index}">返回目录</a> · 由 tools/build_site.py 从仓库 Markdown 生成</div>
{navjs}
</body>
</html>
"""

NAVJS = r"""<script>
(function(){var d=document.getElementById('navpanel');if(!d)return;
function shut(){d.removeAttribute('open');}
document.addEventListener('click',function(e){if(d.open&&!d.contains(e.target)){e.preventDefault();e.stopPropagation();shut();}},true);
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&d.open)shut();});
d.addEventListener('toggle',function(){if(!d.open)return;var c=d.querySelector('[aria-current="page"]')||d.querySelector('details.cur');
if(c){var b=d.querySelector('.navbox');b.scrollTop=Math.max(0,c.offsetTop-b.clientHeight/3);}});})();
</script>"""
NODE_DIR = re.compile(r"^(\d\d)-[A-Za-z0-9-]+$")
PART2_FROM = 30   # 第二部分从 30 节起（设计见 notes/00-design-part2.md）


def h1_of(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                return line[2:].strip()
    return ""


def nav_nodes():
    """[(编号, 目录名, 节名, [(页文件 rel, 篇名), ...]), ...]，按编号排；有 page1.md 的 NN-slug 目录才算。"""
    res = []
    for d in sorted(os.listdir(ROOT)):
        m = NODE_DIR.match(d)
        if not m or not os.path.isfile(os.path.join(ROOT, d, "page1.md")):
            continue
        pages, name = [], ""
        for k in range(1, 10):
            f = os.path.join(ROOT, d, f"page{k}.md")
            if not os.path.isfile(f):
                break
            t = h1_of(f)
            t = re.sub(r"^\d\d\s*", "", t)
            node, _, part = t.partition(" · ")
            name = name or node.strip()
            pages.append((f"{d}/page{k}.md", part.strip() or f"page{k}"))
        res.append((m.group(1), d, name or d, pages))
    return res


def nav_html(nodes, cur_rel, cur_out):
    e = html.escape
    out = [f'<a class="navhome" href="{e(relurl("index.html", cur_out))}">🏠 首页 / README（总目录）</a>']
    part = None
    for num, d, name, pages in nodes:
        p = 2 if int(num) >= PART2_FROM else 1
        if p != part:
            part = p
            out.append('<div class="navpart">' + ("第一部分" if p == 1 else "第二部分") + "</div>")
        cur = any(rel == cur_rel for rel, _ in pages)
        items = []
        for k, (rel, t) in enumerate(pages, 1):
            ac = ' aria-current="page"' if rel == cur_rel else ""
            items.append(f'<li><a href="{e(quote(relurl(out_name(rel), cur_out)))}"{ac}>page{k} · {e(t)}</a></li>')
        attr = ' class="cur" open' if cur else ""
        out.append(f'<details{attr}><summary>{num} {e(name)}</summary><ol>{"".join(items)}</ol></details>')
    return "".join(out)


def slugify(text):
    """github-slugger：小写，去掉标点/符号，空格变 -。"""
    out = []
    for ch in text.lower():
        if ch in "-_":
            out.append(ch)
        elif ch == " ":
            out.append("-")
        elif unicodedata.category(ch)[0] in "LNM":
            out.append(ch)
    return "".join(out)


def md_files():
    res = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
        for f in sorted(fns):
            if f.endswith(".md"):
                res.append(os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/"))
    return res


def out_name(rel):
    if rel == "README.md":
        return "index.html"
    return rel[:-3] + ".html"


def relurl(target, cur_out):
    return posixpath.relpath(target, posixpath.dirname(cur_out) or ".")


class Builder:
    def __init__(self, out, repo, branch):
        self.out, self.repo, self.branch = out, repo, branch
        self.problems = []
        self.nmath = 0
        md = MarkdownIt("commonmark", {"html": True, "linkify": False, "typographer": False})
        md.enable(["table", "strikethrough"])
        try:
            import linkify_it  # noqa: F401
            md.options["linkify"] = True
            md.enable("linkify")
        except ImportError:
            pass
        md.use(footnote_plugin)

        def render_image(renderer, tokens, idx, options, env):  # 图片可点开看原图（手机上放大用）
            t = tokens[idx]
            alt = renderer.renderInlineAsText(t.children or [], options, env)
            attrs = "".join(f' {k}="{html.escape(str(v))}"' for k, v in t.attrs.items() if k != "alt")
            tag = f'<img alt="{html.escape(alt)}"{attrs} />'
            return f'<a class="img-link" href="{html.escape(t.attrGet("src") or "")}">{tag}</a>'
        md.add_render_rule("image", render_image)
        self.md = md

    def blob(self, rel, kind="blob"):
        return f"https://github.com/{self.repo}/{kind}/{self.branch}/" + quote(rel)

    def fix_link(self, href, cur_rel, cur_out):
        if not href or href.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href) or href.startswith("//"):
            return href
        path, frag = (href.split("#", 1) + [None])[:2]
        if not path:
            return href
        tgt = posixpath.normpath(posixpath.join(posixpath.dirname(cur_rel), unquote(path)))
        full = os.path.join(ROOT, tgt)
        suffix = ("#" + frag) if frag is not None else ""
        if tgt.startswith(".."):
            self.problems.append(f"{cur_rel}: link outside repo {href}")
            return href
        if os.path.isdir(full):
            if tgt == ".":
                return relurl("index.html", cur_out) + suffix
            if os.path.exists(os.path.join(full, "page1.md")):
                return quote(relurl(tgt + "/page1.html", cur_out)) + suffix
            if os.path.exists(os.path.join(full, "README.md")):
                return quote(relurl(tgt + "/README.html", cur_out)) + suffix
            return self.blob(tgt, "tree") + suffix
        if not os.path.exists(full):
            self.problems.append(f"{cur_rel}: missing target {href}")
            return href
        if tgt.endswith(".md"):
            return quote(relurl(out_name(tgt), cur_out)) + suffix
        if os.path.splitext(tgt)[1].lower() in IMG_EXT:
            return quote(relurl(tgt, cur_out)) + suffix
        return self.blob(tgt) + suffix

    def build_one(self, rel):
        text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        formulas = []
        pieces, last = [], 0
        for d in spans(text):
            if d["kind"] == "bad":
                self.problems.append(f"{rel}:{d['line']}: {d['msg']}")
                continue
            c = text[d["cstart"]:d["cend"]]
            if d["kind"] == "inline" and len(c) > 1 and c[0] == "`" and c[-1] == "`":
                c = c[1:-1]
            pieces.append(text[last:d["start"]])
            pieces.append(f"MJXPH{len(formulas)}Z")
            formulas.append((d["kind"], c.strip()))
            last = d["end"]
        pieces.append(text[last:])
        src = "".join(pieces)
        self.nmath += len(formulas)
        cur_out = out_name(rel)

        def plain(m):
            return formulas[int(m.group(1))][1]

        env = {}
        tokens = self.md.parse(src, env)
        used = {}
        title = None
        for i, t in enumerate(tokens):
            if t.type == "heading_open":
                inl = tokens[i + 1]
                txt = "".join(c.content for c in (inl.children or []) if c.type in ("text", "code_inline"))
                txt = PH.sub(plain, txt)
                if title is None and t.tag == "h1":
                    title = txt
                s = slugify(txt)
                if s in used:
                    used[s] += 1
                    s2 = f"{s}-{used[s]}"
                    while s2 in used:
                        used[s] += 1; s2 = f"{s}-{used[s]}"
                    used[s2] = 0
                    s = s2
                else:
                    used[s] = 0
                t.attrSet("id", s)
            elif t.type == "blockquote_open" and i + 2 < len(tokens) and tokens[i + 1].type == "paragraph_open":
                inl = tokens[i + 2]
                ch = inl.children or []
                if ch and ch[0].type == "text":
                    m = re.match(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", ch[0].content)
                    if m:
                        t.attrSet("class", "alert alert-" + m.group(1).lower())
                        del ch[0]
                        if ch and ch[0].type in ("softbreak", "hardbreak"):
                            del ch[0]
                        if not ch:  # [!NOTE] 单独成段
                            tokens[i + 1].hidden = tokens[i + 3].hidden = True
            if t.children:
                for c in t.children:
                    if c.type == "link_open":
                        c.attrSet("href", self.fix_link(c.attrGet("href"), rel, cur_out))
                    elif c.type == "image":
                        c.attrSet("src", self.fix_link(c.attrGet("src"), rel, cur_out))
                        c.attrSet("loading", "lazy")
        body = self.md.renderer.render(tokens, self.md.options, env)

        def math_html(i, inline_ctx):
            kind, c = formulas[i]
            e = html.escape(c, quote=False)
            if kind == "inline":
                return f'<span class="math math-inline">\\({e}\\)</span>'
            if inline_ctx:
                return f'<span class="math math-display">\\[{e}\\]</span>'
            return f'<div class="math math-display">\\[{e}\\]</div>'

        body = re.sub(r"<p>\s*MJXPH(\d+)Z\s*</p>", lambda m: math_html(int(m.group(1)), False)
                      if formulas[int(m.group(1))][0] != "inline" else "<p>" + math_html(int(m.group(1)), True) + "</p>", body)
        body = PH.sub(lambda m: math_html(int(m.group(1)), True), body)
        if PH.search(body):
            self.problems.append(f"{rel}: placeholder left")
        page = PAGE.format(title=html.escape(title or rel), css=CSS, mathjax=MATHJAX if formulas else "",
                           index=relurl("index.html", cur_out), src=self.blob(rel), body=body,
                           navmenu=nav_html(self.nodes, rel, cur_out), navjs=NAVJS)
        dst = os.path.join(self.out, cur_out)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "w", encoding="utf-8").write(page)

    def run(self):
        if os.path.exists(self.out):
            shutil.rmtree(self.out)
        os.makedirs(self.out)
        files = md_files()
        self.nodes = nav_nodes()
        for rel in files:
            self.build_one(rel)
        nimg = 0
        for dp, dns, fns in os.walk(ROOT):
            dns[:] = [d for d in dns if d not in SKIP_DIRS and os.path.join(dp, d) != os.path.abspath(self.out)]
            for f in fns:
                if os.path.splitext(f)[1].lower() in IMG_EXT:
                    r = os.path.relpath(os.path.join(dp, f), ROOT)
                    os.makedirs(os.path.join(self.out, os.path.dirname(r)), exist_ok=True)
                    shutil.copy2(os.path.join(dp, f), os.path.join(self.out, r)); nimg += 1
        open(os.path.join(self.out, ".nojekyll"), "w").close()
        print(f"pages={len(files)} formulas={self.nmath} images={nimg} -> {self.out}")
        for p in self.problems:
            print("PROBLEM", p)
        return 1 if self.problems else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "_site"))
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "helplesstuxe/basic-circuits-tutorial"))
    ap.add_argument("--branch", default="main")
    a = ap.parse_args()
    sys.exit(Builder(os.path.abspath(a.out), a.repo, a.branch).run())


if __name__ == "__main__":
    main()
