#!/usr/bin/env bash
# check-legacy-urls.sh —— 博客 P0 派② 验收：15 个旧 permalink 逐个 200 且 <title> 首段 = 清单标题
#
#   tools/check-legacy-urls.sh [BASE]          默认 BASE=https://blogs.center-sept.top（线上）
#   tools/check-legacy-urls.sh file://$PWD/public   本地产物（hexo generate 之后）
#
# ★ 比标题不只比 200：旧站 5 篇标题≠文件名（空格/下划线 vs 连字符），从 URL 反推会漏；
#   N6：故意改清单一个标题必红 —— 证明比的是标题。
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="${1:-https://blogs.center-sept.top}"
MANIFEST="${MANIFEST:-$HERE/legacy-manifest.tsv}"
n=0; bad=0
fetch() {  # fetch <url> → 打印 "<code>\t<title首段>"
    local u="$1" f code
    case "$u" in
        file://*) f="${u#file://}/index.html"; [ -f "$f" ] && code=200 || code=404 ;;
        *) f="$(mktemp)"; code="$(curl -s -m 20 -o "$f" -w '%{http_code}' "$u")" ;;
    esac
    local t=""
    [ "$code" = 200 ] && t="$(python3 - "$f" <<'PY'
import re,html,sys
t=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
m=re.search(r'<title>\s*(.*?)\s*</title>',t,re.S); print(re.sub(r'\s+',' ',html.unescape(m.group(1))).split(' | ')[0].strip() if m else '')
PY
)"
    case "$u" in file://*) ;; *) rm -f "$f";; esac
    printf '%s\t%s\n' "$code" "$t"
}
while IFS=$'\t' read -r perm title _; do
    case "$perm" in \#*|'') continue;; esac
    n=$((n+1))
    url="$BASE/$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$perm")"
    [ "${BASE#file://}" != "$BASE" ] && url="$BASE/$perm"
    IFS=$'\t' read -r code got < <(fetch "$url")
    if [ "$code" = 200 ] && [ "$got" = "$title" ]; then echo "  ✓ $perm  «$title»"
    else bad=$((bad+1)); echo "  ✗ $perm  HTTP $code  期望 «$title» 实得 «$got»" >&2; fi
done < "$MANIFEST"
echo "$((n-bad))/$n 通过（$BASE）"
[ "$n" -eq 15 ] || { echo "✗ 清单不是 15 篇：$n" >&2; exit 2; }
[ "$bad" -eq 0 ]
