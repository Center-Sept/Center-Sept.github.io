#!/usr/bin/env python3
r"""legacy-recopy.py —— 把 legacy-site 分支的 15 篇旧文产物 HTML 回抄成 hexo 源（博客 P0 §五 · P1 回执 B1/C8/C9）

输入：git show legacy-site:<perm>index.html（perm 逐行来自 tools/legacy-manifest.tsv 第一列）
输出：source/_posts/<name>.md（name = perm 末段，一字不改 ⇒ permalink 与旧站相同）
用法：python3 tools/legacy-recopy.py            全部 15 篇，可重放（覆盖同名 md）
      python3 tools/legacy-recopy.py <name>     只做一篇
验收：python3 tools/check-legacy-code.py（逐块逐行与 HTML 相等 + 无 headerlink / class="line" 残留）

做法（顺序即坑序）：
  1 正文 = <div class="article-content markdown-body"> 之后 → <ul class="post-tags-box"> 之前
    （★不能切到 article-nav：中间还有标签盒，会被 pandoc 转成 `- [#tag](/tags/…)` 挂在文末）
  2 剥标题锚点 <a … class="headerlink" …></a>（C9：hexo 会重新生成，留着就是双锚点）
  3 每个 <figure class="highlight LANG"> 换成占位段 <p>HEXOCODEBLOCKnnnn</p>，代码文本按 <br> 切行 →
    去全部标签 → html.unescape（B1：不能用 <span class="line">(.*?)</span> 非贪婪，行内 token 的内层 </span> 会截断）
    ★class 属性里可能有换行（高级篇 nginx 那块是 `class="\n highlight plaintext"`），正则要 \s*
  4 懒加载图 <img src="" data-src="URL"> 换成占位段（3 处，全在高级篇，OSS 已 404），文首加一条回抄注
  5 pandoc -f html -t gfm --wrap=none
  6 占位段按其缩进塞回 fenced 块（<li> 里的块 pandoc 会缩进；fence 长度 = 内容里最长反引号串 + 1）
  7 frontmatter：title = <title> 首段（折叠空白后按 ` | ` 切）；date = 清单日期 + 00:00:00；categories = 清单第 8 列（回抄后新加，加注）；
    tags = 文中标签链接文本（旧站原名，如 `SpringCloud|docker|vue`，hexo slugize 后与旧 /tags/ URL 相同）
  8 ★「裸段」：作者在正文里写了字面 `<script src=" 替换 <script src="/static/`，旧 hexo 的 marked 把它当
    HTML 块起点、找不到 </script> ⇒ 后面全文（高级篇末三分之一，43 个代码块）原样吐出，只有代码块被
    backtick 过滤器换成了 <figure>；浏览器又把这一段全塞进 <script> 元素 ⇒ 旧站从未显示过它
    （2026-09-20 headless chrome dump-dom 实核）。这一段就是作者的原 markdown：不过 pandoc，直接保留，
    只换代码块、把裸的 `<script` `<img` `<html` 转义成 `\<…`（新 hexo 才不会再犯同一个错），
    并还原 keep 主题懒加载对 `<img src=` 的改写。
"""
import html, json, pathlib, re, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = REPO / 'tools/legacy-manifest.tsv'
POSTS = REPO / 'source/_posts'
CODE_PH = 'HEXOCODEBLOCK%04d'
IMG_PH = 'HEXOIMGPLACEHOLDER%04d'

RE_FIGURE = re.compile(r'<figure class="\s*highlight\s*([\w-]*)\s*"[^>]*>(.*?)</figure>', re.S)
RE_CODE_TD = re.compile(r'<td class="code"><pre>(.*?)</pre>', re.S)
RE_HEADERLINK = re.compile(r'<a [^>]*class="headerlink"[^>]*></a>')
RE_LAZY_IMG = re.compile(r'<img [^>]*data-src="([^"]*)"[^>]*>')
RE_TAG = re.compile(r'<a[^>]*href="/tags/[^"]*"[^>]*>(.*?)</a>', re.S)
RE_LAZY_REWRITE = re.compile(r'<img\s+src=" 替换 <img\s+lazyload\s+src="/images/loading\.svg"\s+data-src="')
PH_LINE = re.compile(r'^([ \t]*)HEXOCODEBLOCK(\d{4})$', re.M)
IMG_LINE = re.compile(r'^([ \t]*)HEXOIMGPLACEHOLDER(\d{4})$', re.M)


