# 希臘神話大全集

希臘神話睡前故事集，配上《西洋藝術流派大全集》與《西洋雕刻演進大全集》的館藏插圖，附互動人物關係圖。靜態站，資料全在 `data/`。

## 檔案結構
```
index.html            單頁應用（hash 路由）：首頁／故事／人物／關係圖／藝術作品
lib/d3.min.js         d3 7.9.0（關係圖）
data/stories.json     365 則故事（一天一則；12 個篇章）（id, title, en, cycle, chars, age, minutes, summary, hook, sections[{h,p[]}], ending, parents_note, source, keywords_en, moral, adapt_level, art[]）
data/characters.json  467 位人物（zh, en, gr, roman, cat, domain, symbols, bio, parents, spouses, lovers, children, siblings, killed, killed_by, transformed, mentor_of, note）
data/relations.json   由 characters 推導的關係邊（s, t, k ∈ 父母／配偶／情人／手足／殺害／變形／師徒）
data/artworks.json    插圖：site p/s 為兩個大全集的作品（圖檔引用原站 URL）；site m 為本站自 Wikidata「描繪對象」收成、存於 img/ 的作品
img/800, img/thumb    本站自有插圖（m 開頭 id；Commons 公共領域）
data/meta.json        版本、篇章（cycles）、計數
tools/names.json      人物名稱比對字典（英文名／羅馬名／中文譯名）
tools/match_art.py    從兩個大全集的 works.json 產生 artworks.json
tools/build.py        首版合併腳本（v1）
tools/relations.py    由 characters.json 重建 relations.json
tools/rematch.py      插圖說明譯名正規化（音譯變體統一、羅馬名加註）
tools/match_art.py    從兩個大全集比對候選作品
```

## 如何擴充
- 新增故事：在 `/home/claude/myth/work/STORY_LIST.json` 加一列，請子代理依 `STORY_BRIEF.md` 撰寫，跑 `tools/build.py`。
- 新增人物：加進 characters.json（關係欄位要雙向），`tools/names.json` 加比對名稱，重跑 `match_art.py` 與 `build.py`。
- 插圖配對：候選作品由 Sonnet 子代理逐件判定「正是該情節（3 分）／主角相關（2 分）」，記錄在 stories[].art（依分數排序）。要新增圖源：以 Wikidata SPARQL 查 `wdt:P180`（描繪對象）取得 P18 圖檔，流程見 /home/claude/myth/work/dep/。

## 資料品質
- 故事依原典（赫西俄德、荷馬、奧維德、阿波羅多洛斯等）改寫為 5–12 歲可聽的版本，每篇 `parents_note` 誠實標示改寫處與改寫程度（輕／中／重）。
- 人物關係依最通行版本，有爭議者寫在 `note`。
- 圖檔版權：皆為公共領域作品（Wikimedia Commons／NGA 開放資料），來源頁可從大圖視窗連回。
