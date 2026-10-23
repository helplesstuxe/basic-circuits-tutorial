#!/usr/bin/env python3
"""检查 Markdown 里的公式在 GitHub 网页上能否渲染（用 GitHub 自己的 markdown API）。

对每个 .md：
  1. 统计源文件中的公式（行内 $…$、单行/多行 $$…$$、```math 代码块），跳过普通代码块、行内代码、\\$、HTML 标签内的 $；
  2. 调用 `gh api markdown -f mode=gfm -f context=<repo> -F text=@file` 渲染，数 <math-renderer> 元素，
     并把每个公式的内容与源文件逐个对照（多出/缺少的列出来）；
  3. 去掉 <math-renderer>/<code>/<pre> 与标签后，检查正文里是否还残留 `$`、`\\begin`、`\\frac` 等 TeX 痕迹。
  --fix：先在公式内部做等价改写再检查：< > → \\lt \\gt；* → \\ast；\\, \\! \\; \\: \\{ \\} \\| \\& → \\thinspace 等字母命令；
         表格行里的 |…| → \\lvert…\\rvert；结尾的 \\% 移到公式外；矩阵换行 \\\\ → \\cr；\\& → {\\And}；
         段落中的 $$…$$ 两侧补空格。
（复制自上一个教程项目，规则见 notes/AUTHOR_GUIDE.md「GitHub 公式规则」。仓库默认取当前目录的 gh 仓库，
本仓库即 helplesstuxe/basic-circuits-tutorial。）
用法：python tools/check_github_math.py [--fix] [--json] [--repo owner/name] [--cache DIR] file.md|dir ...（不给参数 = 全仓库 .md）
退出码：0 = 全部通过；1 = 至少一个文件 FAIL。
"""
import html, os, re, subprocess, sys, json, hashlib
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = re.compile(r"\\(begin|end|frac|dfrac|tfrac|sqrt|sum|prod|int|left|right|cdot|times|le|ge|leq|geq|approx|"
                 r"alpha|beta|gamma|delta|Delta|lambda|omega|Omega|pi|theta|phi|psi|tau|sigma|mu|text|operatorname|"
                 r"lvert|rvert|lVert|rVert|mathrm|mathbf|dots|ldots|cdots|infty|to|pm|sin|cos|log|ln|exp)(?![A-Za-z])")


def norm(s):
    return re.sub(r"\s+", "", s)


HTML_TAGS = ("details|summary|br|img|span|sub|sup|a|b|i|em|strong|kbd|div|p|figure|figcaption|table|thead|tbody|"
             "tr|td|th|u|small|code|pre|ul|ol|li|hr|audio|video|source|picture|center|font|dl|dt|dd|ins|del|s|mark|q")
TAG = re.compile(r"</?(?:" + HTML_TAGS + r")(?![A-Za-z0-9_])[^<>]*>|<!--.*?-->")


def dollar_positions(line):
    """行内可作为公式分隔符的单个 $ 的下标（跳过 \\x 转义、行内代码、真正的 HTML 标签；$$ 不算）。"""
    pos, i, n = [], 0, len(line)
    while i < n:
        c = line[i]
        if c == "\\":
            i += 2; continue
        if c == "`":
            j = i
            while j < n and line[j] == "`": j += 1
            k = line.find(line[i:j], j)
            if k != -1:
                i = k + (j - i); continue
            i = j; continue
        if c == "<":
            m = TAG.match(line, i)
            if m:
                i = m.end(); continue
        if c == "$":
            if i + 1 < n and line[i + 1] == "$":
                i += 2; continue
            pos.append(i)
        i += 1
    return pos


