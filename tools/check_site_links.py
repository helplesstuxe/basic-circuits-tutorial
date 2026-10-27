#!/usr/bin/env python3
"""检查 tools/build_site.py 生成的站点：内链、图片、#锚点是否都存在；指向 GitHub 本仓库 blob/tree 的链接对应的文件是否存在；
正文（去掉公式、代码）里是否还残留原始的 $。
用法：python tools/check_site_links.py [_site]   退出码 0 = 0 坏链且无残留 $。"""
import html, os, re, sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "_site"))
# 只认本仓库的 blob/tree 链接（build_site.py 把非 .md 的仓库内链接改写成这种形式）；别人仓库的 GitHub 链接按外链处理
REPO = os.environ.get("GITHUB_REPOSITORY", "helplesstuxe/basic-circuits-tutorial")
REPO_PREFIX = re.compile(r"^https://github\.com/" + re.escape(REPO) + r"/(blob|tree)/[^/]+/(.*)$")


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.text, self.skip = [], set(), [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "a" and a.get("name"): self.ids.add(a["name"])
        for k in ("href", "src"):
            if a.get(k) is not None and tag in ("a", "img", "link", "script", "source"):
                self.links.append((tag, a[k]))
        cls = a.get("class", "") or ""
        if self.skip or tag in ("code", "pre", "script", "style") or "math" in cls.split():
            self.skip += 1

    def handle_endtag(self, tag):
        if self.skip: self.skip -= 1

    def handle_data(self, d):
        if not self.skip: self.text.append(d)


pages = {}
for dp, _, fns in os.walk(SITE):
    for f in fns:
        if f.endswith(".html"):
            full = os.path.join(dp, f)
            p = P(); p.feed(open(full, encoding="utf-8").read()); p.close()
            pages[os.path.normpath(full)] = p

bad, ext, nint, nimg, dollars = [], 0, 0, 0, []
for full, p in sorted(pages.items()):
    rel = os.path.relpath(full, SITE)
    for tag, url in p.links:
        u = urlsplit(url)
        m = REPO_PREFIX.match(url)
        if m:
            path = unquote(m.group(2).split("#")[0])
            if not os.path.exists(os.path.join(ROOT, path)):
                bad.append(f"{rel}: repo link to missing {path}")
            ext += 1; continue
        if u.scheme or url.startswith("//") or url.startswith("mailto:"):
            ext += 1; continue
        target = full if not u.path else os.path.normpath(os.path.join(os.path.dirname(full), unquote(u.path)))
        if tag == "img": nimg += 1
        else: nint += 1
        if not os.path.isfile(target):
            bad.append(f"{rel}: {tag} -> {url} (file missing)"); continue
        if u.fragment:
            frag = unquote(u.fragment)
            tp = pages.get(target)
            if tp is None or frag not in tp.ids:
                bad.append(f"{rel}: {tag} -> {url} (anchor missing)")
    for line in "".join(p.text).split("\n"):
        if "$" in line:
            dollars.append(f"{rel}: {line.strip()[:100]}")

print(f"pages={len(pages)} internal_links={nint} images={nimg} external={ext} broken={len(bad)} raw_dollar_lines={len(dollars)}")
for b in bad: print("BROKEN", b)
for d in dollars: print("DOLLAR", d)
sys.exit(1 if bad or dollars else 0)
