#!/usr/bin/env python3
"""重新為每篇故事配插圖（取代 build.py 內的簡單配對），並統一作品中文題名的人物譯名。
規則：
 - 人物「專屬度」= 出現在幾篇故事的 chars；≤3 篇視為專屬人物（如達芙妮），>3 篇為常見主角（如宙斯、奧德修斯）。
 - 作品入選條件（任一）：
   a) 題名命中故事的場景關鍵字（keywords_en 中非人名者，或專屬人物名）
   b) 與故事共享 ≥2 位人物
   c) 與故事共享 1 位且該人物為專屬人物
 - 排除：作品含有「不在本故事、且專屬於其他故事」的人物（例如木馬篇排除波呂斐摩斯）；黑名單題名（梅杜莎之筏）。
 - 排序：關鍵字命中 > 共享人物數 > 專屬人物；上限 16。
"""
import json,re,collections
R='/home/claude/greek-myth-atlas/'
L=lambda p:json.load(open(p,encoding='utf-8'))
S=L(R+'data/stories.json'); C=L(R+'data/characters.json'); ART=L(R+'data/artworks.json'); N=L(R+'tools/names.json')
BLACK=re.compile(r'(?i)raft of the medusa|medusa\b.*raft|aurora leigh|pan american|diana vreeland')
# 譯名統一：所有 names.json 的 zh 變體 → characters.json 的 zh
v2s={}
for cid,v in N.items():
    std=C.get(cid,{}).get('zh')
    if not std: continue
    for z in v.get('zh',[]):
        if z!=std and len(z)>=2: v2s[z]=std
v2s=dict(sorted(v2s.items(),key=lambda x:-len(x[0])))
def norm_zh(t):
    for a,b in v2s.items():
        if a in t: t=t.replace(a,b)
    return t
for a in ART: a['zn']=norm_zh(a['z']) if a.get('z') else ''
# 專屬度
freq=collections.Counter(c for s in S for c in s['chars'])
specific={c for c,n in freq.items() if n<=3}
charnames=set()
for v in N.values(): charnames.update(x.lower() for x in v.get('en',[]))
stat=collections.Counter(); art_by_id={a['id']:a for a in ART}
for s in S:
    sc=set(s['chars'])
    kws=[k for k in s.get('keywords_en',[]) if len(k)>2 and (k.lower() not in charnames or any(k.lower() in [x.lower() for x in N.get(c,{}).get('en',[])] for c in sc&specific))]
    kp=re.compile(r'(?<![A-Za-z])(?:'+'|'.join(re.escape(k) for k in kws)+r')(?![a-z])',re.I) if kws else None
    scored=[]
    for a in ART:
        if BLACK.search(a['t']): continue
        ac=set(a['chars']); shared=ac&sc
        foreign=(ac-sc)&specific
        if foreign: continue
        kw=bool(kp and (kp.search(a['t']) or (a.get('zn') and any(k in a['zn'] for k in []))))
        ok = kw or len(shared)>=2 or (len(shared)==1 and next(iter(shared)) in specific)
        if not ok: continue
        score=(4 if kw else 0)+2*len(shared)+(1 if shared&specific else 0)-(0.5 if a['wd_flag'] else 0)
        scored.append((score,a['id']))
    scored.sort(key=lambda x:-x[0])
    s['art']=[i for _,i in scored[:16]]
    stat[len(s['art'])>0]+=1
json.dump(S,open(R+'data/stories.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
json.dump(ART,open(R+'data/artworks.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print('stories with art',stat[True],'without',stat[False],'avg',sum(len(s['art']) for s in S)/len(S))
for sid in ['st041','st063','st012','st001','st044']:
    s=next(x for x in S if x['id']==sid); print(sid,s['title'],len(s['art']),[art_by_id[i]['zn'] or art_by_id[i]['t'][:30] for i in s['art'][:8]])
print('zero-art:',[s['id']+s['title'] for s in S if not s['art']])
