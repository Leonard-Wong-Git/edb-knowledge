# K1 Mobile UI Spec v1.0

**Status:** Draft — awaiting Leonard review
**Scope:** Mobile-only experience，desktop 不變
**Reference:** Tado app + Pantone Cloud Dancer 2026 + DesignRush 2025-26 functional storytelling
**Skills used:** refero-design (Discovery + Phase) + ui-ux-responsive (award intelligence + Pantone)

---

## 1. Design Brief（refero-design Phase 0）

> 我哋設計緊**香港 EDB 政策知識搜尋平台嘅 mobile-only 體驗**（4 個 HTML 全部加 mobile detection），俾**校長／管理層／教師／行政全部角色** mobile 場景使用，幫佢哋**極速搜尋政策事實 + 閱讀結果**。Tone：**Tado-app 風格**（minimalist 大字、漸變背景、bottom sheet、focus 單一動作、平靜信任感）。Job：「俾我即時答政策問題，唔好擾亂我嘅工作節奏」。最大 objection：「政府資訊唔太信／怕資訊舊」→ 用 EDB 為準聲明 + source 追溯破局。Memorable hook：「**一句問題，一個答案，一個官方來源**」。

---

## 2. Design Decisions（refero-design Phase 3 — Soul）

### 80% 證實 pattern
1. Bottom tab bar navigation（thumb-zone friendly，4-5 個 tab）
2. Search-first hero（搜尋輸入即係主入口）
3. Card-based result list（每張 card = 一條 fact）
4. Bottom sheet for detail view（90vh，可 swipe down close）
5. Single column, full-width CTAs
6. Body text ≥16px（避免 iOS 自動 zoom）
7. Touch target ≥44×44px

### 20% Soul（K1 獨特）
1. **EDB 深綠 → Cloud Dancer 米白漸變背景**（brand anchor 配 Pantone 2026 cultural exhale）
2. **「一句問題」focus**：search bar 大型（56px 高），placeholder 用具啟發句子例如「教師病假上限多少天？」
3. **Source 圖標系統**：每條 result card 用 emoji + label 標識文件類型（📗 學校行政手冊 / 📑 課程指引 / 📋 採購指引），唔再純 source_id
4. **角色 chip 配色**：principal 磚紅 / panel_chair 海軍藍 / teacher 草綠 / eo_admin 紫，rapid 視覺識別
5. **EDB 為準 disclaimer**：sticky bottom info bar 永久顯示「資料以 EDB 為準」一句，建立 trust signal

---

## 3. Mobile Detection 機制（架構決策）

**選用方案：CSS media query + JS conditional layout**

```css
/* mobile.css 加在每個 HTML head */
@media (max-width: 640px) {
  /* 觸發 mobile-only styles */
  .desktop-only { display: none !important; }
  .mobile-only  { display: block; }
  body { /* mobile layout overrides */ }
}

@media (min-width: 641px) {
  .mobile-only { display: none !important; }
  /* desktop 默認，無需改動 */
}
```

**JS 補強（早期 conditional rendering，避免 flash）：**
```js
const isMobile = window.matchMedia('(max-width: 640px)').matches
              || /Mobi|Android/i.test(navigator.userAgent);
document.documentElement.dataset.viewport = isMobile ? 'mobile' : 'desktop';
```

**為何唔開 separate mobile.html route：**
- 維護成本高（兩個 source of truth 易脫節）
- 同一份 HTML data + 內容，只係 layout 唔同
- CSS-driven 切換最低 risk + 最易 sync

---

## 4. Mobile Design System Tokens

### 4.1 Color Palette（EDB green + Pantone Cloud Dancer 2026）

```css
:root {
  /* EDB brand anchor (existing) */
  --edb-deep:        #0D6B47;  /* 主深綠 — nav / CTA */
  --edb-mid:         #1A8B5F;
  --edb-light:       #4FB388;
  --edb-wash:        #E5F2EB;

  /* Cloud Dancer 2026 — backgrounds */
  --cloud:           #F0EEE9;  /* primary bg */
  --cloud-warm:      #F8F6F2;  /* card bg */
  --cream:           #E4DFD5;  /* divider / muted */

  /* Atmospheric accent (Pantone companion palette) */
  --sea-glass:       #9EC4B8;  /* secondary accent */
  --sky-mist:        #D6E4E8;  /* result card highlight */

  /* Text */
  --text-primary:    #2A3A33;  /* WCAG AAA on cloud */
  --text-secondary:  #5C6A63;
  --text-muted:      #8A938E;

  /* Role chips */
  --role-principal:    #BF360C;
  --role-panel:        #283593;
  --role-teacher:      #1B5E20;
  --role-admin:        #4527A0;

  /* Hero gradient (EDB → Cloud Dancer) */
  --hero-gradient: linear-gradient(135deg, var(--edb-deep) 0%, var(--edb-mid) 60%, var(--cloud-warm) 100%);
}
```

