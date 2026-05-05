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

  // ── 6. Init ──
  function initMobileShell() {
    // Apply mobile-active flag for CSS hooks
    document.body.dataset.mobileActive = 'true';

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
