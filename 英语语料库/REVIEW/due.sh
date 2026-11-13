#!/bin/sh
# 列出今天到期（next_recall <= TODAY）的复习单元
# 用法：sh due.sh            → 用系统日期
#       TODAY=2026-11-05 sh due.sh
cd "$(dirname "$0")" || exit 1
today=${TODAY:-$(date +%F)}
echo "TODAY=$today"
awk -F'|' -v t="$today" '
  /^\| *[a-z]+-/ {
    for(i=1;i<=NF;i++){gsub(/^ +| +$/,"",$i)}
    if ($8 != "" && $8 <= t) { printf "%-16s %-8s %s | %s | 到期 %s (%s)\n", $2,$3,$4,$5,$8,$9 }
  }' recall-queue.md
printf "到期总数: "
awk -F'|' -v t="$today" '/^\| *[a-z]+-/ {gsub(/^ +| +$/,"",$8); if($8<=t)c++} END{print c+0}' recall-queue.md
