/* ============================================================
 * feedback.js — 「提供意見」面板（共用：app.html / index.html / q.html / t-purchase.html，桌面與手機）
 *
 * Same shape as NetworkChecker's feedback panel and the playbook card
 * `feedback-google-form-prefill`: the page never sends anything itself. "送出" opens the
 * owner's Google Form in a new tab with type / text / context prefilled, and the user
 * presses 提交 there. So there is no backend, no Supabase table and no public e-mail,
 * and what users write never touches this repository.
 *
 * FORM_URL is the form's prefill link with three markers: =TYPE, =TEXT, =CTX.
 * Empty → every [data-k1-feedback] entry stays hidden and open() does nothing.
 * TYPES must match the form's choices word for word, or Google drops the prefill —
 * keep them plain text; the emoji live only on the buttons here.
 *
 * Context carries the platform version, desktop/mobile, page, browser/OS and, after a
 * search, its search_log id (a random UUID — lets dev/search_log_report.py line the
 * comment up with the search). The query itself is never put into the form.
 *
 * Version comes from this script's own ?v=, which the four HTML files bump with
 * PLATFORM_VERSION — no second copy of the number here.
 * ============================================================ */
(function () {
  'use strict';

  // Leonard's Google Form「政策搜尋平台・意見箱」(2026-10-30). entry.1324429019 (optional e-mail) is left for the user.
  const FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSdvfrq_Ft02VZ0ez1Rcx2c6mZrjAohWcx64gSayjlbdJ6GW9g/viewform?usp=pp_url&entry.93438649=TYPE&entry.638473992=TEXT&entry.821962211=CTX';

  const MAX = 1200;
  const TYPES = [
    ['bug', '🐞', '回報問題', '發生了甚麼？在哪一頁、哪一步？'],
    ['wrong', '📄', '資料有誤或過時', '哪一份文件或哪一個答案？正確的應該是甚麼？'],
    ['idea', '✨', '想加功能', '想加甚麼？會怎樣用？'],
    ['thanks', '💚', '想說聲謝謝', '哪裏用得好？'],
    ['other', '💭', '其他', '想說甚麼都可以。'],
  ];
  const typeOf = id => TYPES.find(t => t[0] === id) || TYPES[0];

  const script = document.currentScript;
  const version = (() => {
    const m = script && /[?&]v=([\w.-]+)/.exec(script.src);
    return m ? 'v' + m[1] : '';
  })();

  let type = 'bug', lastLogId = null, layer = null, opener = null;

  const formUrl = () => {
    const u = (window.K1_FEEDBACK_FORM || FORM_URL || '').trim();
    return /^https:\/\/docs\.google\.com\/forms\/.+=TYPE.*=TEXT.*=CTX/.test(u) ? u : '';
  };
  const enabled = () => !!formUrl();

  function context() {
    const ua = navigator.userAgent || '';
    const br = /Edg\//.test(ua) ? 'Edge' : /Firefox\//.test(ua) ? 'Firefox' : /Chrome\//.test(ua) ? 'Chrome' : /Safari\//.test(ua) ? 'Safari' : '其他瀏覽器';
    const os = /iPhone|iPad/.test(ua) ? 'iOS' : /Android/.test(ua) ? 'Android' : /Mac/.test(ua) ? 'macOS' : /Windows/.test(ua) ? 'Windows' : /Linux/.test(ua) ? 'Linux' : '';
    const page = (location.pathname.split('/').pop() || 'index.html').replace(/\.html$/, '') || 'index';
    const tab = (location.hash || '').replace(/^#/, '');
    const parts = [
      ['政策搜尋平台', version].filter(Boolean).join(' '),
      window.matchMedia('(max-width: 640px)').matches ? '手機' : '桌面',
      tab ? page + '#' + tab : page,
      [br, os].filter(Boolean).join(' / '),
    ];
    if (lastLogId) parts.push('搜尋編號 ' + lastLogId);
    return parts.join('・');
  }

  const CSS = ''
    + '.k1fb-layer{position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;background:rgba(20,24,20,.45);padding:16px}'
    + '.k1fb-layer[hidden]{display:none}'
    + '.k1fb-panel{background:#FBF9F3;color:#1B1F1A;width:100%;max-width:520px;max-height:calc(100vh - 32px);overflow:auto;border-radius:14px;box-shadow:0 18px 48px rgba(0,0,0,.25);padding:20px 20px 16px;font-family:inherit;font-size:14px;line-height:1.6}'
    + '.k1fb-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:6px}'
    + '.k1fb-head h2{margin:0;font-size:18px;color:#1F3A2E}'
    + '.k1fb-x{background:transparent;border:0;font-size:20px;line-height:1;cursor:pointer;color:#3A4238;padding:6px}'
    + '.k1fb-note{margin:0 0 12px;color:#3A4238;font-size:13px}'
    + '.k1fb-types{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}'
    + '.k1fb-types button{border:1px solid #C9D3CB;background:#fff;color:#1B1F1A;border-radius:99px;padding:6px 12px;font-size:13px;cursor:pointer;font-family:inherit}'
    + '.k1fb-types button[aria-pressed="true"]{background:#1F3A2E;border-color:#1F3A2E;color:#fff}'
    + '.k1fb-field{display:block}'
    + '.k1fb-field span{display:block;font-weight:600;margin-bottom:4px;font-size:13px}'
    + '.k1fb-field textarea{box-sizing:border-box;width:100%;min-height:120px;resize:vertical;border:1px solid #C9D3CB;border-radius:10px;padding:10px;font:inherit;font-size:16px;background:#fff;color:#1B1F1A}'
    + '.k1fb-count{display:block;text-align:right;font-size:12px;color:#6B7268}'
    + '.k1fb-count.near{color:#B45309}'
    + '.k1fb-ctx{margin:8px 0 14px;font-size:12px;color:#6B7268;word-break:break-all}'
    + '.k1fb-row{display:flex;flex-wrap:wrap;align-items:center;gap:8px}'
    + '.k1fb-btn{display:inline-flex;align-items:center;border:1px solid #1F3A2E;background:#fff;color:#1F3A2E;border-radius:8px;padding:8px 14px;font-size:14px;font-weight:600;cursor:pointer;text-decoration:none;font-family:inherit}'
    + '.k1fb-btn.primary{background:#1F3A2E;color:#fff}'
    + '.k1fb-msg{font-size:13px;color:#2E5A46}'
    + '.k1fb-msg.err{color:#B91C1C}'
    + '[data-k1-feedback].k1fb-link{background:none;border:0;padding:0;font:inherit;color:inherit;text-decoration:underline;text-underline-offset:2px;cursor:pointer}'
    + '@media (max-width:640px){.k1fb-layer{align-items:flex-end;padding:0}.k1fb-panel{max-width:none;border-radius:16px 16px 0 0;max-height:92vh;padding:18px 16px calc(16px + env(safe-area-inset-bottom))}}';

  function build() {
    if (layer) return layer;
    const style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);
    layer = document.createElement('div');
    layer.className = 'k1fb-layer';
    layer.hidden = true;
    layer.innerHTML = ''
      + '<div class="k1fb-panel" role="dialog" aria-modal="true" aria-labelledby="k1fb-title">'
      +   '<div class="k1fb-head"><h2 id="k1fb-title">提供意見</h2><button type="button" class="k1fb-x" data-k1fb="close" aria-label="關閉">✕</button></div>'
      +   '<p class="k1fb-note">一兩句就可以。按「送出」會開啟 Google 表單，再按「提交」便完成；版本及瀏覽器會自動填上，不會附上你搜尋的內容。</p>'
      +   '<div class="k1fb-types" role="group" aria-label="意見類型">'
      +     TYPES.map(t => '<button type="button" data-k1fb-type="' + t[0] + '">' + t[1] + ' ' + t[2] + '</button>').join('')
      +   '</div>'
      +   '<label class="k1fb-field"><span>內容</span><textarea id="k1fb-text" maxlength="' + MAX + '"></textarea></label>'
      +   '<small class="k1fb-count" id="k1fb-count"></small>'
      +   '<p class="k1fb-ctx" id="k1fb-ctx"></p>'
      +   '<div class="k1fb-row">'
      +     '<a class="k1fb-btn primary" id="k1fb-send" target="_blank" rel="noopener">送出</a>'
      +     '<button type="button" class="k1fb-btn" id="k1fb-copy">複製內容</button>'
      +     '<span class="k1fb-msg" id="k1fb-msg" aria-live="polite"></span>'
      +   '</div>'
      + '</div>';
    document.body.appendChild(layer);

    const text = layer.querySelector('#k1fb-text');
    const msg = layer.querySelector('#k1fb-msg');
    const say = (s, err) => { msg.textContent = s; msg.className = 'k1fb-msg' + (err ? ' err' : ''); };
    const empty = () => {
      if (text.value.trim()) return false;
      say('請先寫內容。', true); text.focus(); return true;
    };
    layer.addEventListener('click', e => {
      if (e.target === layer || e.target.closest('[data-k1fb="close"]')) { close(); return; }
      const t = e.target.closest('[data-k1fb-type]');
      if (t) { type = t.dataset.k1fbType; say(''); render(); }
    });
    layer.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    text.addEventListener('input', () => { say(''); render(); });
    layer.querySelector('#k1fb-send').addEventListener('click', e => {
      if (empty()) { e.preventDefault(); return; }
      say('已在新分頁開啟表單，請在表單按「提交」。');
    });
    layer.querySelector('#k1fb-copy').addEventListener('click', async () => {
      if (empty()) return;
      const t = typeOf(type);
      const body = '[政策搜尋平台意見] ' + t[2] + '\n\n' + text.value.trim().slice(0, MAX) + '\n\n— ' + context();
      try { await navigator.clipboard.writeText(body); say('已複製。'); }
      catch (err) { say('未能複製，請手動選取文字。', true); }
    });
    return layer;
  }

  function render() {
    if (!layer) return;
    const t = typeOf(type), text = layer.querySelector('#k1fb-text'), n = text.value.length, enc = encodeURIComponent;
    layer.querySelectorAll('[data-k1fb-type]').forEach(b => b.setAttribute('aria-pressed', b.dataset.k1fbType === type ? 'true' : 'false'));
    text.setAttribute('placeholder', t[3]);
    const count = layer.querySelector('#k1fb-count');
    count.textContent = n.toLocaleString('en') + ' / ' + MAX.toLocaleString('en');
    count.classList.toggle('near', n >= MAX - 200);
    layer.querySelector('#k1fb-ctx').textContent = '自動附上：' + context();
    layer.querySelector('#k1fb-send').href = formUrl()
      .replace(/=TYPE(?=&|$)/, '=' + enc(t[2]))
      .replace(/=TEXT(?=&|$)/, '=' + enc(text.value.slice(0, MAX)))
      .replace(/=CTX(?=&|$)/, '=' + enc(context()));
  }

  function open(opts) {
    if (!enabled()) return;
    opts = opts || {};
    if (opts.type && TYPES.some(t => t[0] === opts.type)) type = opts.type;
    if (opts.logId) lastLogId = opts.logId;
    opener = document.activeElement;
    build();
    layer.querySelector('#k1fb-msg').textContent = '';
    render();
    layer.hidden = false;
    document.documentElement.style.overflow = 'hidden';
    layer.querySelector('#k1fb-text').focus();
  }

  function close() {
    if (!layer || layer.hidden) return;
    layer.hidden = true;
    document.documentElement.style.overflow = '';
    if (opener && opener.focus) opener.focus();
  }

  // Show or hide every entry point; React re-renders call this again via refresh().
  function refresh() {
    const on = enabled();
    document.querySelectorAll('[data-k1-feedback]').forEach(el => { el.hidden = !on; });
  }

  document.addEventListener('click', e => {
    const el = e.target.closest('[data-k1-feedback]');
    if (!el) return;
    e.preventDefault();
    open({ type: el.dataset.k1Feedback || undefined, logId: el.dataset.k1LogId || undefined });
  });

  window.K1Feedback = {
    enabled, open, close, refresh,
    setLogId: id => { lastLogId = id || null; },
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', refresh);
  else refresh();
})();
