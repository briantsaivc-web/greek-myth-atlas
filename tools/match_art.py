#!/usr/bin/env python3
"""由兩個大全集（art-history-atlas / sculpture-atlas）的 works.json 建立 data/artworks.json
比對規則：題名（英文 t 與中文 z）出現人物的英文名／羅馬名／中文譯名（整字比對），或主題含「神話／寓言」且題名含關鍵詞。
只收有本地圖檔者。輸出欄位帶兩站的絕對 URL，圖直接引用原站。
"""
import json,re,sys,collections
PA='/home/claude/art-history-atlas/'; SC='/home/claude/sculpture-atlas/'
URL={'p':'https://briantsaivc-web.github.io/art-history-atlas/','s':'https://briantsaivc-web.github.io/sculpture-atlas/'}
NAMES=json.load(open('/home/claude/greek-myth-atlas/tools/names.json',encoding='utf-8'))
# NAMES: {char_id: {"en":[...], "zh":[...]}}
pat={}
for cid,v in NAMES.items():
    en=[re.escape(x) for x in v.get('en',[])]; zh=[re.escape(x) for x in v.get('zh',[])]
    pe=re.compile(r'(?<![A-Za-z])(?:'+'|'.join(en)+r')(?![a-z])',re.I) if en else None
    pz=re.compile('|'.join(zh)) if zh else None
    pat[cid]=(pe,pz)
AMB={'artemis','helen','paris','io','pan','eros','echo','atlas','minos','hebe','ajax','hector','jason','medusa','sirens','muses','graces','eos','selene','nymphs','phaedra'}
def match(t,z):
    out=[]
    port=re.search(r'portrait|self-portrait|bust of (?:a|an|the)\b',t,re.I)
    for cid,(pe,pz) in pat.items():
        if cid in AMB and port: continue
        if (pe and pe.search(t)) or (pz and z and pz.search(z)): out.append(cid)
    return out
out=[]; stat=collections.Counter()
for site,root in [('p',PA),('s',SC)]:
    W=json.load(open(root+'data/works.json',encoding='utf-8')); A=json.load(open(root+'data/artists.json',encoding='utf-8'))
    for w in W:
        if not w.get('img'): continue
        chars=match(w['t'],w.get('z',''))
        myth='神話／寓言' in w.get('th',[])
        if not chars and not myth: continue
        rec={'id':f"{site}:{w['id']}",'site':site,'wid':w['id'],'a':w['a'],'a_zh':A.get(w['a'],{}).get('zh',''),'t':w['t'],'z':w.get('z',''),'y':w.get('y',''),
             'mu':w.get('mu',''),'img':URL[site]+w['img'],'thumb':URL[site]+(w.get('thumb') or w['img']),'chars':chars,'myth_theme':myth,
             'mat':w.get('mat'),'src_url':w.get('src_url'),'wd_flag':bool(w.get('wd_flag'))}
        out.append(rec); stat[site]+=1; stat[site+'_named']+=bool(chars)
json.dump(out,open('/home/claude/greek-myth-atlas/data/artworks.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
cc=collections.Counter(c for r in out for c in r['chars'])
print(dict(stat)); print(cc.most_common(40)); print('chars with 0 works:',[c for c in NAMES if cc[c]==0])
