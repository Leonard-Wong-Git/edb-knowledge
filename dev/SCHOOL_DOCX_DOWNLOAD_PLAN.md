# 學校版政策文件 — 下載呈現方案（S160）

> Leonard 通宵指示：「我起床時，要有一個方案去擺好現時學校版的文件，供使用者下載。」
> 本方案已**實作 + browser-verify 通過**（desktop React），待 Leonard 拍板是否 deploy。

## 1. 結論（TL;DR）

新增 app.html **「📋 政策範本」tab**：把現有 14 範疇 × 102 份學校版/清單 docx 以**下載入口**形式呈現，按範疇分組、可按校類（小/中/特/通用）篩選。**零檔案複製、零 backend、純加法、可逆**。

- docx 本身**已 git-tracked + 已 live-servable**（`.nojekyll` + GitHub Pages），實測 `https://policychecker.wongfu.net/dev/checklists/<域>/<檔>.docx` → HTTP 200、正確 docx MIME、49KB。
- 新 tab 由 `policy_templates.json`（root manifest）驅動，列出每份檔的範疇/校類/類型/路徑/大小 → render 下載掣（`<a download>` 直連 live docx）。

## 2. 為何揀呢個做法（選項比較）

| 選項 | 做法 | 取捨 | 裁決 |
|---|---|---|---|
| **A（已採用）** | 直接連現有 `dev/checklists/<域>/*.docx` live 路徑 + manifest 驅動 UI | 零複製、零 backend、改 docx 即重生 manifest 同步；URL 帶 `dev/` 路徑（用戶撳掣下載、唔會睇 URL） | ✅ 最小解、可逆 |
| B | 複製 102 份去乾淨 `downloads/政策範本/` 路徑 | URL 靚啲；但 repo 多 102 個 binary 複本、每次重生要 copy、易 drift | ❌ 多餘複製 |
| C | client-side 即時生成 docx（browser docx UMD + checklist JSON） | repo 唔使存 binary；但要 port 成 browser、所有 checklist JSON 落前端、工程大 | ❌ 過度建造 |
| D | backend route 生成/serve docx | URL 乾淨；但 docx 係靜態交付物，generation overkill、加 backend 複雜度 | ❌ 不必要 |

**A** 對齊 playbook `right-size-personal-scope`（揀啱大細最小解）。若 Leonard 想要 B 嘅乾淨 URL，可後續加一個 copy 步驟落 `gen_all.py`（已留 note）。

## 3. 實作了什麼（本 session）

| 檔案 | 動作 | 說明 |
|---|---|---|
| `policy_templates.json`（root） | **NEW** | 14 域 × 102 docx manifest（kind/school_type/type_label/name/path/size）。由生成器產出、勿手改 |
| `dev/checklists/_work/gen_templates_manifest.py` | **NEW** | 掃 `dev/checklists/<域>/*.docx` → 砌 manifest。`--check` 只印唔寫。**改 docx 後 re-run** |
| `app.html` | **MODIFIED（純加法）** | +`TemplatesPanel` component +`'templates'` 入 VALID_VIEWS +tab 掣「📋 政策範本」+router branch。其餘 tab/邏輯零接觸 |

### UI 行為
- 頂部：標題 + 說明 + **DRAFT 草擬本免責提示**（磚紅框）。
- **校類篩選**：全部 / 通用 / 小學 / 中學 / 特殊學校（segmented，即時過濾 + 計數）。
- 每範疇一張卡：範疇中文名 + 份數；分「政策範本（學校版，可編輯）」+「文件要求清單」兩組；每份一個下載掣（綠=學校版 / 白=清單），顯示校類 label + KB。

## 4. QC（browser-verify @ localhost：app.html#templates）

- ✅ Babel 編譯零錯（無 blank page）；console 淨係 benign Babel transformer warning、0 error。
- ✅ 14 範疇卡、**102 個 `<a download>` 連結**（= manifest total）。
- ✅ 校類篩選：揀「小學」→ 26 連結（13 域 × policy+checklist；kg_admission 無小學版，數字啱）；reset「全部」→ 102。
- ✅ 下載連結實測 `fetch(href)` → HTTP 200 + 正確 docx MIME；href URL-encoded、`download` 屬性帶正確中文檔名。
- ✅ 改動隔離 React desktop view；mobile `m-shell` 未受影響。

## 5. 已知限制 / 待 Leonard 決定

1. **Mobile shell 未有呢個 tab** — `mobile.js`（平板 m-shell）暫未加「政策範本」入口（同 S154 文件分析 mobile = Phase 1.5 一樣嘅已知 scope，非 bug）。要落 mobile 再講。
2. **DRAFT 標示** — 所有 docx 檔名帶 `_DRAFT`、UI 有免責框。若要拆「DRAFT」需 Leonard review 內容後先郁。
3. **URL 帶 `dev/` 路徑** — 功能無問題（撳掣下載）；要靚 URL 走選項 B。
4. **清單版要唔要對外** — 目前學校版 + 清單版都列。若只想出學校版，manifest 生成器加一個 `kind` filter 即可。
5. **Deploy 與否** — 本 session 唔自動 deploy 上 live（通宵自主、新 user-facing tab 留你 review）。一鍵上線見 §6。

## 6. 一鍵 deploy（Leonard review 後）

於 `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`：
```bash
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && git push origin main
```
（commit 已喺本機 main；push = GitHub Pages 自動 deploy，新 tab 即時生效，docx 已在線。）

## 7. 重生流程（日後 docx 更新）

```bash
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/checklists/_work/gen_templates_manifest.py
```
→ 覆寫 `policy_templates.json`；app.html 下次載入自動反映。**DOC_SYNC**：docx 重生 → 必 re-run 此生成器（已記入本方案）。