def spans(text):
    """返回公式列表 dict(kind, line, start, end, cstart, cend)：start/end 为整段（含定界符）在 text 中的偏移，
    cstart/cend 为内容偏移。kind: inline | display | mathblock | bad。"""
    out, fence, disp = [], None, None
    off = 0
    lines = text.split("\n")
    starts = []
    for line in lines:
        starts.append(off); off += len(line) + 1
    for ln, line in enumerate(lines, 1):
        base = starts[ln - 1]
        s = line.lstrip(); ind = len(line) - len(s)
        if fence:
            ch, mark, is_math, fstart, cst = fence
            if s.startswith(mark) and s.strip().strip(ch) == "":
                if is_math:
                    out.append(dict(kind="mathblock", line=fstart_ln, start=fstart, end=base + len(line),
                                    cstart=cst, cend=max(cst, base - 1)))
                fence = None
            continue
        m = re.match(r"(`{3,}|~{3,})\s*([\w+-]*)", s)
        if m:
            fence = (m.group(1)[0], m.group(1), m.group(2) == "math", base + ind, base + len(line) + 1)
            fstart_ln = ln
            continue
        if disp:
            k = line.find("$$")
            if k != -1:
                d0, dl, c0 = disp
                out.append(dict(kind="display", line=dl, start=d0, end=base + k + 2, cstart=c0, cend=base + k))
                disp = None
                rest_from = k + 2
            else:
                continue
        else:
            rest_from = 0
        seg = line[rest_from:]
        # 行内代码、图片 alt 文字里的 $ 不是公式（GitHub 也不渲染）：先遮掉
        seg = re.sub(r"(`+)(.+?)\1", lambda m: " " * len(m.group(0)), seg)
        seg = re.sub(r"!\[(?:[^\[\]]|\[[^\[\]]*\])*\]", lambda m: " " * len(m.group(0)), seg)
        # 行内 $$…$$（可能多个，也可能开了一个跨行的）
        masked = list(seg)
        i = 0
        while True:
            a = seg.find("$$", i)
            if a == -1 or (a > 0 and seg[a - 1] == "\\"):
                if a == -1: break
                i = a + 2; continue
            b = seg.find("$$", a + 2)
            if b == -1:
                disp = (base + rest_from + a, ln, base + rest_from + a + 2)
                for j in range(a, len(seg)): masked[j] = " "
                break
            out.append(dict(kind="display", line=ln, start=base + rest_from + a, end=base + rest_from + b + 2,
                            cstart=base + rest_from + a + 2, cend=base + rest_from + b))
            for j in range(a, b + 2): masked[j] = " "
            i = b + 2
        mseg = "".join(masked)
        pos = dollar_positions(mseg)
        if len(pos) % 2:
            out.append(dict(kind="bad", line=ln, start=base, end=base, cstart=base, cend=base,
                            msg="odd $ count: " + line.strip()[:70]))
            pos = pos[:-1]
        for a, b in zip(pos[::2], pos[1::2]):
            out.append(dict(kind="inline", line=ln, start=base + rest_from + a, end=base + rest_from + b + 1,
                            cstart=base + rest_from + a + 1, cend=base + rest_from + b))
    out.sort(key=lambda d: d["start"])
    return out


def source_formulas(text):
    out = []
    for d in spans(text):
        if d["kind"] == "bad":
            out.append((d["line"], "?", d["msg"]))
        else:
            c = text[d["cstart"]:d["cend"]]
            if d["kind"] == "inline" and len(c) > 1 and c[0] == "`" and c[-1] == "`":
                c = c[1:-1]  # $`…`$ 写法
            out.append((d["line"], d["kind"], c))
    return out


def render(path, repo, cache):
    data = open(path, "rb").read()
    key = hashlib.sha1(repo.encode() + data).hexdigest()
    cf = os.path.join(cache, key + ".html") if cache else None
    if cf and os.path.exists(cf):
        return open(cf, encoding="utf-8").read()
    r = subprocess.run(["gh", "api", "markdown", "-f", "mode=gfm", "-f", f"context={repo}", "-F", f"text=@{path}"],
                       capture_output=True, text=True, check=True)
    if cf:
        os.makedirs(cache, exist_ok=True); open(cf, "w", encoding="utf-8").write(r.stdout)
    return r.stdout


MR = re.compile(r'<math-renderer class="js-(inline|display)-math"[^>]*>(.*?)</math-renderer>', re.S)


def rendered_formulas(h):
    out = []
    for kind, body in MR.findall(h):
        b = html.unescape(re.sub(r"<[^>]+>", "", body))
        m = re.fullmatch(r"(\$+)(.*?)(\$+)", b, re.S)  # 段落中的 $$…$$ 会被标成 inline，内容仍带 $$
        if m:
            b = m.group(2)
        out.append((kind, b))
    return out


