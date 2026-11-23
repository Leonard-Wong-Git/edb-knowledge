/* ============================================================
 * move-notice.js — 遷址橫額（共用：app.html / index.html，桌面與手機）
 *
 * S256：網站由 policychecker.wongfu.net 遷往 policychecker.minny.app。舊網址由
 * 一個暫時的轉駁服務送到新網址同一頁，並加上 ?from=wongfu。只有帶着這個記號
 * 到達的人才看到橫額，請他把新網址存起來；按「知道了」後同一部裝置不再出現。
 * ?movenotice=1 可在任何時候預覽。轉駁於 2027 年 1 月底停用後，本檔可整個刪除
 * （連同兩個 HTML 的 <script> 一行）。
 *
 * 瀏覽器不容許網站代用戶加書籤；加到主畫面只有 Android／電腦版 Chrome、Edge
 * 可以一按完成（beforeinstallprompt），其餘顯示一行步驟。
 * 只用 textContent／createElement，不讀寫任何搜尋內容。
 * ============================================================ */
(function () {
  'use strict';

  var KEY = 'k1-move-notice';
  var NEW_HOST = 'policychecker.minny.app';

  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function write(v) { try { localStorage.setItem(KEY, v); } catch (e) { /* 私密模式：只在本次顯示 */ } }

  var params = new URLSearchParams(location.search);
  var arrivedFromOld = params.get('from') === 'wongfu';
  var preview = params.get('movenotice') === '1';

  if (arrivedFromOld) {
    if (read() !== 'done') write('show');
    // 瀏覽器按網址分開儲存，舊用戶到了新網址會被當作初次到訪。他們不是新用戶，
    // 不再播歡迎導覽。本檔必須排在 mobile.js 之前載入（它一執行就判斷導覽）。
    try {
      localStorage.setItem('k1_mobile_tour_v1', '1');
      localStorage.setItem('k1_tour_done_v1', '1');
    } catch (e) {}
    params.delete('from');
    var rest = params.toString();
    try { history.replaceState(null, '', location.pathname + (rest ? '?' + rest : '') + location.hash); } catch (e) {}
  }

  var installEvent = null;
  window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); installEvent = e; });

  var standalone = window.matchMedia && window.matchMedia('(display-mode: standalone)').matches
    || window.navigator.standalone === true;
  var ua = navigator.userAgent;
  var isIOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  var isAndroid = /Android/.test(ua);
  var isMac = /Mac/.test(navigator.platform || ua);
  var isPhoneOrTablet = isIOS || isAndroid;

  function shouldShow() {
    if (preview) return true;
    if (standalone) return false;
    return arrivedFromOld ? read() !== 'done' : read() === 'show';
  }

  function el(tag, text, style) {
    var n = document.createElement(tag);
    if (text) n.textContent = text;
    if (style) n.style.cssText = style;
    return n;
  }

  function render() {
    if (!shouldShow() || document.getElementById('k1-move-notice')) return;

    var bar = el('div', '', 'background:#1B1F1A;color:#F0EEE9;font:14px/1.5 "Noto Sans HK","PingFang HK","Microsoft JhengHei",sans-serif;padding:10px 16px;display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;position:relative;z-index:60');
    bar.id = 'k1-move-notice';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', '網址更新');

    var msg = el('span', '', 'flex:1 1 220px');
    msg.appendChild(document.createTextNode('網址已更新為 '));
    msg.appendChild(el('strong', NEW_HOST, 'color:#9acba4;font-weight:700'));

    var hint = el('span', '', 'flex-basis:100%;font-size:13px;color:#C9D3CC;display:none');

    var btn = 'font:inherit;font-size:14px;border-radius:8px;padding:8px 14px;min-height:40px;cursor:pointer';
    var save = el('button', isPhoneOrTablet ? '加到主畫面' : '加入書籤', btn + ';border:0;background:#9acba4;color:#1B1F1A;font-weight:700');
    save.type = 'button';
    save.addEventListener('click', function () {
      if (installEvent) {
        installEvent.prompt();
        installEvent = null;
        return;
      }
      hint.textContent = isIOS ? '按瀏覽器的「分享」，再選「加至主畫面」。'
        : isAndroid ? '按瀏覽器右上角「⋮」，再選「加到主畫面」。'
        : '按 ' + (isMac ? '⌘D' : 'Ctrl+D') + ' 即可加入書籤。';
      hint.style.display = 'block';
    });

    var ok = el('button', '知道了', btn + ';border:1px solid rgba(240,238,233,0.35);background:transparent;color:#F0EEE9');
    ok.type = 'button';
    ok.addEventListener('click', function () { write('done'); bar.remove(); });

    var actions = el('span', '', 'display:flex;gap:8px;flex:0 0 auto');
    actions.appendChild(save);
    actions.appendChild(ok);
    bar.appendChild(msg);
    bar.appendChild(actions);
    bar.appendChild(hint);
    document.body.insertBefore(bar, document.body.firstChild);
  }

  // 等手機版外殼先插入（它也放在 body 最前），橫額才放在最頂。
  if (document.readyState === 'complete') render();
  else window.addEventListener('load', render);
})();
