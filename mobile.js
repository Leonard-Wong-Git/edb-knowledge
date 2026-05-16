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
  // If body not yet parsed, wait
  document.addEventListener('DOMContentLoaded', () => {
    document.body.dataset.mobileActive = 'true';
    initMobileShell();
  });
  if (document.readyState !== 'loading') {
    document.body && (document.body.dataset.mobileActive = 'true');
    initMobileShell();
  }

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

  function getStoredRole() {
    try { return localStorage.getItem(ROLE_STORAGE_KEY); }
    catch (_) { return null; }
  }
  function storeRole(key) {
    try { localStorage.setItem(ROLE_STORAGE_KEY, key); } catch (_) {}
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
    html += '<div class="m-role-picker-eyebrow">K1 知識平台 · 第一次使用</div>';
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

  // ── 5. Bottom tab bar (3 entries: 搜尋 / 文件庫 / 平台介紹) ──
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
      { key: 'search',     icon: '🔍', label: '搜尋',       href: 'app.html',                match: ['app.html', 'q.html'] },
      { key: 'library',    icon: '📚', label: '文件庫',     href: 'app.html#guidelines',     match: ['#guidelines'] },
      { key: 'about',      icon: 'ℹ️', label: '平台介紹',   href: 'index.html',              match: ['index.html', ''] },
    ];

    TABS.forEach(t => {
      const isActive =
        (t.key === 'library' && hash === '#guidelines') ||
        (t.key === 'search'  && (here === 'app.html' || here === 'q.html') && hash !== '#guidelines') ||
        (t.key === 'about'   && (here === 'index.html' || here === '') && hash !== '#guidelines');
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

  const sourceIcon = id => {
    if (!id) return '📄';
    if (id.indexOf('sag') >= 0 || id === 'g24') return '📗';
    if (id.indexOf('coa') >= 0) return '📘';
    if (id.indexOf('g0') === 0 || id.indexOf('g1') === 0) return '📋';
    if (id.indexOf('role_facts') === 0) return '✅';
    if (id.indexOf('edbc') >= 0) return '📄';
    return '📑';
  };

  // Build app.html mobile shell: hero + search + results + sheet
  function buildAppShell() {
    if (document.getElementById('m-app-shell')) return;
    const shell = document.createElement('main');
    shell.id = 'm-app-shell';
    shell.className = 'm-shell';
    shell.innerHTML = ''
      + '<section class="m-hero">'
      +   '<div class="m-hero-eyebrow">K1 知識平台 · 香港學校管治</div>'
      +   '<h1 class="m-hero-title">查找有根有據的政策答案</h1>'
      +   '<p class="m-hero-desc">輸入問題，即時比對 EDB 已核實事實及原文片段。</p>'
      +   '<form class="m-search" id="m-search-form" autocomplete="off">'
      +     '<svg class="m-search-icon" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>'
      +     '<input class="m-search-input" id="m-search-input" type="search" inputmode="search" placeholder="教師病假上限多少天？" />'
      +   '</form>'
      + '</section>'
      + '<section class="m-result-list" id="m-result-list" aria-live="polite"></section>'
      + '<div class="m-sheet-backdrop" id="m-sheet-backdrop" aria-hidden="true"></div>'
      + '<aside class="m-sheet" id="m-sheet" aria-hidden="true" role="dialog" aria-modal="true">'
      +   '<div class="m-sheet-handle"></div>'
      +   '<div id="m-sheet-content"></div>'
      + '</aside>';
    document.body.insertBefore(shell, document.body.firstChild);

    const form = document.getElementById('m-search-form');
    const input = document.getElementById('m-search-input');
    const list = document.getElementById('m-result-list');

    // Initial empty state
    renderEmpty(list);

    form.addEventListener('submit', e => {
      e.preventDefault();
      const q = (input.value || '').trim();
      if (!q) return;
      input.blur();
      runSearch(q, list);
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
      const resp = await fetch(BACKEND_URL + '/api/search/combined', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, top_k: 8, min_score: 0.15, synthesize: true, enable_topic_filter: true }),
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
           + '</div>';
    }
    results.forEach((r, idx) => {
      const sid = r.source_id || '';
      const channel = r.channel || (r.content_type === 'approved_fact' ? 'A' : 'B');
      const channelLabel = (r.content_type === 'approved_fact') ? '已核實' : '原文';
      const score = (typeof r.score === 'number') ? r.score.toFixed(2) : '';
      html += '<button class="m-result-card" data-idx="' + idx + '" type="button">'
           +   '<div class="m-result-meta">'
           +     '<span class="m-result-source">' + sourceIcon(sid) + ' ' + escapeHTML(sourceLabel(sid)) + '</span>'
           +     '<span style="font-size:11px;color:var(--m-text-muted);font-weight:600">' + channelLabel + ' · ' + score + '</span>'
           +   '</div>'
           +   '<div class="m-result-content">' + escapeHTML(r.text || '') + '</div>'
           + '</button>';
    });
    list.innerHTML = html;

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
    const channelLabel = (row.content_type === 'approved_fact') ? '已核實資料' : '來源文件原文';
    const role = row.role || '';

    let html = ''
      + '<div style="padding:0 4px">'
      +   '<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">'
      +     '<span class="m-result-source" style="font-size:13px">' + sourceIcon(sid) + ' ' + escapeHTML(sourceLabel(sid)) + '</span>'
      +     '<span style="font-size:11px;color:var(--m-text-muted);font-weight:600">' + channelLabel + '</span>'
      +   '</div>'
      +   (row.title ? '<div style="font-size:13px;color:var(--m-text-secondary);margin-bottom:12px;line-height:1.5">' + escapeHTML(row.title) + '</div>' : '')
      +   '<div style="font-size:15px;line-height:1.7;color:var(--m-text-primary);margin-bottom:20px;white-space:pre-wrap">' + escapeHTML(row.text || '') + '</div>'
      +   (role ? '<div style="margin-bottom:16px"><span style="font-size:11px;color:var(--m-text-muted);font-weight:600;letter-spacing:0.08em;text-transform:uppercase">適用角色</span><div style="margin-top:6px"><span class="m-role-chip" style="background:var(--m-edb-deep)">' + escapeHTML(role) + '</span></div></div>' : '')
      +   (url ? '<a href="' + escapeHTML(url) + '" target="_blank" rel="noopener" style="display:block;text-align:center;padding:14px;background:var(--m-edb-deep);color:#fff;border-radius:var(--m-r-pill);font-weight:700;text-decoration:none;font-size:15px;margin-top:8px">🔗 看 EDB 原文</a>' : '')
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

  // ── 7. Init ──
  function initMobileShell() {
    // Apply mobile-active flag for CSS hooks
    document.body.dataset.mobileActive = 'true';

    // Detect current page → render appropriate mobile content
    const here = (location.pathname.split('/').pop() || 'index.html');
    const hash = location.hash || '';

    if (here === 'app.html' && hash !== '#guidelines') {
      buildAppShell();
    } else if (here === 'app.html' && hash === '#guidelines') {
      // Fallback: 暫露 React GuidelinesPanel（下節做專用 mobile render）
      const tryShow = () => {
        const root = document.getElementById('root');
        if (root) {
          root.style.setProperty('display', 'block', 'important');
          root.style.setProperty('padding-bottom', '80px');
        }
      };
      tryShow();
      setTimeout(tryShow, 500);
    } else if (here === 'index.html' || here === '') {
      buildIndexShell();
    } else if (here === 'q.html') {
      buildQShell();
    } else if (here === 't-purchase.html') {
      buildTPurchaseShell();
    }

    // Build tab bar (every page)
    buildTabBar();

    // Show role picker on first run (skip if already chosen)
    if (!getStoredRole()) {
      showRolePicker();
    }

    // Start placeholder rotation (only if .m-search-input exists on this page)
    startPlaceholderRotation();

    // Listen for viewport resize → flip viewport flag if user rotates / resizes
    MOBILE_QUERY.addEventListener('change', e => {
      document.documentElement.dataset.viewport = e.matches ? 'mobile' : 'desktop';
      document.body.dataset.mobileActive = e.matches ? 'true' : 'false';
    });
  }
})();
