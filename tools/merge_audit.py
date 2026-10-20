#!/usr/bin/env python3
"""合併 Gemini 稽核（gemini_myth_audit_all.json 或 tab 匯出）：
 rel  → FIX 寫入 characters[id].audit（不自動改關係，列出供人工／第二輪處理）
 story→ FIX 寫入 stories[id].audit
 art  → remove 清單直接從 stories[id].art 移除（兩種來源一致性低，寧可少配一張）
用法：merge_audit.py <audit_json>
"""
import json,re,sys,datetime,shutil,collections
R='/home/claude/greek-myth-atlas/'; today=datetime.date.today().isoformat()
res=json.load(open(sys.argv[1],encoding='utf-8'))
B={b['batch']:b for b in json.load(open(R+'work_gemini_batches.json',encoding='utf-8'))}
S=json.load(open(R+'data/stories.json',encoding='utf-8')); C=json.load(open(R+'data/characters.json',encoding='utf-8'))
for f in ['stories','characters']: shutil.copy(R+f'data/{f}.json',R+f'data/{f}.json.backup.{today}-audit')
byS={s['id']:s for s in S}
def parse(raw):
    raw=re.sub(r'^```(?:json)?\s*|\s*```$','',(raw or '').strip())
    try: return json.loads(raw)
    except Exception:
        m=re.search(r'\[.*\]',raw,re.S); return json.loads(m.group(0)) if m else []
stat=collections.Counter(); relfix=[]; stfix=[]; removed=0
for k,v in res.items():
    b=B.get(int(k));
    if not b: continue
    arr=v.get('parsed') or parse(v.get('raw'))
    for it in arr:
        i=it.get('id')
        if b['kind']=='rel' and i in C:
            stat['rel_'+it.get('verdict','?')]+=1
            if it.get('verdict')=='FIX': C[i]['audit']={'verdict':'FIX','issues':it.get('issues'),'source':it.get('source'),'model':v.get('model'),'grounded':False,'date':today}; relfix.append((i,it.get('issues')))
        elif b['kind']=='story' and i in byS:
            stat['story_'+it.get('verdict','?')]+=1
            if it.get('verdict')=='FIX' or it.get('source_ok') is False: byS[i]['audit']={'verdict':it.get('verdict'),'issues':it.get('issues'),'source_ok':it.get('source_ok'),'model':v.get('model'),'grounded':False,'date':today}; stfix.append((i,it.get('issues')))
        elif b['kind']=='art' and i in byS:
            rm=set(it.get('remove') or []); before=len(byS[i]['art']); byS[i]['art']=[a for a in byS[i]['art'] if a not in rm]; removed+=before-len(byS[i]['art'])
            if rm: byS[i].setdefault('art_removed',[]).extend(sorted(rm))
json.dump(S,open(R+'data/stories.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
json.dump(C,open(R+'data/characters.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(dict(stat),'art removed',removed)
print('REL FIX:'); [print(' ',i,'|',x) for i,x in relfix]
print('STORY FIX:'); [print(' ',i,'|',x) for i,x in stfix]
