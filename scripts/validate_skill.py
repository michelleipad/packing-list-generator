#!/usr/bin/env python3
"""
packing-list-generator skill 验证脚本
用于校验 skill 文件完整性、模板结构正确性和规则文件一致性。
运行方式：python3 scripts/validate_skill.py
"""

import os
import re
import sys
import json

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_FILES = [
    'SKILL.md',
    'references/packing-rules.md',
    'assets/templates/html-template.html',
    'assets/templates/body-skeleton.html',
    'references/multi-city-file-branch.md',
]

CHECKS = []


def check(name, passed, detail=''):
    status = 'PASS' if passed else 'FAIL'
    CHECKS.append((name, status, detail))
    icon = '✅' if passed else '❌'
    msg = f"  {icon} [{status}] {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return passed


def validate_files_exist():
    """校验所有必需文件是否存在"""
    all_ok = True
    for f in REQUIRED_FILES:
        path = os.path.join(SKILL_DIR, f)
        exists = os.path.isfile(path)
        if not check(f"文件存在: {f}", exists):
            all_ok = False
    return all_ok


def validate_skill_md_structure():
    """校验 SKILL.md 包含必要章节"""
    path = os.path.join(SKILL_DIR, 'SKILL.md')
    if not os.path.isfile(path):
        return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_sections = [
        ('触发边界', '## 触发边界（快速校验）'),
        ('输入采集流程', '## 输入采集流程'),
        ('天气数据获取', '## 天气数据获取'),
        ('清单生成逻辑', '## 清单生成逻辑'),
        ('HTML 输出规范', '## HTML 输出规范'),
        ('错误处理', '## 错误处理'),
        ('输出检查清单', '## 输出检查清单'),
    ]
    all_ok = True
    for name, marker in required_sections:
        found = marker in content
        if not check(f"SKILL.md 章节: {name}", found):
            all_ok = False
    return all_ok


def validate_html_template():
    """校验 HTML 模板包含必要结构"""
    path = os.path.join(SKILL_DIR, 'assets', 'templates', 'html-template.html')
    if not os.path.isfile(path):
        return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_elements = [
        ('viewport meta', '<meta name="viewport"'),
        ('print media query', '@media print'),
        ('category-card 模板', 'category-card'),
        ('pre-departure 区块', 'pre-departure'),
        ('daily-outfit 区块', 'daily-outfit'),
        ('info-card 区块', 'info-card'),
        ('action-bar 操作栏', 'action-bar'),
        ('filter 筛选功能', 'setFilter'),
        ('localStorage 持久化', 'localStorage'),
        ('setupAddItemRows 函数', 'setupAddItemRows'),
        ('exportAsImage 函数', 'exportAsImage'),
        ('copyAsText 函数', 'copyAsText'),
        ('approx-notice 近似日期横幅', 'approx-notice'),
        ('approx-days-notice 天数近似横幅', 'approx-days-notice'),
        ('item-approx-hint 件数估算小字', 'item-approx-hint'),
    ]
    all_ok = True
    for name, marker in required_elements:
        found = marker in content
        if not check(f"HTML 模板: {name}", found):
            all_ok = False

    # 校验无硬编码 add-item-row（应在 JS 中动态注入）
    # 允许 CSS 中的 .add-item-row 定义，但不允许在 HTML body 中出现 <div class="add-item-row">
    body_match = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
    if body_match:
        body = body_match.group(1)
        has_hardcoded = '<div class="add-item-row">' in body or "class='add-item-row'" in body
        check("HTML 无硬编码 add-item-row", not has_hardcoded,
              "add-item-row 必须由 JS setupAddItemRows() 动态注入" if has_hardcoded else "")
        if has_hardcoded:
            all_ok = False

    return all_ok


def validate_packing_rules():
    """校验 packing-rules.md 包含必要分类"""
    path = os.path.join(SKILL_DIR, 'references', 'packing-rules.md')
    if not os.path.isfile(path):
        return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_sections = [
        ('基础分类结构', '## 1. 基础分类结构'),
        ('紧急联系区块', '## 2. 紧急联系'),
        ('按天穿搭逻辑', '## 3. 按天穿搭'),
    ]
    all_ok = True
    for name, marker in required_sections:
        found = marker in content
        if not check(f"packing-rules.md: {name}", found):
            all_ok = False
    return all_ok


def validate_no_external_deps_in_html():
    """校验 HTML 模板无外部 CSS/JS 依赖（html2canvas CDN 除外，已有降级方案）"""
    path = os.path.join(SKILL_DIR, 'assets', 'templates', 'html-template.html')
    if not os.path.isfile(path):
        return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 <head> 中是否有外部 CSS/JS link/script（排除 html2canvas 动态加载）
    head_match = re.search(r'<head>(.*?)</head>', content, re.DOTALL)
    if head_match:
        head = head_match.group(1)
        external_css = re.findall(r'<link[^>]+href=["\']https?://', head)
        external_js = re.findall(r'<script[^>]+src=["\']https?://(?!.*html2canvas)', head)
        has_external = len(external_css) > 0 or len(external_js) > 0
        check("HTML <head> 无外部依赖", not has_external,
              f"发现 {len(external_css)} 个外部CSS / {len(external_js)} 个外部JS" if has_external else "")
        if has_external:
            return False
    return True


