/* ============================================================
 * mobile.js — K1 Mobile-only logic（v1.0, 2026-05-03）
 *
 * Scope: detect mobile viewport / UA → activate mobile shell;
 *        first-run role picker; search placeholder rotation;
 *        bottom tab navigation cross-page.
 * Desktop: completely no-op（detection guard）.
 *
 * 4 HTML 共用：index.html / app.html / q.html / t-purchase.html
 * ============================================================ */

(function () {
  'use strict';

  // ── 1. Mobile detection (CSS-aligned: ≤640px viewport OR mobile UA) ──
  const MOBILE_QUERY = window.matchMedia('(max-width: 640px)');
  const UA_IS_MOBILE = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
  const isMobile = () => MOBILE_QUERY.matches || UA_IS_MOBILE;

  // No-op on desktop
  if (!isMobile()) {
    document.documentElement.dataset.viewport = 'desktop';
    return;
  }

  document.documentElement.dataset.viewport = 'mobile';
  document.body && (document.body.dataset.mobileActive = 'true');
  // If body not yet parsed, wait. NOTE: the eager (readyState !== 'loading')
  // trigger lives at the BOTTOM of this IIFE — initMobileShell()/buildGuidelinesShell()
  // reference module-scope `const`s (GUIDE_CATS, ROLES, …) declared further down,
  // so running init before those lines execute throws a TDZ ReferenceError.
  document.addEventListener('DOMContentLoaded', () => {
    document.body.dataset.mobileActive = 'true';
    initMobileShell();
  });

  // Guard: bind the same-document hashchange→reload handler only once.
  let hashReloadBound = false;

  // ── 2. Role definitions (synced with k1 platform schema) ──
  const ROLES = [
    { key: 'principal',      label: '校長 / 副校長',     desc: '政策決策、採購審批、財務合規',          color: '#BF360C' },
    { key: 'panel_chair',    label: '科主任 / 統籌主任', desc: '課程政策、SEN 支援、CPD 要求',          color: '#283593' },
    { key: 'subject_head',   label: '科主任',            desc: '學科課程及評估安排',                     color: '#1565C0' },
    { key: 'teacher',        label: '教師',              desc: '請假手續、課時安排、職務責任',          color: '#1B5E20' },
    { key: 'eo_admin',       label: '行政人員 / EO',     desc: '採購程序、津貼使用、會議記錄',          color: '#4527A0' },
    { key: 'all_roles',      label: '一般用戶（不指定）', desc: '查閱所有角色適用嘅政策事實',            color: '#5C6A63' },
  ];

  const ROLE_STORAGE_KEY = 'k1-mobile-role';
  const MOBILE_TOUR_FLAG = 'k1_mobile_tour_v1';

  function getStoredRole() {
    try { return localStorage.getItem(ROLE_STORAGE_KEY); }
    catch (_) { return null; }
  }
  function storeRole(key) {
    try { localStorage.setItem(ROLE_STORAGE_KEY, key); } catch (_) {}
  }

  function getMobileTourDone() {
    try { return !!localStorage.getItem(MOBILE_TOUR_FLAG); } catch (_) { return true; }
  }
  function setMobileTourDone() {
    try { localStorage.setItem(MOBILE_TOUR_FLAG, '1'); } catch (_) {}
  }

  // S175 — 4-step first-visit onboarding tour (mobile-specific features)
  const MOBILE_TOUR_STEPS = [
    { icon: '👋', title: '歡迎使用香港學校政策搜尋平台', body: '快速查找 EDB 教育政策，附來源頁碼，直跳官方原文 PDF。四個主要功能讓你告別翻文件。' },
    { icon: '🔍', title: '政策搜尋', body: '輸入 1–3 個關鍵字（例如「教師病假」「採購 5 萬」），AI 即時比對 EDB 官方指引，附來源頁碼，可直跳 PDF 對應頁。' },
    { icon: '📚', title: '指引文件庫', body: '分類整理嘅 EDB 官方指引文件——課程、財務、SEN、幼稚園等。點下方「📚 指引文件」打開。' },
    { icon: '✅', title: '準備好了！', body: '接下來請選擇你嘅崗位角色，系統會根據角色精準篩選最相關嘅政策事實。' },
  ];

  function showMobileTour(onDone) {
    var total = MOBILE_TOUR_STEPS.length;
    var current = 0;

    var overlay = document.getElementById('m-tour');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'm-tour';
      overlay.className = 'm-tour';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-modal', 'true');
      overlay.setAttribute('aria-label', '平台導覽');
      document.body.appendChild(overlay);
    }
    overlay.setAttribute('aria-hidden', 'false');

    function render() {
      var s = MOBILE_TOUR_STEPS[current];
      var isLast = current === total - 1;
      var dots = '';
      for (var i = 0; i < total; i++) {
        dots += '<span class="m-tour-dot' + (i === current ? ' active' : '') + '"></span>';
      }
      overlay.innerHTML = ''
        + '<div class="m-tour-icon">' + s.icon + '</div>'
        + '<h2 class="m-tour-title">' + escapeHTML(s.title) + '</h2>'
        + '<p class="m-tour-body">' + escapeHTML(s.body) + '</p>'
        + '<div class="m-tour-dots">' + dots + '</div>'
        + '<nav class="m-tour-nav">'
        +   '<button class="m-tour-skip" id="m-tour-skip">略過</button>'
        +   '<button class="m-tour-next' + (isLast ? ' primary' : '') + '" id="m-tour-next">'
        +     (isLast ? '開始使用 →' : '下一步')
        +   '</button>'
        + '</nav>';
      overlay.querySelector('#m-tour-skip').addEventListener('click', finish);
      overlay.querySelector('#m-tour-next').addEventListener('click', function () {
        if (isLast) { finish(); } else { current++; render(); }
      });
    }

    function finish() {
      overlay.setAttribute('aria-hidden', 'true');
      setMobileTourDone();
      if (typeof onDone === 'function') onDone();
    }

    render();
  }

  // ── 3. Search placeholder rotate (5-8 條，每 5 秒切換) ──
  const PLACEHOLDER_QUERIES = [
    '教師病假上限多少天？',
    '採購超過 5 萬元程序？',
    '全方位學習津貼可用範圍？',
    '幼稚園收生安排？',
    '教師專業發展 CPD 要求？',
    '校曆表 190 天上學日如何計？',
    '訓導及輔導學生指引？',
    '採購 200,000 元以上招標流程？',
  ];
  let placeholderIndex = 0;
  function startPlaceholderRotation() {
    const inputs = document.querySelectorAll('.m-search-input');
    if (!inputs.length) return;
    const setAll = () => {
      inputs.forEach(i => { i.placeholder = PLACEHOLDER_QUERIES[placeholderIndex]; });
    };
    setAll();
    setInterval(() => {
      placeholderIndex = (placeholderIndex + 1) % PLACEHOLDER_QUERIES.length;
      setAll();
    }, 5000);
  }

  // ── 4. Build role picker overlay ──
  function buildRolePickerHTML() {
    let html = '';
    html += '<div class="m-role-picker-eyebrow">香港學校政策搜尋平台 · 第一次使用</div>';
    html += '<h2>請選擇你的角色</h2>';
    html += '<p style="text-align:center;color:var(--m-text-secondary);font-size:var(--m-text-sm);margin:0 0 var(--m-sp-md)">影響搜尋結果的角色適用標籤；之後可在設定改變</p>';
    ROLES.forEach(r => {
      html += '<button class="m-role-option" data-role-key="' + r.key + '" aria-pressed="false">';
      html += '  <span class="m-role-option-dot" style="background:' + r.color + '"></span>';
      html += '  <span style="flex:1">';
      html += '    <span class="m-role-option-name">' + r.label + '</span>';
      html += '    <span class="m-role-option-desc">' + r.desc + '</span>';
      html += '  </span>';
      html += '</button>';
    });
    html += '<button class="m-role-picker-cta" disabled>確認選擇</button>';
    return html;
  }

  function showRolePicker() {
    let overlay = document.getElementById('m-role-picker');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'm-role-picker';
      overlay.className = 'm-role-picker';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-modal', 'true');
      overlay.innerHTML = buildRolePickerHTML();
      document.body.appendChild(overlay);
    }
    overlay.setAttribute('aria-hidden', 'false');

    let selected = null;
    overlay.querySelectorAll('.m-role-option').forEach(btn => {
      btn.addEventListener('click', () => {
        overlay.querySelectorAll('.m-role-option').forEach(b => b.setAttribute('aria-pressed', 'false'));
        btn.setAttribute('aria-pressed', 'true');
        selected = btn.dataset.roleKey;
        const cta = overlay.querySelector('.m-role-picker-cta');
        if (cta) cta.disabled = false;
      });
    });
    const cta = overlay.querySelector('.m-role-picker-cta');
    if (cta) {
      cta.addEventListener('click', () => {
        if (!selected) return;
        storeRole(selected);
        overlay.setAttribute('aria-hidden', 'true');
        // Optional: trigger a custom event for pages that want to react
        document.dispatchEvent(new CustomEvent('k1-role-selected', { detail: { role: selected } }));
      });
    }
  }

  // ── 5. Bottom tab bar (4 entries: 搜尋 / 指引文件 / 範本下載 / 平台介紹) ──
  // Cross-page links — current page determined by location.pathname + URL hash
  function buildTabBar() {
    if (document.querySelector('.m-tabbar')) return; // page already has its own
    const tabbar = document.createElement('nav');
    tabbar.className = 'm-tabbar';
    tabbar.setAttribute('role', 'navigation');
    tabbar.setAttribute('aria-label', '主要導航');

    const here = (location.pathname.split('/').pop() || 'index.html');
    const hash = location.hash || '';
    const TABS = [
      { key: 'search',     icon: '🔍', label: '搜尋',       href: 'app.html',                match: ['app.html'] },
      { key: 'library',    icon: '📚', label: '指引文件',   href: 'app.html#guidelines',     match: ['#guidelines'] },
      { key: 'templates',  icon: '📋', label: '範本下載',   href: 'app.html#templates',      match: ['#templates'] },
      { key: 'about',      icon: 'ℹ️', label: '平台介紹',   href: 'index.html',              match: ['index.html', ''] },
    ];

    TABS.forEach(t => {
      const isActive =
        (t.key === 'library'   && hash === '#guidelines') ||
        (t.key === 'templates' && hash === '#templates') ||
        (t.key === 'search'    && here === 'app.html' && hash !== '#guidelines' && hash !== '#templates') ||
        (t.key === 'about'     && (here === 'index.html' || here === '') && hash !== '#guidelines' && hash !== '#templates');
      const a = document.createElement('a');
      a.className = 'm-tab';
      a.href = t.href;
      if (isActive) a.setAttribute('aria-current', 'page');
      a.innerHTML = '<span class="m-tab-icon">' + t.icon + '</span><span>' + t.label + '</span>';
      tabbar.appendChild(a);
    });

    document.body.appendChild(tabbar);
  }

  // ── 6. Page-specific content render ──
  const BACKEND_URL = 'https://edb-knowledge.onrender.com';

  // Source label map (mirrors app.html SOURCE_LABELS, mobile-friendly subset)
  const SOURCE_LABEL = {
    sag_2025_11: '學校行政手冊',
    g24: '學校行政手冊',
    coa_imc_1_19: '資助則例',
    g01: '採購程序指引',
    g02: '財務管理指引',
    g03: '全方位學習津貼',
    g04: '教職員批假指引',
    g05: '教師專業操守指引',
    g11: '校曆表指引',
    g29: '幼稚園課程指引',
    role_facts_finance: '已核實知識庫 · 財務',
    role_facts_hr: '已核實知識庫 · 人事',
    role_facts_curriculum: '已核實知識庫 · 課程',
    role_facts_general: '已核實知識庫 · 通用',
  };
  const sourceLabel = id => SOURCE_LABEL[id] || (id || '').replace(/^vault_/, '').replace(/_/g, ' ');
  // Always-Chinese display name: curated short label → the doc's own (Chinese) title
  // → generic fallback. Never the raw English source_id.
  const displayName = (id, title) => SOURCE_LABEL[id] || (title && String(title).trim()) || 'EDB 文件';

  const sourceIcon = id => {
    if (!id) return '📄';
    if (id.indexOf('sag') >= 0 || id === 'g24') return '📗';
    if (id.indexOf('coa') >= 0) return '📘';
    if (id.indexOf('g0') === 0 || id.indexOf('g1') === 0) return '📋';
    if (id.indexOf('role_facts') === 0) return '✅';
    if (id.indexOf('edbc') >= 0) return '📄';
    return '📑';
  };

  // ── WhatsApp share helpers ──
  function buildShareText(query, synthesis, results) {
    const seen = new Map();
    (results || []).forEach(r => {
      const sid = r.source_id || '';
      if (!sid) return;
      if (!seen.has(sid)) {
        seen.set(sid, { label: displayName(sid, r.title), pages: new Set(), score: 0 });
      }
      const entry = seen.get(sid);
      if (typeof r.page === 'number' && r.page > 0) entry.pages.add(r.page);
      if ((r.score || 0) > entry.score) entry.score = r.score || 0;
    });
    const top = Array.from(seen.values()).sort((a, b) => b.score - a.score).slice(0, 5);
    const srcLine = top.map(s => {
      const pages = Array.from(s.pages).sort((a, b) => a - b).slice(0, 3);
      return '《' + s.label + '》' + (pages.length ? ' p.' + pages.join(',') : '');
    }).join(' · ');
    const lines = ['【香港學校政策搜尋平台 · 政策搜尋】', '問：' + (query || '').trim()];
    if (synthesis) lines.push('', synthesis);
    if (srcLine) lines.push('', '來源：' + srcLine);
    lines.push('🔗 https://policychecker.wongfu.net/app.html');
    return lines.join('\n');
  }
  function shareToWhatsApp(text) {
    window.open('https://wa.me/?text=' + encodeURIComponent(text), '_blank', 'noopener');
  }

  // Build app.html mobile shell: hero + search + results + sheet
  function buildAppShell() {
    if (document.getElementById('m-app-shell')) return;
    const shell = document.createElement('main');
    shell.id = 'm-app-shell';
    shell.className = 'm-shell';
    shell.innerHTML = ''
      + '<section class="m-hero">'
      +   '<div class="m-hero-eyebrow">香港學校政策搜尋平台 · 香港學校管治</div>'
      +   '<h1 class="m-hero-title">查找有根有據的政策答案</h1>'
      +   '<p class="m-hero-desc">輸入問題，即時比對 EDB 已核實事實及原文片段。</p>'
      +   '<p class="m-hero-desc" id="m-hero-usage" style="opacity:.72;margin-top:-2px"></p>'
      +   '<form class="m-search" id="m-search-form" autocomplete="off">'
      +     '<svg class="m-search-icon" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>'
      +     '<input class="m-search-input" id="m-search-input" type="search" inputmode="search" enterkeyhint="search" placeholder="教師病假上限多少天？" />'
      +     '<button type="submit" class="m-search-btn" aria-label="搜尋">搜尋</button>'
      +   '</form>'
      + '</section>'
      + '<section class="m-result-list" id="m-result-list" aria-live="polite"></section>'
      + '<div class="m-sheet-backdrop" id="m-sheet-backdrop" aria-hidden="true"></div>'
      + '<aside class="m-sheet" id="m-sheet" aria-hidden="true" role="dialog" aria-modal="true">'
      +   '<div class="m-sheet-handle"></div>'
      +   '<div id="m-sheet-content"></div>'
      + '</aside>';
    document.body.insertBefore(shell, document.body.firstChild);

    // S204 — cumulative search count. The desktop QAPanel shows this inside its 來源文件
    // subtitle, which the mobile shell has no equivalent of, so without its own line here
    // phone users never see the counter. textContent, not innerHTML; and the line stays
    // empty on failure rather than rendering a misleading zero.
    fetch(BACKEND_URL + '/api/stats/usage')
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d || !d.ok) return;
        var el = document.getElementById('m-hero-usage');
        if (el) el.textContent = '累計已服務 ' + Number(d.total).toLocaleString() + ' 次查詢';
      })
      .catch(function () {});

    const form = document.getElementById('m-search-form');
    const input = document.getElementById('m-search-input');
    const list = document.getElementById('m-result-list');

    // Initial empty state
    renderEmpty(list);

    const submitSearch = () => {
      const q = (input.value || '').trim();
      if (!q) return;
      input.blur();
      runSearch(q, list);
    };
    form.addEventListener('submit', e => { e.preventDefault(); submitSearch(); });
    // Belt-and-suspenders: some mobile keyboards / IME do not fire implicit form
    // submission on Enter when the form has no submit button — bind Enter directly.
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.keyCode === 13) { e.preventDefault(); submitSearch(); }
    });

    // Bottom sheet close on backdrop tap
    document.getElementById('m-sheet-backdrop').addEventListener('click', closeSheet);
  }

  function renderEmpty(list) {
    list.innerHTML = ''
      + '<div style="padding:48px 20px;text-align:center;color:var(--m-text-muted);font-size:14px;line-height:1.6">'
      +   '<div style="font-size:40px;margin-bottom:12px;opacity:0.5">🔍</div>'
      +   '輸入政策問題開始搜尋<br>例：採購超過 5 萬元程序？'
      + '</div>';
  }

  function renderLoading(list, query) {
    list.innerHTML = ''
      + '<div id="m-loading-box" style="padding:32px 20px;text-align:center;color:var(--m-text-secondary);font-size:14px">'
      +   '<div style="display:inline-flex;gap:6px"><span style="width:8px;height:8px;border-radius:50%;background:var(--m-edb-mid);animation:m-pulse 1s infinite"></span><span style="width:8px;height:8px;border-radius:50%;background:var(--m-edb-mid);animation:m-pulse 1s infinite 0.15s"></span><span style="width:8px;height:8px;border-radius:50%;background:var(--m-edb-mid);animation:m-pulse 1s infinite 0.3s"></span></div>'
      +   '<div id="m-loading-text" style="margin-top:12px">正在搜尋…</div>'
      + '</div>'
      + '<style>@keyframes m-pulse{0%,100%{opacity:0.3}50%{opacity:1}}</style>';
  }

  function updateLoadingText(text) {
    const t = document.getElementById('m-loading-text');
    if (t) t.textContent = text;
  }

  function renderError(list, msg, query) {
    list.innerHTML = ''
      + '<div style="padding:20px 16px;text-align:center;color:#c0392b;background:#fdecea;border-radius:12px;margin:16px;font-size:14px;line-height:1.6">'
      +   '⚠️ ' + escapeHTML(msg || '搜尋暫時不可用，請稍後再試')
      +   (query ? '<button id="m-retry-btn" type="button" style="display:block;margin:14px auto 0;padding:10px 20px;background:var(--m-edb-deep);color:#fff;border:0;border-radius:var(--m-r-pill);font-weight:700;font-size:14px;cursor:pointer">重試搜尋</button>' : '')
      + '</div>';
    if (query) {
      const btn = document.getElementById('m-retry-btn');
      if (btn) btn.addEventListener('click', () => runSearch(query, list));
    }
  }

  async function runSearch(query, list) {
    renderLoading(list, query);
    // Cold start awareness: progressively update loading text
    const t1 = setTimeout(() => updateLoadingText('正在喚醒伺服器…首次查詢約 30 秒'), 5000);
    const t2 = setTimeout(() => updateLoadingText('伺服器即將就緒，請耐心等候'), 20000);
    const t3 = setTimeout(() => updateLoadingText('幾乎好了，再等多陣…'), 40000);

    // 60-second hard timeout via AbortController
    const ctrl = new AbortController();
    const killTimer = setTimeout(() => ctrl.abort(), 60000);

    try {
      const resp = await fetch(BACKEND_URL + '/api/search/channel-b', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, top_k: 8, min_score: 0.15, synthesize: true }),
        signal: ctrl.signal,
      });
      clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); clearTimeout(killTimer);

      if (resp.status === 429) {
        renderError(list, '搜尋次數過多，請稍候再試（每分鐘上限 10 次）', query);
        return;
      }
      if (!resp.ok) {
        renderError(list, '伺服器回應 HTTP ' + resp.status + '；可能需要重試', query);
        return;
      }
      const data = await resp.json();
      renderResults(list, data, query);
    } catch (err) {
      clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); clearTimeout(killTimer);
      const isAbort = err && err.name === 'AbortError';
      const isNet = err && /network|failed to fetch/i.test(err.message || '');
      let msg;
      if (isAbort) msg = '搜尋超時（60 秒）。Render 免費版閒置會休眠，第一次查詢需喚醒，請按重試';
      else if (isNet) msg = '網絡連接失敗，請檢查 Wi-Fi / 流動數據後重試';
      else msg = '搜尋失敗：' + (err && err.message ? err.message : '未知錯誤');
      renderError(list, msg, query);
    }
  }

  function renderResults(list, data, query) {
    const results = (data.results || []).slice(0, 8);
    if (!results.length) {
      list.innerHTML = '<div style="padding:32px 20px;text-align:center;color:var(--m-text-muted);font-size:14px">未找到相關政策事實，可改用其他關鍵詞</div>';
      return;
    }

    let html = '';
    if (data.synthesis) {
      html += '<div style="margin:0 0 4px;padding:16px;background:var(--m-edb-wash);border-radius:var(--m-r-md);border-left:3px solid var(--m-edb-deep)">'
           +   '<div style="font-size:11px;font-weight:700;color:var(--m-edb-deep);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px">整理答案</div>'
           +   '<div style="font-size:14px;line-height:1.6;color:var(--m-text-primary)">' + escapeHTML(data.synthesis) + '</div>'
           +   '<div style="display:flex;justify-content:flex-end;margin-top:12px;padding-top:10px;border-top:1px solid rgba(0,0,0,0.06)">'
           +     '<button id="m-share-wa-btn" type="button" aria-label="分享至 WhatsApp" '
           +       'style="display:inline-flex;align-items:center;gap:6px;background:#25D366;color:#fff;border:none;padding:8px 16px;border-radius:99px;font-size:13px;font-weight:700;cursor:pointer">'
           +       '📤 分享至 WhatsApp'
           +     '</button>'
           +   '</div>'
           + '</div>';
    }
    results.forEach((r, idx) => {
      const sid = r.source_id || '';
      const verified = r.content_type === 'approved_fact';
      const pageLabel = (typeof r.page === 'number' && r.page > 0) ? '頁 ' + r.page : '';
      const metaRight = verified ? ('✅ 已核實' + (pageLabel ? ' · ' + pageLabel : '')) : pageLabel;
      html += '<button class="m-result-card" data-idx="' + idx + '" type="button">'
           +   '<div class="m-result-meta">'
           +     '<span class="m-result-source">' + sourceIcon(sid) + ' ' + escapeHTML(displayName(sid, r.title)) + '</span>'
           +     (metaRight ? '<span style="font-size:11px;color:var(--m-text-muted);font-weight:600">' + metaRight + '</span>' : '')
           +   '</div>'
           +   '<div class="m-result-content">' + escapeHTML(r.text || '') + '</div>'
           + '</button>';
    });
    list.innerHTML = html;

    // Wire WhatsApp share button (only rendered when synthesis present)
    const shareBtn = document.getElementById('m-share-wa-btn');
    if (shareBtn) {
      shareBtn.addEventListener('click', () => {
        shareToWhatsApp(buildShareText(query, data.synthesis, results));
      });
    }

    // Wire card taps to bottom sheet
    list.querySelectorAll('.m-result-card').forEach(btn => {
      btn.addEventListener('click', () => {
        const i = parseInt(btn.dataset.idx, 10);
        openSheet(results[i]);
      });
    });
  }

  function escapeHTML(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  function openSheet(row) {
    const sheet = document.getElementById('m-sheet');
    const backdrop = document.getElementById('m-sheet-backdrop');
    const content = document.getElementById('m-sheet-content');
    if (!sheet || !content) return;

    const sid = row.source_id || '';
    const url = row.url || '';
    const verified = row.content_type === 'approved_fact';
    const role = row.role || '';
    const page = (typeof row.page === 'number' && row.page > 0) ? row.page : null;
    const isPdf = /\.pdf/i.test(url);
    const jumpUrl = (isPdf && page) ? (url + '#page=' + page) : url;
    const pageLabel = page ? ('頁 ' + page) : '';
    const sheetMetaRight = verified ? ('✅ 已核實' + (pageLabel ? ' · ' + pageLabel : '')) : pageLabel;

    let html = ''
      + '<div style="padding:0 4px">'
      +   '<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">'
      +     '<span class="m-result-source" style="font-size:13px">' + sourceIcon(sid) + ' ' + escapeHTML(displayName(sid, row.title)) + '</span>'
      +     (sheetMetaRight ? '<span style="font-size:11px;color:var(--m-text-muted);font-weight:600">' + sheetMetaRight + '</span>' : '')
      +   '</div>'
      +   ((row.title && SOURCE_LABEL[sid]) ? '<div style="font-size:13px;color:var(--m-text-secondary);margin-bottom:12px;line-height:1.5">' + escapeHTML(row.title) + '</div>' : '')
      +   '<div style="font-size:15px;line-height:1.7;color:var(--m-text-primary);margin-bottom:20px;white-space:pre-wrap">' + escapeHTML(row.text || '') + '</div>'
      +   (role ? '<div style="margin-bottom:16px"><span style="font-size:11px;color:var(--m-text-muted);font-weight:600;letter-spacing:0.08em;text-transform:uppercase">適用角色</span><div style="margin-top:6px"><span class="m-role-chip" style="background:var(--m-edb-deep)">' + escapeHTML(role) + '</span></div></div>' : '')
      +   (url ? '<a href="' + escapeHTML(jumpUrl) + '" target="_blank" rel="noopener" style="display:block;text-align:center;padding:14px;background:var(--m-edb-deep);color:#fff;border-radius:var(--m-r-pill);font-weight:700;text-decoration:none;font-size:15px;margin-top:8px">🔗 看 EDB 原文' + (isPdf && page ? '（第 ' + page + ' 頁）' : '') + '</a>' : '')
      + '</div>';
    content.innerHTML = html;

    sheet.setAttribute('aria-hidden', 'false');
    backdrop.setAttribute('aria-hidden', 'false');
  }

  function closeSheet() {
    const sheet = document.getElementById('m-sheet');
    const backdrop = document.getElementById('m-sheet-backdrop');
    if (sheet) sheet.setAttribute('aria-hidden', 'true');
    if (backdrop) backdrop.setAttribute('aria-hidden', 'true');
  }

  // ── 6b. 文件庫 (#guidelines) dedicated mobile render (Phase 2) ──
  // Category chips mirror desktop GuidelinesPanel CATS (zero-count cats hidden).
  const GUIDE_CATS = [
    { key: 'all',     label: '全部',     icon: '📋' },
    { key: '課程',     label: '課程',     icon: '📚' },
    { key: '財務採購',  label: '財務採購',  icon: '💰' },
    { key: '人力資源',  label: '人力資源',  icon: '👥' },
    { key: '學生事務',  label: '學生事務',  icon: '🎒' },
    { key: '學生安全',  label: '學生安全',  icon: '🛡️' },
    { key: '安全',      label: '科目安全',  icon: '⚠️' },
    { key: '活動',     label: '活動',     icon: '🏃' },
    { key: '津貼',     label: '津貼',     icon: '🏷️' },
    { key: '行政',     label: '行政',     icon: '🏫' },
    { key: '資訊科技',  label: '資訊科技',  icon: '💻' },
  ];
  const GUIDE_LEVELS = ['幼稚園', '小學', '中學', '特殊', '跨階段'];

  function guideYearCls(yr) {
    const y = parseInt(yr, 10);
    if (!yr || isNaN(y)) return 'm-gy-old';
    if (y >= 2024) return 'm-gy-new';
    if (y >= 2020) return 'm-gy-recent';
    return 'm-gy-old';
  }

  function guideFilterSort(reg, st) {
    let list = reg.filter(g => {
      if (st.cat !== 'all' && g.category !== st.cat) return false;
      if (st.level !== 'all' && g.level !== st.level) return false;
      if (st.q && (g.title || '').indexOf(st.q) < 0 && (g.titleShort || '').indexOf(st.q) < 0) return false;
      return true;
    });
    if (st.sort === 'year-desc') list = list.slice().sort((a, b) => (parseInt(b.year, 10) || 0) - (parseInt(a.year, 10) || 0));
    else if (st.sort === 'year-asc') list = list.slice().sort((a, b) => (parseInt(a.year, 10) || 0) - (parseInt(b.year, 10) || 0));
    else if (st.sort === 'title') list = list.slice().sort((a, b) => (a.title || '').localeCompare(b.title || '', 'zh-HK'));
    return list;
  }

  // Returns true once the shell is built; false if registry not yet available.
  function buildGuidelinesShell() {
    const reg = window.GUIDELINES_REGISTRY;
    if (!Array.isArray(reg) || !reg.length) return false;
    if (document.getElementById('m-guide-shell')) return true;

    try {
    const st = { cat: 'all', level: 'all', q: '', sort: 'year-desc' };
    const counts = { all: reg.length };
    reg.forEach(g => { counts[g.category] = (counts[g.category] || 0) + 1; });

    const shell = document.createElement('main');
    shell.id = 'm-guide-shell';
    shell.className = 'm-shell';

    let catChips = '<div class="m-guide-chips" id="m-guide-cats" role="tablist" aria-label="分類">';
    GUIDE_CATS.forEach(c => {
      if (c.key !== 'all' && !counts[c.key]) return;
      catChips += '<button type="button" class="m-guide-chip' + (c.key === st.cat ? ' is-active' : '') + '" data-cat="' + c.key + '">'
        + c.icon + ' ' + escapeHTML(c.label)
        + ' <span class="m-guide-chip-n">' + (counts[c.key] || 0) + '</span></button>';
    });
    catChips += '</div>';

    let levelChips = '<div class="m-guide-chips m-guide-chips-sub" id="m-guide-levels" role="tablist" aria-label="學習階段">';
    levelChips += '<button type="button" class="m-guide-chip m-chip-sm is-active" data-level="all">全部階段</button>';
    GUIDE_LEVELS.forEach(lv => {
      levelChips += '<button type="button" class="m-guide-chip m-chip-sm" data-level="' + lv + '">' + escapeHTML(lv) + '</button>';
    });
    levelChips += '</div>';

    const sortRow = '<div class="m-guide-sort" id="m-guide-sort">'
      + '<span class="m-guide-sort-lbl">排序</span>'
      + '<button type="button" class="m-guide-sortbtn is-active" data-sort="year-desc">最新</button>'
      + '<button type="button" class="m-guide-sortbtn" data-sort="year-asc">最舊</button>'
      + '<button type="button" class="m-guide-sortbtn" data-sort="title">名稱</button>'
      + '</div>';

    shell.innerHTML = ''
      + '<header class="m-guide-head">'
      +   '<div class="m-guide-eyebrow">EDB 官方政策指引</div>'
      +   '<h1 class="m-guide-title">指引文件</h1>'
      +   '<p class="m-guide-sub">共 ' + reg.length + ' 份官方指引文件，點擊即看 EDB 原文</p>'
      +   '<form class="m-guide-search" id="m-guide-search-form" autocomplete="off">'
      +     '<svg class="m-search-icon" width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>'
      +     '<input class="m-guide-search-input" id="m-guide-search-input" type="search" inputmode="search" placeholder="搜尋文件名稱…" />'
      +   '</form>'
      + '</header>'
      + catChips
      + levelChips
      + sortRow
      + '<section class="m-guide-list" id="m-guide-list" aria-live="polite"></section>';

    document.body.insertBefore(shell, document.body.firstChild);

    const listEl = shell.querySelector('#m-guide-list');

    function cardHTML(g) {
      const fmt = (g.format || '').toString();
      return '<a class="m-guide-card" href="' + escapeHTML(g.url || '#') + '" target="_blank" rel="noopener">'
        + '<div class="m-guide-card-top">'
        +   '<span class="m-guide-fmt">' + escapeHTML(fmt || '文件') + '</span>'
        +   '<span class="m-guide-year ' + guideYearCls(g.year) + '">' + escapeHTML(g.year || '—') + '</span>'
        + '</div>'
        + '<div class="m-guide-card-title">' + escapeHTML(g.title || '') + '</div>'
        + '<div class="m-guide-card-meta">'
        +   (g.level ? '<span class="m-guide-level">' + escapeHTML(g.level) + '</span>' : '')
        +   '<span class="m-guide-open">看 EDB 原文 ↗</span>'
        + '</div>'
        + '</a>';
    }

    function render() {
      const items = guideFilterSort(reg, st);
      if (!items.length) {
        listEl.innerHTML = '<div class="m-guide-empty">未找到符合條件的指引文件<br>可清除篩選或改用其他關鍵詞</div>';
        return;
      }
      let html = '<div class="m-guide-count">' + items.length + ' 份</div>';
      items.forEach(g => { html += cardHTML(g); });
      listEl.innerHTML = html;
    }

    function setActive(container, attr, val) {
      container.querySelectorAll('.m-guide-chip, .m-guide-sortbtn').forEach(b => {
        if (b.dataset[attr] != null) b.classList.toggle('is-active', b.dataset[attr] === val);
      });
    }

    shell.querySelector('#m-guide-cats').addEventListener('click', e => {
      const btn = e.target.closest('[data-cat]'); if (!btn) return;
      st.cat = btn.dataset.cat; setActive(btn.parentElement, 'cat', st.cat); render();
    });
    shell.querySelector('#m-guide-levels').addEventListener('click', e => {
      const btn = e.target.closest('[data-level]'); if (!btn) return;
      st.level = btn.dataset.level; setActive(btn.parentElement, 'level', st.level); render();
    });
    shell.querySelector('#m-guide-sort').addEventListener('click', e => {
      const btn = e.target.closest('[data-sort]'); if (!btn) return;
      st.sort = btn.dataset.sort; setActive(btn.parentElement, 'sort', st.sort); render();
    });
    const sForm = shell.querySelector('#m-guide-search-form');
    const sInput = shell.querySelector('#m-guide-search-input');
    sForm.addEventListener('submit', e => { e.preventDefault(); sInput.blur(); });
    sInput.addEventListener('input', () => { st.q = (sInput.value || '').trim(); render(); });

    render();
    return true;
    } catch (e) {
      if (window.console && console.warn) console.warn('[mobile.js] buildGuidelinesShell failed:', e);
      return false;
    }
  }

  // ── 6c. 範本下載 (#templates) — desktop-only feature notice (mobile) ──
  // 學校版政策範本為可編輯 Word 檔，需用電腦下載及編輯方有意義，故 mobile 不提供
  // 實際下載清單，改為「桌面版功能」說明 + desktop 範本下載面板截圖示意。
  // 純靜態畫面（無 fetch / 無外部依賴）→ 不會白屏、不影響現有 mobile 導航。
  function buildTemplatesShell() {
    if (document.getElementById('m-tpl-shell')) return true;
    const shell = document.createElement('main');
    shell.id = 'm-tpl-shell';
    shell.className = 'm-shell';
    shell.innerHTML = ''
      + '<header class="m-guide-head">'
      +   '<div class="m-guide-eyebrow">EDB 校本政策範本</div>'
      +   '<h1 class="m-guide-title">範本下載</h1>'
      +   '<p class="m-guide-sub">15 個合規範疇的學校版政策範本（可編輯 Word 檔），按校類下載。</p>'
      + '</header>'
      + '<section class="m-tpl-body">'
      +   '<div class="m-tpl-card">'
      +     '<div class="m-tpl-badge">💻 桌面版功能</div>'
      +     '<p class="m-tpl-lead">範本為<strong>可編輯的 Word（.docx）文件</strong>，需用電腦下載及填寫修訂方便使用。</p>'
      +     '<p class="m-tpl-note">請改用<strong>桌面瀏覽器</strong>開啟本平台的「範本下載」分頁，即可按範疇及校類（小／中／特／幼稚園）下載學校版政策範本草稿。</p>'
      +     '<figure class="m-tpl-shot">'
      +       '<img src="templates-preview.png" alt="桌面版「範本下載」面板示意截圖" loading="lazy" '
      +         'onerror="this.closest(\'.m-tpl-shot\').style.display=\'none\'" />'
      +       '<figcaption>桌面版「範本下載」面板示意</figcaption>'
      +     '</figure>'
      +   '</div>'
      + '</section>';
    document.body.insertBefore(shell, document.body.firstChild);
    return true;
  }

  // ── 7. Init ──
  function initMobileShell() {
    // Apply mobile-active flag for CSS hooks
    document.body.dataset.mobileActive = 'true';

    // Detect current page → render appropriate mobile content
    const here = (location.pathname.split('/').pop() || 'index.html');
    const hash = location.hash || '';

    // Resolve the page-specific shell builder WITHOUT throwing if it is
    // undefined. The desktop-hiding CSS is gated behind body.mobile-shell-active
    // (added only on success), so a missing builder = graceful fallback to the
    // normal desktop content on the small screen instead of a blank page.
    let shellBuilt = false;
    try {
      if (here === 'app.html' && hash === '#templates') {
        // 範本下載 = desktop 功能（學校版範本為可編輯 Word 檔，需電腦下載編輯）。
        // mobile 提供「桌面版功能」說明 + desktop 面板截圖示意，不在手機提供下載清單。
        if (typeof buildTemplatesShell === 'function') {
          buildTemplatesShell();
          shellBuilt = true;
        }
      } else if (here === 'app.html' && hash !== '#guidelines') {
        if (typeof buildAppShell === 'function') {
          buildAppShell();
          shellBuilt = true;
        }
      } else if (here === 'app.html' && hash === '#guidelines') {
        // Phase 2: dedicated 文件庫 mobile render. window.GUIDELINES_REGISTRY is
        // set by app.html's Babel-compiled script, which runs AFTER this deferred
        // file — so poll briefly, then gracefully fall back to revealing the React
        // #root panel if the registry never appears (e.g. React failed to load).
        let guideDone = false;
        const revealRoot = () => {
          const root = document.getElementById('root');
          if (root) {
            root.style.setProperty('display', 'block', 'important');
            root.style.setProperty('padding-bottom', '80px');
          }
        };
        const build = () => {
          if (guideDone) return true;
          if (buildGuidelinesShell()) {
            guideDone = true;
            document.body.classList.add('mobile-shell-active');
            return true;
          }
          return false;
        };
        if (!build()) {
          // Deterministic path: app.html fires this once the registry is exposed.
          window.addEventListener('k1-registry-ready', build, { once: true });
          // Poll backstop (~12s) in case the event was already missed; then fall
          // back to revealing the React #root panel (never a blank page).
          const tryBuild = (attempt) => {
            if (build()) return;
            if (attempt < 60) { setTimeout(() => tryBuild(attempt + 1), 200); return; }
            if (!guideDone) revealRoot();
          };
          tryBuild(0);
        }
      } else if (here === 'index.html' || here === '') {
        if (typeof buildIndexShell === 'function') {
          buildIndexShell();
          shellBuilt = true;
        }
      } else if (here === 'q.html') {
        if (typeof buildQShell === 'function') {
          buildQShell();
          shellBuilt = true;
        }
      } else if (here === 't-purchase.html') {
        if (typeof buildTPurchaseShell === 'function') {
          buildTPurchaseShell();
          shellBuilt = true;
        }
      }
    } catch (err) {
      // A builder existed but threw mid-render. Bail out of the takeover so the
      // desktop content stays visible rather than leaving a blank page.
      shellBuilt = false;
      if (window.console && console.warn) {
        console.warn('[mobile.js] shell builder failed; falling back to desktop content:', err);
      }
    }

    // Only now — after a shell actually built — activate the CSS that hides
    // the desktop chrome/content. No shell ⇒ no class ⇒ desktop content shows.
    if (shellBuilt) {
      document.body.classList.add('mobile-shell-active');
    }

    // Build tab bar (every page)
    buildTabBar();

    // S175 — First-run sequence: tour (if new) → role picker (if no role set yet)
    if (!getMobileTourDone()) {
      showMobileTour(function () { if (!getStoredRole()) showRolePicker(); });
    } else if (!getStoredRole()) {
      showRolePicker();
    }

    // Start placeholder rotation (only if .m-search-input exists on this page)
    startPlaceholderRotation();

    // Listen for viewport resize → flip viewport flag if user rotates / resizes.
    // Keep mobile-shell-active in sync: if we leave mobile, drop the class so
    // desktop CSS is unaffected; if we return to mobile, only re-add it when a
    // shell is actually present (never blank desktop content).
    MOBILE_QUERY.addEventListener('change', e => {
      document.documentElement.dataset.viewport = e.matches ? 'mobile' : 'desktop';
      document.body.dataset.mobileActive = e.matches ? 'true' : 'false';
      if (!e.matches) {
        document.body.classList.remove('mobile-shell-active');
      } else if (shellBuilt) {
        document.body.classList.add('mobile-shell-active');
      }
    });

    // Within app.html the 搜尋 (no hash) and 文件庫 (#guidelines) tabs are
    // same-document hash links — tapping them changes the hash WITHOUT reloading,
    // so the shell would not rebuild. Reload once on hash toggle to swap shells
    // cleanly (cached page, fast). Bind only once across re-inits.
    if (!hashReloadBound && here === 'app.html') {
      hashReloadBound = true;
      window.addEventListener('hashchange', () => { location.reload(); });
    }
  }

  // Eager init for the case where this script runs after the DOM is already
  // parsed (deferred scripts execute at readyState 'interactive', before
  // DOMContentLoaded). Placed at the END of the IIFE so every module-scope
  // const above is initialized first (avoids the TDZ described near the top).
  if (document.readyState !== 'loading') {
    document.body && (document.body.dataset.mobileActive = 'true');
    initMobileShell();
  }
})();