def residue(h):
    t = MR.sub(" ", h)
    t = re.sub(r"<pre\b.*?</pre>", " ", t, flags=re.S)
    t = re.sub(r"<code\b.*?</code>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    hits = []
    for i, line in enumerate(t.split("\n")):
        for m in re.finditer(r"(?<!\\)\$|" + TEX.pattern, line):
            hits.append(line.strip()[:120]); break
    return hits


def check(path, repo, cache):
    text = open(path, encoding="utf-8").read()
    src = source_formulas(text)
    bad_src = [f"L{ln}: {c}" for ln, k, c in src if k == "?"]
    src = [(ln, k, c) for ln, k, c in src if k != "?"]
    h = render(path, repo, cache)
    ren = rendered_formulas(h)
    sc = Counter(norm(c) for _, _, c in src)
    rc = Counter(norm(c) for _, c in ren)
    missing = sc - rc
    extra = rc - sc
    miss_lines = []
    for ln, k, c in src:
        if missing[norm(c)] > 0:
            missing[norm(c)] -= 1; miss_lines.append(f"L{ln} {k}: {c[:80]!r}")
    res = residue(h)
    ok = not (bad_src or miss_lines or extra or res)
    return ok, len(src), len(ren), bad_src, miss_lines, list(extra.elements()), res



# ---------------------------------------------------------------- --fix
# GitHub 会先按 Markdown 处理 $…$ / $$…$$ 里的内容：吃掉 "\\标点" 的反斜杠、把 < > 转义两次、把 *…* 当强调、
# 在表格行里把 | 当分隔符。下面把这些写法换成 KaTeX 与 MathJax 都认识、含义完全相同的字母命令。
ESC = {",": r"\thinspace", "!": r"\negthinspace", ";": r"\thickspace", ":": r"\medspace",
       "{": r"\lbrace", "}": r"\rbrace", "|": r"\Vert", "&": r"{\And}", "\\": r"\cr"}


def tokens(s):
    i, n = 0, len(s)
    while i < n:
        if s[i] == "\\" and i + 1 < n:
            if s[i + 1].isalpha():
                j = i + 1
                while j < n and s[j].isalpha(): j += 1
                yield s[i:j]; i = j
            else:
                yield s[i:i + 2]; i += 2
        else:
            yield s[i]; i += 1


def fix_content(s, in_table, problems, where):
    toks = list(tokens(s))
    # 表格行：|…| 配对成 \lvert…\rvert
    if in_table:
        bars = [k for k, t in enumerate(toks) if t == "|"]
        for idx, k in enumerate(bars):
            prev = toks[k - 1] if k else ""
            if prev == r"\left": toks[k] = r"\lvert"
            elif prev == r"\right": toks[k] = r"\rvert"
            elif len(bars) % 2 == 0: toks[k] = r"\lvert" if idx % 2 == 0 else r"\rvert"
            else: toks[k] = r"\vert"
    out = []
    for k, t in enumerate(toks):
        if t == "<": t = r"\lt"
        elif t == ">": t = r"\gt"
        elif t == "*": t = r"\ast"
        elif len(t) == 2 and t[0] == "\\" and t[1] in ESC: t = ESC[t[1]]
        elif len(t) == 2 and t[0] == "\\" and not t[1].isalnum() and t[1] not in " ":
            problems.append(f"{where}: escape {t!r} left as is")
        out.append(t)
    # 控制词后面紧跟字母时补一个空格
    res = ""
    for t in out:
        if res and re.search(r"\\[A-Za-z]+$", res) and t[:1].isalpha():
            res += " "
        res += t
    return res


def fix_text(text, problems, name):
    edits = []
    for d in spans(text):
        if d["kind"] in ("bad", "mathblock"):
            if d["kind"] == "bad": problems.append(f"{name}:{d['line']}: {d['msg']}")
            continue
        c = text[d["cstart"]:d["cend"]]
        ls = text.rfind("\n", 0, d["start"]) + 1
        le = text.find("\n", d["end"]); le = len(text) if le == -1 else le
        line = text[ls:le]
        in_table = line.lstrip().startswith("|")
        where = f"{name}:{d['line']}"
        if d["kind"] == "display" and d["line"] == text.count("\n", 0, d["end"]) + 1:
            # 段落中的单行 $$…$$：两侧要有空格 GitHub 才认
            pre = text[d["start"] - 1] if d["start"] > ls else " "
            post = text[d["end"]] if d["end"] < le else " "
            nc = fix_content(c, in_table, problems, where)
            new = (" " if not pre.isspace() else "") + "$$" + nc + "$$" + (" " if not post.isspace() else "")
            if new != text[d["start"]:d["end"]]:
                edits.append((d["start"], d["end"], new))
            continue
        if d["kind"] == "inline" and c.endswith(r"\%"):
            nc = fix_content(c[:-2], in_table, problems, where)
            edits.append((d["start"], d["end"], "$" + nc + "$%"))
            continue
        nc = fix_content(c, in_table, problems, where)
        if nc != c:
            edits.append((d["cstart"], d["cend"], nc))
    for a, b, s in sorted(edits, reverse=True):
        text = text[:a] + s + text[b:]
    # 含 \begin 的整行 $$…$$ 必须自成段落（前后空行），否则 GitHub 不渲染
    lines, out, nblank = text.split("\n"), [], 0
    for i, line in enumerate(lines):
        m = re.match(r"^((?:\s*>)*\s*)\$\$(.*)\$\$\s*$", line)
        if m and "\\begin" in m.group(2) and "$$" not in m.group(2):
            pre = m.group(1).rstrip(" ")
            blank = lambda l: l.strip().strip(">").strip() == ""
            if out and not blank(out[-1]):
                out.append(pre); nblank += 1
            if pre[:1].isspace():  # 列表项里 GitHub 不渲染含 \\begin 的公式，$`…`$ 又会把 & 双重转义：只能手改结构
                problems.append(f"{name}:{i + 1}: 列表项里的 \\begin 公式 GitHub 不渲染，需把它移出列表")
                out.append(line)
            else:
                out.append(line)
            if i + 1 < len(lines) and not blank(lines[i + 1]):
                out.append(pre); nblank += 1
            continue
        out.append(line)
    return "\n".join(out), len(edits) + nblank


def main():
    args = sys.argv[1:]
    repo, cache = None, None
    if "--repo" in args:
        i = args.index("--repo"); repo = args[i + 1]; del args[i:i + 2]
    if "--cache" in args:
        i = args.index("--cache"); cache = args[i + 1]; del args[i:i + 2]
    as_json = "--json" in args
    do_fix = "--fix" in args
    args = [a for a in args if a not in ("--json", "--fix")]
    if not repo:
        repo = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
                              capture_output=True, text=True, cwd=ROOT).stdout.strip()
    if not args:
        args = [ROOT]
    files = []
    for a in args:
        if os.path.isdir(a):
            for d, ds, fs in os.walk(a):
                ds[:] = sorted(x for x in ds if not x.startswith(".") and x != "node_modules")
                files += [os.path.join(d, f) for f in sorted(fs) if f.endswith(".md")]
        else:
            files.append(a)
    if do_fix:
        for f in files:
            probs = []
            old = open(f, encoding="utf-8").read()
            new, k = fix_text(old, probs, os.path.relpath(f, ROOT))
            if k:
                open(f, "w", encoding="utf-8").write(new)
            print(f"fixed {k:3d}  {os.path.relpath(f, ROOT)}")
            for x in probs: print("      " + x)
    nfail, report = 0, {}
    for f in files:
        ok, ns, nr, bad_src, miss, extra, res = check(f, repo, cache)
        rel = os.path.relpath(f, ROOT)
        report[rel] = dict(ok=ok, src=ns, rendered=nr, unparsed=bad_src, missing=miss, extra=extra, residue=res)
        nfail += not ok
        if as_json:
            continue
        print(f"{'OK  ' if ok else 'FAIL'} src={ns:4d} github={nr:4d}  {rel}")
        for x in bad_src: print(f"      source: {x}")
        for x in miss: print(f"      not rendered: {x}")
        for x in extra: print(f"      unexpected math: {x[:80]!r}")
        for x in res: print(f"      raw TeX in text: {x}")
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    print(f"{len(files) - nfail}/{len(files)} files OK", file=sys.stderr)
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