def validate_frontmatter():
    """校验 SKILL.md frontmatter 包含必要字段"""
    path = os.path.join(SKILL_DIR, 'SKILL.md')
    if not os.path.isfile(path):
        return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        check("SKILL.md frontmatter 存在", False, "缺少 --- 包裹的 frontmatter")
        return False

    fm = fm_match.group(1)
    required_fields = ['name:', 'description:', 'version:', 'allowed-tools:']
    all_ok = True
    for field in required_fields:
        found = field in fm
        if not check(f"frontmatter 字段: {field.rstrip(':')}", found):
            all_ok = False
    return all_ok


def validate_body_skeleton_action_bar():
    """校验 body 骨架文件含完整 action-bar 契约，且 SKILL.md 保留指针与硬契约警示。

    骨架已从 SKILL.md 外置到 assets/templates/body-skeleton.html（渐进式披露合规），
    因此 HTML 结构标记在骨架文件里检查；SKILL.md 只校验：① 引用了骨架文件 ② 保留硬契约警示语。
    """
    skill_path = os.path.join(SKILL_DIR, 'SKILL.md')
    skeleton_path = os.path.join(SKILL_DIR, 'assets/templates/body-skeleton.html')
    if not os.path.isfile(skill_path) or not os.path.isfile(skeleton_path):
        return False
    with open(skill_path, 'r', encoding='utf-8') as f:
        skill_content = f.read()
    with open(skeleton_path, 'r', encoding='utf-8') as f:
        skeleton_content = f.read()

    # 骨架文件必须包含的 HTML/JS 契约标记
    skeleton_contract_markers = [
        ('div.action-bar 容器', 'class="action-bar"'),
        ('action-left 左栏', 'class="action-left"'),
        ('action-right 右栏', 'class="action-right"'),
        ('filter-group 胶囊组', 'class="filter-group"'),
        ('filter-btn active 初始态', 'class="filter-btn active"'),
        ('data-filter=all', 'data-filter="all"'),
        ('data-filter=packed', 'data-filter="packed"'),
        ('data-filter=unpacked', 'data-filter="unpacked"'),
        ('progress-label id', 'id="progress-label"'),
        ('progress-percent id', 'id="progress-percent"'),
        ('count-all id', 'id="count-all"'),
        ('count-packed id', 'id="count-packed"'),
        ('count-unpacked id', 'id="count-unpacked"'),
        ('setFilter(all) 绑定', "setFilter('all')"),
        ('setFilter(packed) 绑定', "setFilter('packed')"),
        ('setFilter(unpacked) 绑定', "setFilter('unpacked')"),
        ('btn-secondary 灰底按钮', 'class="btn btn-secondary"'),
        ('resetProgress 绑定', 'resetProgress()'),
        ('exportAsImage 绑定', 'exportAsImage()'),
        ('copyAsText 绑定', 'copyAsText()'),
    ]
    # SKILL.md 必须保留的指针与警示
    skill_pointer_markers = [
        ('body 骨架外置指针', 'assets/templates/body-skeleton.html'),
        ('硬契约警示语', 'class 名与元素结构是硬契约'),
    ]
    all_ok = True
    for name, marker in skeleton_contract_markers:
        found = marker in skeleton_content
        if not check(f"body-skeleton.html action-bar 契约: {name}", found,
                     "body-skeleton.html 骨架缺失或被削弱，会导致 AI 生成的底部 bar 失样式/失交互" if not found else ""):
            all_ok = False
    for name, marker in skill_pointer_markers:
        found = marker in skill_content
        if not check(f"SKILL.md 骨架指针: {name}", found,
                     "SKILL.md 未引用外置骨架文件或缺硬契约警示，AI 可能忽略骨架规范" if not found else ""):
            all_ok = False
    return all_ok


def main():
    print("=" * 60)
    print("packing-list-generator skill 验证报告")
    print("=" * 60)
    print(f"Skill 目录: {SKILL_DIR}\n")

    results = {}

    print("[1/7] 文件完整性校验")
    results['files'] = validate_files_exist()
    print()

    print("[2/7] SKILL.md 结构校验")
    results['skill_structure'] = validate_skill_md_structure()
    print()

    print("[3/7] HTML 模板结构校验")
    results['html_template'] = validate_html_template()
    print()

    print("[4/7] packing-rules.md 校验")
    results['packing_rules'] = validate_packing_rules()
    print()

    print("[5/7] 外部依赖校验")
    results['no_external_deps'] = validate_no_external_deps_in_html()
    print()

    print("[6/7] Frontmatter 校验")
    results['frontmatter'] = validate_frontmatter()
    print()

    print("[7/7] SKILL.md body 骨架 action-bar 契约校验")
    results['body_skeleton'] = validate_body_skeleton_action_bar()
    print()

    # 汇总
    total = len(CHECKS)
    passed = sum(1 for _, s, _ in CHECKS if s == 'PASS')
    failed = total - passed

    print("=" * 60)
    print(f"验证结果: {passed}/{total} 通过, {failed} 失败")
    if failed > 0:
        print("⚠️  存在未通过的校验项，请修复后重新验证。")
    else:
        print("✅ 所有校验项通过！")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
