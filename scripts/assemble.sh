#!/bin/bash
# 拼接 assets/templates/html-head.html + AI生成的body内容 + assets/templates/html-tail.html → 最终输出 HTML
# 用法: bash scripts/assemble.sh <body-content-file> <output-file>
# 示例: bash scripts/assemble.sh /tmp/body.html /path/to/outputs/packing-list.html

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TPL_DIR="$SKILL_DIR/assets/templates"
BODY_FILE="${1:-}"
OUTPUT_FILE="${2:-}"

if [ -z "$BODY_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
  echo "用法: bash scripts/assemble.sh <body-content-file> <output-file>"
  exit 1
fi

if [ ! -f "$BODY_FILE" ]; then
  echo "错误: body 内容文件不存在: $BODY_FILE"
  exit 1
fi

if [ ! -f "$TPL_DIR/html-head.html" ] || [ ! -f "$TPL_DIR/html-tail.html" ]; then
  echo "错误: 模板文件缺失，检查 $TPL_DIR/html-head.html 和 $TPL_DIR/html-tail.html"
  exit 1
fi

cat "$TPL_DIR/html-head.html" "$BODY_FILE" "$TPL_DIR/html-tail.html" > "$OUTPUT_FILE"
echo "✓ 已生成: $OUTPUT_FILE ($(wc -l < "$OUTPUT_FILE") 行)"
