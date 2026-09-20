#!/usr/bin/env python3
"""check-legacy-code.py —— 15 篇回抄的代码块与 legacy-site HTML 逐块逐行相等（博客 P1 回执 B1 / C9）

用法：python3 tools/check-legacy-code.py            期望末行 `TOTAL blocks 426, code lines 9273, differing lines 0`（回执写 425/9270：其参考实现的正则漏了 class 属性夹换行的那 1 块），退 0
判据（任一不满足退 1，打印第一处差异）：
  ① 每篇 md 的 fenced 块数 == legacy-site HTML 的 <figure class="highlight"> 数
  ② 同序逐块逐行：HTML 行按 <br> 切 → 去全部标签 → html.unescape，与 md 行逐字相等
  ③ md 里无 class="line"（代码表 HTML 逃逸成文本）、无 class="headerlink"（C9：标题锚点残留）
★ 参考实现来自架构师·fuxi 审查线回执 §二 B1（wsl-vault:9d51009）；本线加 ③ 的 headerlink 项。
★ 负对照：修法落地前在旧回抄上跑必须红（2026-09-20 读数 differing 3118 量级）。红过一次，0 才算数。
"""
import re, html, subprocess, sys, pathlib
repo = pathlib.Path(__file__).resolve().parent.parent

def html_blocks(h):
    out = []
    # ★class 属性里可能夹换行（高级篇 nginx 块是 class="\n highlight plaintext"），故 \s*；回执参考实现漏它 1 块
    for fg in re.findall(r'<figure class="\s*highlight.*?</figure>', h, re.S):
        m = re.search(r'<td class="code"><pre>(.*?)</pre>', fg, re.S)
        lines = [html.unescape(re.sub(r'<[^>]+>', '', p)) for p in (m.group(1) if m else '').split('<br>')]
        if lines and lines[-1] == '': lines.pop()
        out.append(lines)
    return out

def md_blocks(md):
    # fenced 块可带缩进（<li> 里的块），fence 可长于 3（内容含反引号串时）；只有同缩进、同长或更长的 fence 才关块
    out, cur, indent, fence = [], None, '', ''
    for l in md.split('\n'):
        m = re.match(r'^([ \t]*)(`{3,})', l)
        if cur is None:
            if m: cur, indent, fence = [], m.group(1), m.group(2)
        elif m and m.group(1) == indent and len(m.group(2)) >= len(fence) and l.strip('` \t') == '':
            out.append(cur); cur = None
        else:
            cur.append(l[len(indent):] if l.startswith(indent) else l)
    return out

tb = tl = bad = 0
for line in (repo / 'tools/legacy-manifest.tsv').read_text(encoding='utf-8').splitlines():
    if line.startswith('#') or not line.strip(): continue
    perm = line.split('\t')[0]; name = perm.rstrip('/').split('/')[-1]
    h = subprocess.run(['git', '-C', str(repo), 'show', f'legacy-site:{perm}index.html'], capture_output=True, text=True, check=True).stdout
    md = (repo / 'source/_posts' / f'{name}.md').read_text(encoding='utf-8')
    hb, mb = html_blocks(h), md_blocks(md)
    if 'class="line"' in md: print(f'✗ {name}: md 里残留代码表 HTML（class="line"）'); bad += 1
    n_hl = md.count('class="headerlink"')
    if n_hl: print(f'✗ {name}: md 里残留 headerlink 锚点 {n_hl} 处（C9）'); bad += 1
    if len(hb) != len(mb): print(f'✗ {name}: 块数 html={len(hb)} md={len(mb)}'); bad += 1
    for i, (a, b) in enumerate(zip(hb, mb)):
        for j in range(max(len(a), len(b))):
            x = a[j] if j < len(a) else None; y = b[j] if j < len(b) else None
            if x != y:
                if bad == 0: print(f'✗ {name} 块 {i} 行 {j}\n  html: {x!r}\n  md  : {y!r}')
                bad += 1
    tb += len(hb); tl += sum(map(len, hb))
print(f'TOTAL blocks {tb}, code lines {tl}, differing lines {bad}')
sys.exit(1 if bad else 0)