def die(msg):
    print(f'✗ {msg}', file=sys.stderr)
    sys.exit(1)


def code_lines(fig_inner):
    m = RE_CODE_TD.search(fig_inner)
    if not m:
        die('figure 里没有 <td class="code">')
    lines = [html.unescape(re.sub(r'<[^>]+>', '', p)) for p in m.group(1).split('<br>')]
    if lines and lines[-1] == '':
        lines.pop()
    return lines


def _description(md_text: str, limit: int = 120) -> str:
    """正文首 limit 字做摘要（P2-4 线 A）。

    去掉代码块、标题、引用、列表符号、图片与链接壳、行内反引号与强调号；
    合并空白后截断。**只读正文、不改正文** —— 摘要是 frontmatter 的派生量。
    """
    out, in_code = [], False
    for line in md_text.split('\n'):
        st = line.strip()
        if st.startswith('```'):
            in_code = not in_code
            continue
        if in_code or not st:
            continue
        if st.startswith(('#', '>', '|', '---', ':::')):
            continue
        st = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', st)
        st = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', st)
        st = re.sub(r'^[-*+]\s+|^\d+\.\s+', '', st)
        st = st.replace('`', '').replace('**', '').replace('\\', '')
        st = st.strip()
        if st:
            out.append(st)
        if sum(len(x) for x in out) >= limit:
            break
    text = re.sub(r'\s+', ' ', ' '.join(out)).strip()
    if not text:
        # 正文几乎全是小标题 + 代码块（实测 4 篇：Docker镜像加速问题 / Jira / Gitlab / CentOS-TAR 装 Mysql）
        # ⇒ 用小标题序列作摘要。是对真实结构的概括，不编造内容。
        heads = [re.sub(r'^#+\s*', '', l).strip() for l in md_text.split('\n')
                 if re.match(r'^#{1,6}\s+\S', l.strip())]
        text = ' · '.join(dict.fromkeys(h for h in heads if h))
    return text[:limit].rstrip() + ('…' if len(text) > limit else '')


def fence_for(lines):
    longest = max((len(m) for l in lines for m in re.findall(r'`+', l)), default=0)
    return '`' * max(3, longest + 1)


def split_raw_tail(body):
    """坑 8：figure 之外若出现 <script，从该行起到末尾是 marked 原样吐出的作者 markdown。返回 (html 段, 裸段或 None)。"""
    nofig = RE_FIGURE.sub(lambda m: ' ' * len(m.group(0)), body)
    i = nofig.find('<script')
    if i < 0:
        return body, None
    i = body.rfind('\n', 0, i) + 1
    raw = body[i:]
    raw = re.sub(r'\s*</div>\s*$', '', raw)
    if '<div' in RE_FIGURE.sub('', raw):
        die('裸段里还有 <div，切点不对')
    return body[:i], raw