### 4.2 Typography（fluid scale）

```css
:root {
  --m-text-base:    16px;          /* body min */
  --m-text-sm:      14px;
  --m-text-xs:      12px;
  --m-text-lg:      18px;          /* card title */
  --m-text-xl:      22px;          /* section title */
  --m-text-hero:    clamp(28px, 8vw, 36px);  /* search bar prompt */
  --m-text-stat:    clamp(36px, 12vw, 56px); /* large stat numbers */

  --m-font-body:    'Noto Sans HK', system-ui, sans-serif;
  --m-leading:      1.55;
  --m-tracking-tight: -0.01em;
}
```

### 4.3 Spacing & Radius

```css
:root {
  --m-space-xs: 4px;
  --m-space-sm: 8px;
  --m-space-md: 16px;
  --m-space-lg: 24px;
  --m-space-xl: 32px;
  --m-space-2xl: 48px;

  --m-radius-sm: 8px;
  --m-radius-md: 16px;        /* cards — Tado-feel rounded */
  --m-radius-lg: 24px;        /* bottom sheet top corners */
  --m-radius-pill: 999px;

  --m-touch-min: 44px;        /* WCAG touch target min */
}
```

### 4.4 Motion（subtle, prefers-reduced-motion respected）

```css
:root {
  --m-ease: cubic-bezier(0.32, 0.72, 0, 1);  /* iOS-feel */
  --m-dur-fast: 180ms;
  --m-dur-base: 240ms;
  --m-dur-slow: 360ms;
}

@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
```

---

## 5. Layout & Navigation（Tado-inspired）

### 5.1 Bottom Tab Bar（共用，4 個入口）

```
┌─────────────────────────────────────┐
│                                     │
│  (active screen content)            │
│                                     │
│                                     │
├─────────────────────────────────────┤
│  🔍       📚       ℹ️       👤     │
│  搜尋     文件庫    平台介紹  我的角色 │
└─────────────────────────────────────┘
```

- 高 64px，永遠 sticky bottom
- 4 個 icon + label，touch target 44px×64px
- Active state：icon 變 EDB 深綠 + label bold + 上方 2px accent line
- Material/SF symbols style icons（statement weight 400-500）

### 5.2 Top App Bar（最簡 — 唔搶 search 焦點）

```
┌─────────────────────────────────────┐
│  ◀  K1 知識平台          ⚙        │  ← 56px high
└─────────────────────────────────────┘
```

- 純 logo / 標題 + 設定齒輪
- 唔放 hamburger menu（bottom tab 已 cover navigation）
- 在搜尋頁可省略，俾 hero search 食 full screen

### 5.3 EDB 為準 sticky info bar（永久 trust signal）

```
┌─────────────────────────────────────┐
│ ⓘ 資料以 EDB 為準 · 點擊查官網    →  │  ← 32px height，bottom tab 上方
└─────────────────────────────────────┘
```

- 高 32px，永遠 sticky 在 bottom tab 上方
- 點擊跳 EDB 官網
- 細字 12px，訊息 brief 但 always visible

---

## 6. 4 個 HTML 嘅 Mobile Layout

### 6.1 index.html — Mobile Landing

**Layout：**
1. **Hero gradient section（屏幕高 60vh）**
   - 中央：「K1 知識平台」logo + tagline
   - 大 search bar prompt：「搜尋 EDB 政策…」placeholder
   - 點擊 search bar → jump 至 app.html mobile search
2. **Stats strip（4 stats 2x2 grid）**
   - 792 已核實 / 10,736 文件 / 7 主題 / 120 來源
   - 大字 32px + small label
3. **「核心功能」3 卡 stack**（垂直 single column）
   - 政策語義搜尋 / 指引文件庫 / EDB 通告分析系統
   - 每卡帶 icon + 短描述 + CTA button
4. **資料覆蓋 section**（K1-K3 / P1-P6 / S1-S6 / 跨階段，2x2 grid）
5. **EDB 為準 disclaimer card**
6. **Bottom tab bar**（永遠 visible）

### 6.2 app.html — Mobile Search Workspace（核心）

**Layout：**
1. **Top app bar minimal**（◀ 標題 + ⚙）56px
2. **Search hero card（即係 active tab content）**
   - 大 search input 56px high
   - Placeholder rotate 啟發句子（「教師病假上限多少天？」「採購 5 萬以上程序？」）
   - 提交後 → result list 即場 inline 出現
3. **Result list**
   - 每張 card：
     ```
     ┌──────────────────────────────┐
     │ 📗 學校行政手冊  [校長][教師]│  ← 來源 + 角色 chip
     │                              │
     │ 教師病假首年可享 28 天有薪…  │  ← fact 內容（2 行 truncate）
     │                              │
     │ ●●●○○ 0.72                  │  ← score dot + 數字
     └──────────────────────────────┘
     ```
   - Tap card → bottom sheet 開
