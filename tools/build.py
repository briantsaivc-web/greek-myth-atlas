#!/usr/bin/env python3
"""合併 Sonnet 產出 → data/stories.json、data/characters.json、data/relations.json、data/meta.json；為每篇故事配對藝術作品。"""
import json,glob,re,datetime,collections
V='/home/claude/myth/work/'; R='/home/claude/greek-myth-atlas/'
L=lambda p:json.load(open(p,encoding='utf-8'))
SL=L(V+'STORY_LIST.json'); CH=L(V+'out/characters.json'); ART=L(R+'data/artworks.json')
order=[s[0] for s in SL['stories']]
ST={}
for f in sorted(glob.glob(V+'out/stories_part*.json')): ST.update(L(f))
missing=[i for i in order if i not in ST]; print('stories',len(ST),'missing',missing)
stories=[]
for sid in order:
    if sid not in ST: continue
    s=ST[sid]; s['id']=sid
    s['chars']=[c for c in s.get('chars',[]) if c in CH]
    # artwork matching: score = #shared chars (weighted) + keyword hits
    kws=[k for k in s.get('keywords_en',[]) if len(k)>2]
    kp=re.compile(r'(?<![A-Za-z])(?:'+'|'.join(re.escape(k) for k in kws)+r')(?![a-z])',re.I) if kws else None
    main=set(s['chars'][:3]); allc=set(s['chars'])
    scored=[]
    for a in ART:
        ac=set(a['chars']); sc=0
        sc+=3*len(ac&main)+1.5*len(ac&(allc-main))
        if kp and kp.search(a['t']): sc+=2
        if ac and not (ac&allc): sc-=2   # 明確屬於別人的作品
        if a['wd_flag']: sc-=0.5
        if sc>=3: scored.append((sc,a['id']))
    scored.sort(key=lambda x:-x[0]); s['art']=[i for _,i in scored[:24]]
    n=sum(len(p) for x in s['sections'] for p in x['p'])+len(s.get('ending',''))
    s['chars_count']=n
    stories.append(s)
# relations from characters
REL=[]; seen=set()
def add(a,b,k):
    key=(min(a,b),max(a,b),k) if k in('配偶','手足','情人') else (a,b,k)
    if key in seen or a not in CH or b not in CH or a==b: return
    seen.add(key); REL.append({'s':a,'t':b,'k':k})
for cid,c in CH.items():
    for p in c.get('parents') or []: add(p,cid,'父母')
    for p in c.get('children') or []: add(cid,p,'父母')
    for p in c.get('spouses') or []: add(cid,p,'配偶')
    for p in c.get('lovers') or []: add(cid,p,'情人')
    for p in c.get('siblings') or []: add(cid,p,'手足')
    for p in c.get('killed') or []: add(cid,p,'殺害')
    for p in c.get('killed_by') or []: add(p,cid,'殺害')
    for p in c.get('mentor_of') or []: add(cid,p,'師徒')
    t=c.get('transformed')
    if t and t.get('by'): add(t['by'],cid,'變形')
for c in CH.values(): c.setdefault('id',None)
for cid,c in CH.items(): c['id']=cid
colors={'creation':'#8e7cc3','olympians':'#d2a85a','love':'#e0a0b0','heroes':'#c96b5c','troy':'#7a9cc9','return':'#6ea39a'}
en={'creation':'Creation & the Titans','olympians':'The Olympians','love':'Love & Metamorphoses','heroes':'Heroes','troy':'The Trojan War','return':'The Odyssey & Homecomings'}
desc={'creation':'從混沌、大地與天空，到泰坦與宙斯的世代之爭，以及普羅米修斯與潘朵拉。','olympians':'奧林帕斯山上的神祇各有性情與故事：四季的由來、月桂樹、織布比賽、點金術。','love':'奧維德《變形記》裡最動人的篇章：愛、追逐、失去，以及化作花草星辰的結局。','heroes':'柏修斯、海克力斯、翟修斯、傑森、伊底帕斯——凡人與半神的冒險與試煉。','troy':'一顆金蘋果引發的十年戰爭：阿基里斯、赫克托耳、海倫與木馬。','return':'奧德修斯漂泊十年的歸鄉路，以及埃涅阿斯航向義大利的旅程。'}
cycles=[{**c,'color':colors[c['id']],'en':en[c['id']],'desc':desc[c['id']],'count':sum(1 for s in stories if s['cycle']==c['id'])} for c in SL['cycles']]
meta={'version':'v1','updated':datetime.date.today().isoformat(),'cycles':cycles,'counts':{'stories':len(stories),'characters':len(CH),'artworks':len(ART),'relations':len(REL)},
      'notes':[f'v1（{datetime.date.today().isoformat()}）：72 則故事由 Sonnet 子代理依原典改寫為兒童睡前版本；人物資料與關係由子代理整理；插圖以人物名／關鍵字自動比對兩個大全集的作品題名，可能有誤配。']}
json.dump(stories,open(R+'data/stories.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
json.dump(CH,open(R+'data/characters.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
json.dump(REL,open(R+'data/relations.json','w',encoding='utf-8'),ensure_ascii=False)
json.dump(meta,open(R+'data/meta.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('relations',len(REL),collections.Counter(r['k'] for r in REL))
print('stories with 0 art',[s['id'] for s in stories if not s['art']],'avg art',sum(len(s['art']) for s in stories)/max(1,len(stories)))
print('chars/story avg len',sum(s['chars_count'] for s in stories)//max(1,len(stories)))
