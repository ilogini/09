# -*- coding: utf-8 -*-
import os, glob

dir_path = r'D:\claude\website_plan\pds\2026\토이 프로젝트\withBowwow\design\연주\소스\글라스모피니즘 아이콘\소스1'

color_map = {
    # Purple -> Lime
    '#c3a1f7': '#D4E300', '#a36ff3': '#C5D900',
    '#f2eafd': '#F7FBDA', '#e2d1fb': '#EBF3A6',
    '#efe5fd': '#F7FBDA', '#d8c2fa': '#EBF3A6',
    '#faf7fe': '#FEFEF8', '#e7d9fc': '#EBF3A6',
    '#f5effe': '#FAFDE6', '#fbf9fe': '#FEFEF8',
    '#e5d6fc': '#EBF3A6', '#fdfcff': '#FEFEF8',
    '#e1d1fb': '#EBF3A6', '#e9ddfc': '#EBF3A6',
    '#d6bff9': '#E0EC8C', '#d8c2f9': '#EBF3A6',
    '#ebe0fc': '#F7FBDA',
    # Blue -> Azure
    '#93d4ff': '#33BBFF', '#61c0ff': '#0099FF',
    '#33a6ff': '#0099FF', '#8ea4ff': '#33BBFF',
    '#bbe4ff': '#B3E0FF', '#f3faff': '#F0F9FF',
    '#d4eeff': '#CCE9FF', '#ebf7ff': '#E6F5FF',
    '#d2edff': '#CCE9FF', '#b6e2ff': '#B3E0FF',
    '#def2ff': '#E6F5FF', '#b4e1ff': '#B3E0FF',
    '#f2faff': '#F0F9FF', '#c2e7ff': '#CCE9FF',
    '#dff1ff': '#E6F5FF', '#addcff': '#99D4FF',
    '#dce3ff': '#CCE9FF', '#d9e0ff': '#CCE9FF',
    '#f1f9ff': '#F0F9FF', '#bcc8ff': '#99D4FF',
    '#cae8ff': '#CCE9FF', '#c5e6ff': '#CCE9FF',
    '#b9e1ff': '#B3E0FF', '#a5d8ff': '#99D4FF',
    '#90cfff': '#66CCFF', '#d6ecff': '#CCE9FF',
    '#b1dbff': '#B3E0FF',
    # Gold -> Lime
    '#ffeb86': '#E8F060', '#ffbf5b': '#C5D900',
    '#fffac3': '#FAFDE6', '#ffeab3': '#F7FBDA',
    '#ffeac9': '#F7FBDA', '#fffae1': '#FAFDE6',
    '#ffecbb': '#F7FBDA', '#ffe6ae': '#EBF3A6',
    # Orange -> Lime
    '#ffac72': '#D4E300', '#ff846e': '#C5D900',
    '#fff4ed': '#FAFDE6', '#ffc8be': '#F7FBDA',
    '#ffcdc5': '#F7FBDA', '#fff0e6': '#FAFDE6',
    '#ffd7d0': '#EBF3A6', '#ffc8bf': '#F7FBDA',
    # Pink -> Azure
    '#ffb8e4': '#33BBFF', '#ff86b1': '#0099FF',
    '#fff7fc': '#F0F9FF', '#ffe8ee': '#E6F5FF',
    '#ffb3c6': '#99D4FF', '#fff2fa': '#F0F9FF',
    '#ffccda': '#CCE9FF', '#ffedf2': '#F0F9FF',
    # Green -> Lime
    '#cde377': '#D4E300', '#98d66b': '#C5D900',
    '#e0edab': '#EBF3A6', '#d2edc5': '#EBF3A6',
    '#f8fbec': '#FAFDE6', '#cfedc3': '#EBF3A6',
    '#ffffec': '#FAFDE6', '#dff5ce': '#EBF3A6',
    '#cef1b6': '#E0EC8C',
    # Yellow-Orange -> Lime
    '#ffd85e': '#D4E300', '#ffb365': '#C5D900',
    '#ffca6f': '#D4E300', '#ffb25b': '#C5D900',
    '#fff9e7': '#FAFDE6', '#fff2c3': '#F7FBDA',
    '#ffd794': '#EBF3A6', '#fff4e0': '#FAFDE6',
    '#ffecd7': '#F7FBDA', '#ffdfbf': '#EBF3A6',
    '#ffeca8': '#EBF3A6', '#fffdf5': '#FEFEF8',
    '#fffefc': '#FEFEF8', '#fffdfc': '#FEFEF8',
    '#fffef8': '#FEFEF8', '#fffef9': '#FEFEF8',
}

svg_files = glob.glob(os.path.join(dir_path, '*.svg'))
print(f"Found {len(svg_files)} SVG files")

count = 0
for fp in svg_files:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for old, new in color_map.items():
        content = content.replace(old, new)

    if content != original:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
        print(f"Updated: {os.path.basename(fp)}")

print(f"\nTotal: {count} files updated")