4. **Result detail bottom sheet（90vh）**
   - Drag handle top
   - 來源 icon + 全文標題
   - Fact full text
   - 「📋 適用角色」chips
   - 「🔗 看 EDB 原文」CTA button（大 primary）
   - Channel 標識（已核實資料 / 來源文件）
   - Swipe down 或 close button 關閉
5. **EDB 為準 sticky info bar** + **Bottom tab bar**

### 6.3 q.html — Quick Q&A Mobile

- 同 app.html 搜尋頁類似但精簡
- 純 search + result list inline，無 bottom sheet（直接 expand inline）
- 適合 quick lookup 場景

### 6.4 t-purchase.html — Mobile Form Flow

- 表格 single column stack
- 每 step 一個 screen（next button bottom full-width）
- Progress indicator top（4 dots）
- Less 適合 mobile，但保留作 fallback

---

## 7. Implementation Phases

| Phase | 範圍 | 工程量 | Risk |
|---|---|---|---|
| 1 | 設計 + 切 4 個 HTML 共 mobile.css 同 mobile.js + design token 寫入 | 中 | 低 |
| 2 | index.html mobile layout（最易 — landing） | 小 | 低 |
| 3 | app.html mobile layout（最複雜 — search + bottom sheet） | 大 | 中 |
| 4 | q.html mobile layout | 小 | 低 |
| 5 | t-purchase.html mobile layout | 中 | 低 |
| 6 | QA：iPhone 12/SE / Android Pixel viewport 全測；prefers-reduced-motion；touch target 44px audit | 中 | 低 |
| 7 | Polish + commit + push | 小 | 低 |

預估全部完成 5-8 hours 工作（分多 session 做穩）。

---

## 8. Quality Checklist（refero-design Phase 4 + ui-ux-responsive Part D）

### Award standard
- [ ] 設計有清晰 point of view（Tado-inspired calm + EDB trust）
- [ ] Animation 服務 narrative（bottom sheet open / page transition）
- [ ] `prefers-reduced-motion` 全程 respect
- [ ] Typography 有意圖（fluid scale，hero search 大字 statement）
- [ ] Mobile 唔係 desktop 縮版（獨立 layout 同 navigation）

### Color
- [ ] 全部 text/bg WCAG AA 4.5:1（已用 #2A3A33 on Cloud Dancer = AAA）
- [ ] Mobile 同屏 ≤3 顏色（EDB green + Cloud Dancer + 1 accent）
- [ ] Color 編碼一致意義（accent = action）

### Responsive
- [ ] No overflow（所有 card width ≤ 100vw - 32px padding）
- [ ] Touch target ≥ 44px
- [ ] Body text ≥ 16px
- [ ] Scroll smooth，no janks

### Anti AI-slop
- [ ] 無 indigo / 無 generic blob bg / 無 stock illustration
- [ ] 用 EDB 深綠（brand-appropriate）唔係 default blue
- [ ] 至少一個記得住嘅 detail：「一句問題」prompt rotate / EDB 為準 sticky bar / Tado-feel rounded cards

---

## 9. Spec 決策（Leonard 答覆，2026-05-03）

1. ✅ **Mobile.css 命名**：A — 獨立 `mobile.css` + `mobile.js` 共享檔（清晰分隔，4 HTML 共用）
2. ✅ **Bottom tab bar**：3 個入口 = 搜尋 / 文件庫 / 平台介紹（**唔放「我的角色」**）
3. ✅ **角色切換**：唔做 persistent tab — 改為 **loading 時 first-run role picker overlay**（user 入 mobile app.html 第一次見 role picker，揀完之後寫入 localStorage，將來再 tap settings icon 改）
4. ✅ **Search placeholder rotate**：A — 我寫初稿（rotate 5-8 條，每 5 秒換）
5. 🟡 **EDB 為準 sticky info bar**：B — 太搶位，**改為登入後先 show**（unverified user 唔顯示，登入後 footer 永久顯示作 admin context）；未百分百肯定 — 可下節按實機 visual 再 tune
6. ✅ **Gradient bg + system mode**：A — Tado-inspired EDB 深綠 → Cloud Dancer 漸變；同時支援 **`prefers-color-scheme` light / dark 自動切換**（夜間 OS dark mode → mobile app 自動 dark theme）

---

## 10. Refero Research Caveat

本 spec doc 嘅 visual reference 主要靠：
- Tado app（你提供）
- Pantone Cloud Dancer 2026 + companion palettes
- ui-ux-responsive skill 嘅 award intelligence

**未跑 Refero MCP search**（sandbox 內 MCP 工具未 connect）。下次有 Refero 可補：
- search_screens "ios search bar" / "bottom sheet" / "policy search mobile"
- search_flows "search to detail" / "mobile onboarding"
- get_screen Tado-similar references

---

*Spec v1.0 — 2026-05-03 — 待 Leonard review，approved 後開 Implementation Phase 1*