def recopy(perm, title_hint, date, category=''):
    name = perm.rstrip('/').split('/')[-1]
    h = subprocess.run(['git', '-C', str(REPO), 'show', f'legacy-site:{perm}index.html'],
                       capture_output=True, text=True, check=True).stdout

    m = re.search(r'<title>(.*?)</title>', h, re.S)
    title = re.sub(r'\s+', ' ', html.unescape(m.group(1))).strip().split(' | ')[0].strip() if m else ''
    if not title or title != title_hint:
        die(f'{name}: <title> 首段 {title!r} ≠ 清单 {title_hint!r}')

    start_tag = '<div class="article-content markdown-body">'
    if h.count(start_tag) != 1:
        die(f'{name}: 正文容器不是恰好一个')
    body = h.split(start_tag, 1)[1]
    end = body.find('<ul class="post-tags-box">')
    if end < 0:
        die(f'{name}: 找不到 <ul class="post-tags-box">，正文终点不明')
    tags = [html.unescape(re.sub(r'\s+', ' ', t)).strip().lstrip('#') for t in RE_TAG.findall(body[end:end + 4000])]
    body = body[:end]

    body, n_hl = RE_HEADERLINK.subn('', body)
    body, raw = split_raw_tail(body)

    blocks = []
    def take_code(mo):
        blocks.append((mo.group(1), code_lines(mo.group(2))))
        return f'<p>{CODE_PH % len(blocks)}</p>'
    body = RE_FIGURE.sub(take_code, body)
    if '<figure' in body:
        die(f'{name}: 还有未识别的 <figure>')

    imgs = []
    def take_img(mo):
        imgs.append(mo.group(1))
        return f'<p>{IMG_PH % len(imgs)}</p>'
    body = RE_LAZY_IMG.sub(take_img, body)

    md = subprocess.run(['pandoc', '-f', 'html', '-t', 'gfm', '--wrap=none'],
                        input=body, capture_output=True, text=True, check=True).stdout

    n_raw = 0
    if raw is not None:
        raw, n_lazy = RE_LAZY_REWRITE.subn('<img src=" 替换 <img src="', raw)
        def take_code_raw(mo):
            blocks.append((mo.group(1), code_lines(mo.group(2))))
            return f'\n{CODE_PH % len(blocks)}\n'
        raw = RE_FIGURE.sub(take_code_raw, raw)
        n_raw = len(blocks) - md.count('HEXOCODEBLOCK')
        raw, n_esc = re.subn(r'<(?=[A-Za-z/])', r'\<', raw)
        if re.search(r'(?<!\\)<[A-Za-z/]', raw):
            die(f'{name}: 裸段里还有未转义的标签')
        md = md.rstrip('\n') + '\n\n' + raw.strip('\n') + '\n'
        print(f'  ★ {name}: 裸段 {len(raw)} 字符，代码块 {n_raw}，转义标签 {n_esc}，还原懒加载改写 {n_lazy}（旧站从未显示这一段）')

    def put_code(mo):
        indent, idx = mo.group(1), int(mo.group(2)) - 1
        lang, lines = blocks[idx]
        fence = fence_for(lines)
        out = [f'{indent}{fence}{lang}'] + [f'{indent}{l}' if l else '' for l in lines] + [f'{indent}{fence}']
        return '\n'.join(out)
    md, n_code = PH_LINE.subn(put_code, md)
    if n_code != len(blocks):
        die(f'{name}: 代码块塞回 {n_code} ≠ 抽出 {len(blocks)}（占位符被 pandoc 改了形）')

    def put_img(mo):
        return f'{mo.group(1)}> （图：原 OSS 链接已失效，原地址 `{imgs[int(mo.group(2)) - 1]}`）'
    md, n_img = IMG_LINE.subn(put_img, md)
    if n_img != len(imgs):
        die(f'{name}: 图片占位 {n_img} ≠ {len(imgs)}')
    if imgs:
        md = (f'> （回抄注：原文 {len(imgs)} 处图片托管于阿里云 OSS，2026-09-19 实测已 404，图已永久丢失；'
              f'各处原地址留在原位。）\n\n') + md

    # P2-4 线 A（2026-09-23）：description = 正文首 120 字（去代码块/标题/引用/列表符号/链接壳），
    # 只进 frontmatter，不改正文。消费者：butterfly 卡片摘要 + og:description + sitemap/feed。
    desc = _description(md)
    fm = ['---', f'title: {json.dumps(title, ensure_ascii=False)}', f'date: {date} 00:00:00', 'tags:']
    fm += [f'  - {json.dumps(t, ensure_ascii=False)}' for t in tags]
    if category:
        # 分类为 2026-09 回抄后新加，原文无（P1 回执 §九 P2-2：可填一层分类并加注，是归档不是编造）
        fm += ['categories:', f'  - {json.dumps(category, ensure_ascii=False)}  # 分类为 2026-09 回抄后新加，原文无']
    else:
        fm += ['categories: []']
    if desc:
        fm.append(f'description: {json.dumps(desc, ensure_ascii=False)}')
    fm += ['---']
    out = POSTS / f'{name}.md'
    out.write_text('\n'.join(fm) + '\n' + md.rstrip('\n') + '\n', encoding='utf-8')
    print(f'  ✓ {name}: 代码块 {len(blocks)}（{sum(len(l) for _, l in blocks)} 行）· 剥锚 {n_hl} · 图 {len(imgs)} · tags {tags}')


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    n = 0
    for line in MANIFEST.read_text(encoding='utf-8').splitlines():
        if line.startswith('#') or not line.strip():
            continue
        cols = line.split('\t'); perm, title, date = cols[:3]; category = cols[7] if len(cols) > 7 else ''
        if only and perm.rstrip('/').split('/')[-1] != only:
            continue
        recopy(perm, title, date, category)
        n += 1
    if not only and n != 15:
        die(f'清单不是 15 篇：{n}')


if __name__ == '__main__':
    main()
