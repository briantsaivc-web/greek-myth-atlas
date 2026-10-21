#!/usr/bin/env python3
"""資料一致性檢查：執行 python tools/validate.py。"""
import json, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = lambda p: json.load(open(os.path.join(R, 'data', p), encoding='utf-8'))

stories = L('stories.json')
chars = L('characters.json')
relations = L('relations.json')
artworks = L('artworks.json')
meta = L('meta.json')

c_ids = set(chars.keys())
s_ids = {s['id'] for s in stories}
a_ids = {a['id'] for a in artworks}
cycle_ids = {c['id'] for c in meta.get('cycles', [])}

err = []
for s in stories:
    sid = s.get('id', '')
    if not sid:
        err.append('故事缺少 id')
    if s.get('cycle') not in cycle_ids:
        err.append(f'故事 {sid} 所屬 cycle 不存在: {s.get("cycle")}')
    for c in s.get('chars', []):
        if c not in c_ids:
            err.append(f'故事 {sid} 引用未定義人物: {c}')
    for a in s.get('art', []):
        if a not in a_ids:
            err.append(f'故事 {sid} 引用未定義作品: {a}')

for cid, c in chars.items():
    for fld in ['parents', 'children', 'spouses', 'lovers', 'siblings', 'killed', 'killed_by', 'mentor_of']:
        for rel_c in (c.get(fld) or []):
            if rel_c not in c_ids:
                err.append(f'人物 {cid} 的 {fld} 引用未定義人物: {rel_c}')
    for sid in c.get('stories', []):
        if sid not in s_ids:
            err.append(f'人物 {cid} 引用未定義故事: {sid}')

for r in relations:
    if r.get('s') not in c_ids:
        err.append(f'關聯 s 不存在: {r.get("s")}')
    if r.get('t') not in c_ids:
        err.append(f'關聯 t 不存在: {r.get("t")}')

missing_img = 0
for a in artworks:
    if a.get('site') == 'm':
        p = os.path.join(R, a.get('img', ''))
        if not os.path.exists(p):
            missing_img += 1
            if missing_img <= 5:
                err.append(f'本地圖檔不存在: {p}')

print(f"{len(stories)} 故事 / {len(chars)} 人物 / {len(relations)} 關係 / {len(artworks)} 作品")
if missing_img > 0:
    print(f"缺失圖檔: {missing_img} 張")
if err:
    print('\n'.join(err[:50]))
    print(f'共 {len(err)} 個問題')
    sys.exit(1)
print('OK 無問題')
