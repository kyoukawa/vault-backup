/* 全站共享交互：搜索 + 移动端抽屉。
   用法：<link rel="stylesheet" href="assets/kb-ui.css">
         <script src="assets/kb-ui.js" defer></script>
   会自动：
   - 把 [data-kb-search] 容器变成搜索框（带结果面板）
   - 在窄屏注入抽屉按钮，内容由 [data-kb-toc] 或自动生成的目录填充
*/
(function () {
  'use strict';

  var BASE = (function () {
    var s = document.querySelector('script[src$="kb-ui.js"]');
    if (!s) return '';
    var src = s.getAttribute('src');
    return src.replace(/assets\/kb-ui\.js.*$/, '');
  })();

  var IDMAP = {}, LINKMAP = {}, SEARCH = null, BODY = {}, BODY_Q = {};
  var ready = false;
  var pending = [];

  function idForPath(p) {
    for (var id in IDMAP) { if (IDMAP[id] === p) return id; }
    return p;
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function hi(text, terms) {
    var out = esc(text);
    terms.forEach(function (t) {
      if (!t) return;
      var re;
      try { re = new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'); }
      catch (e) { return; }
      out = out.replace(re, '<mark>$1</mark>');
    });
    return out;
  }

  // ---------- 数据 ----------
  function loadData() {
    var sameOrigin = /^https?:$/.test(location.protocol) || location.protocol === 'file:';
    var root = sameOrigin ? BASE : 'https://kb.is-a.dev/';
    var p1 = fetch(root + 'assets/ids.json?v=' + Date.now())
      .then(function (r) { return r.ok ? r.json() : {}; })
      .catch(function () { return {}; });
    var p2 = fetch(root + 'assets/linkmap.json?v=' + Date.now())
      .then(function (r) { return r.ok ? r.json() : {}; })
      .catch(function () { return {}; });
    var p3 = fetch(root + 'assets/search-index.json?v=' + Date.now())
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });

    return Promise.all([p1, p2, p3]).then(function (a) {
      IDMAP = a[0]; LINKMAP = a[1]; SEARCH = a[2];
      ready = true;
      pending.forEach(function (fn) { fn(); });
      pending = [];
    });
  }
  function whenReady(fn) { if (ready) fn(); else pending.push(fn); }

  function loadChunk(root, ci) {
    if (BODY_Q[ci]) return BODY_Q[ci];
    BODY_Q[ci] = fetch(root + 'assets/search-body/' + ci + '.json?v=' + Date.now())
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (d) { for (var k in d) BODY[k] = d[k]; return d; })
      .catch(function () { return {}; });
    return BODY_Q[ci];
  }

  // ---------- 搜索 ----------
  function mountSearch(el) {
    var root = el.getAttribute('data-kb-root') || BASE;
    el.classList.add('kb-search');
    el.innerHTML = '<input type="search" placeholder="搜全站…（按 / 聚焦）" '
      + 'autocomplete="off" spellcheck="false" aria-label="搜索全站">'
      + '<span class="kbd">/</span>';

    var inp = el.querySelector('input');
    var panel = document.createElement('div');
    panel.className = 'kb-hits';
    panel.hidden = true;
    el.parentNode.insertBefore(panel, el.nextSibling);

    var sel = -1, timer = null;

    function paint(res, terms) {
      sel = -1;
      if (!res.length) {
        panel.innerHTML = '<div class="none">没有匹配的笔记。试试更短的关键词。</div>';
        panel.hidden = false;
        return;
      }
      // 按库分组
      var groups = {}, order = [];
      res.forEach(function (r) {
        var top = r.f ? r.f.split('/')[0] : '根目录';
        if (!groups[top]) { groups[top] = []; order.push(top); }
        groups[top].push(r);
      });
      var html = '';
      order.forEach(function (g) {
        if (order.length > 1) html += '<div class="grphead">' + esc(g) + '</div>';
        groups[g].forEach(function (r) {
          var snip = r.s;
          var body = BODY[r.p];
          if (body) {
            var at = body.toLowerCase().indexOf(terms[0]);
            if (at > 60) snip = '…' + body.slice(Math.max(0, at - 40), at + 120);
          }
          html += '<a href="' + root + 'view.html?file=' + encodeURIComponent(idForPath(r.p)) + '">'
            + '<div class="ht">' + hi(r.t, terms) + '</div>'
            + '<div class="hp">' + hi(r.p, terms) + '</div>'
            + (snip ? '<div class="hs">' + hi(snip, terms) + '</div>' : '')
            + '</a>';
        });
      });
      panel.innerHTML = html;
      panel.hidden = false;
    }

    function doRun() {
      if (!SEARCH) return;
      var terms = inp.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      if (!terms.length) { panel.hidden = true; panel.innerHTML = ''; sel = -1; return; }

      var rows = SEARCH.rows || SEARCH;
      var res = rows.filter(function (r) {
        var hay = (r.t + ' ' + r.p + ' ' + (r.s || '')).toLowerCase();
        return terms.every(function (t) { return hay.indexOf(t) >= 0; });
      }).slice(0, 40);

      if (res.length < 8) {
        Promise.all([0,1,2,3,4,5,6,7,8,9].map(function (i) { return loadChunk(root, i); }))
          .then(function () {
            var seen = {};
            res.forEach(function (r) { seen[r.p] = 1; });
            var extra = rows.filter(function (r) {
              if (seen[r.p]) return false;
              var b = BODY[r.p];
              if (!b) return false;
              var lb = b.toLowerCase();
              return terms.every(function (t) { return lb.indexOf(t) >= 0; });
            }).slice(0, 40 - res.length);
            if (extra.length) paint(res.concat(extra), terms);
          });
      }
      paint(res, terms);
    }

    inp.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(doRun, 120);
    });
    inp.addEventListener('keydown', function (e) {
      var items = panel.querySelectorAll('a');
      if (e.key === 'ArrowDown') { e.preventDefault(); sel = Math.min(sel + 1, items.length - 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); sel = Math.max(sel - 1, 0); }
      else if (e.key === 'Enter') {
        e.preventDefault();
        (items[sel] || items[0] || {}).click && (items[sel] || items[0]).click();
        return;
      } else if (e.key === 'Escape') { panel.hidden = true; inp.blur(); return; }
      else return;
      items.forEach(function (a, i) { a.classList.toggle('sel', i === sel); });
      if (items[sel]) items[sel].scrollIntoView({ block: 'nearest' });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement !== inp
          && !/input|textarea|select/i.test((document.activeElement || {}).tagName || '')) {
        e.preventDefault(); inp.focus();
      }
    });

    whenReady(doRun);
  }

  // ---------- 目录数据 ----------
  function buildGroups() {
    var groups = {};
    for (var id in IDMAP) {
      var p = IDMAP[id];
      if (!p || !/\.md$/.test(p)) continue;
      var parts = p.split('/');
      var top = parts.length > 1 ? parts[0] : '根目录';
      (groups[top] = groups[top] || []).push(p);
    }
    for (var k in groups) groups[k].sort();
    return groups;
  }

  var ORDER = ['试卷库','语文语料库','英语语料库','化学错题本','学业档案',
               '阅读收集','读书','数学','每日题目','根目录'];

  // ---------- 移动端抽屉 ----------
  function mountDrawer(curPath) {
    if (document.querySelector('.kb-drawer-btn')) return;

    var btn = document.createElement('button');
    btn.className = 'kb-drawer-btn';
    btn.type = 'button';
    btn.setAttribute('aria-label', '打开目录');
    btn.textContent = '☰';

    var mask = document.createElement('div');
    mask.className = 'kb-drawer-mask';

    var drawer = document.createElement('nav');
    drawer.className = 'kb-drawer';
    drawer.setAttribute('aria-label', '站点目录');

    document.body.appendChild(btn);
    document.body.appendChild(mask);
    document.body.appendChild(drawer);

    function open() {
      render(curPath);
      drawer.classList.add('open');
      mask.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function close() {
      drawer.classList.remove('open');
      mask.classList.remove('open');
      document.body.style.overflow = '';
    }
    btn.addEventListener('click', open);
    mask.addEventListener('click', close);

    function render(cur) {
      var root = BASE;
      var groups = ready ? buildGroups() : {};
      var curLib = cur && cur.indexOf('/') > 0 ? cur.split('/')[0] : '根目录';

      var html = '<div class="dh"><b>目录</b>'
        + '<button type="button" aria-label="关闭">×</button></div>'
        + '<input class="dsearch" type="search" placeholder="搜全站…" autocomplete="off">';

      var keys = Object.keys(groups).sort(function (a, b) {
        var ia = ORDER.indexOf(a), ib = ORDER.indexOf(b);
        return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
      });

      keys.forEach(function (k) {
        var isCur = (k === curLib);
        html += '<div class="grp"><b>' + esc(k) + '</b>';
        if (!isCur) {
          var idxId = Object.keys(IDMAP).find(function (id) {
            var p = IDMAP[id];
            return p && (p.indexOf(k + '/INDEX') === 0 || p === k + '/INDEX.md');
          });
          if (idxId) {
            html += '<a href="' + root + 'view.html?file=' + encodeURIComponent(idxId) + '">'
              + '索引 · ' + groups[k].length + ' 篇</a>';
          }
          html += '</div>';
          return;
        }
        groups[k].slice(0, 36).forEach(function (p) {
          var label = p.split('/').pop().replace(/\.md$/, '').slice(0, 24);
          var cls = p === cur ? ' class="cur"' : '';
          html += '<a' + cls + ' href="' + root + 'view.html?file='
            + encodeURIComponent(idForPath(p)) + '">' + esc(label) + '</a>';
        });
        html += '</div>';
      });

      drawer.innerHTML = html;
      drawer.querySelector('.dh button').addEventListener('click', close);

      // 抽屉里的搜索：直接跳 view.html，用 ?q= 传过去
      var ds = drawer.querySelector('.dsearch');
      ds.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && ds.value.trim()) {
          location.href = root + 'view.html?q=' + encodeURIComponent(ds.value.trim());
        }
      });
    }
    whenReady(function () { if (drawer.classList.contains('open')) render(curPath); });
  }

  // ---------- 启动 ----------
  document.addEventListener('DOMContentLoaded', function () {
    var searchEls = document.querySelectorAll('[data-kb-search]');
    Array.prototype.forEach.call(searchEls, mountSearch);

    var body = document.body;
    var cur = body.getAttribute('data-kb-path') || '';
    // 若页面没声明当前路径，从 URL 猜
    if (!cur) {
      var m = location.search.match(/[?&]file=([^&]+)/);
      if (m) cur = decodeURIComponent(m[1]);
    }
    mountDrawer(cur);

    loadData();
  });
})();
