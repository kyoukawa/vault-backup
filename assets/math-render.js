/* 全站公式渲染（KaTeX）。
   用法：<script src="assets/math-render.js"></script>
   两种场景：
     1) Markdown 页面（view.html）：marked 之前先 kbMath.extract()，渲染后 kbMath.render(el, store)
     2) 静态 HTML（latest.html）：直接 kbMath.typeset(document.body)

   为什么不直接对渲染后的 DOM 跑 /\$([^$]+?)\$/：
     - 行内正则会把 $$…$$ 拆成 $ + … + $，块级公式变行内，页面上留两个孤零零的 $
     - marked 会先吃掉公式里的 _ 和 *，\mathrm{Na_2O_2} 变成 \mathrm{Na<em>2O</em>2}
   所以 Markdown 场景必须"先摘出来 → 占位符 → 再贴回去"。 */

(function (global) {
  'use strict';

  var SENTINEL = '\u0001';
  var PLACEHOLDER = new RegExp(SENTINEL + 'M(\\d+)' + SENTINEL, 'g');

  // 行内 $…$ 的识别规则（跟 pandoc / KaTeX 自动渲染一致）：
  //   开 $ 后面不能紧跟空白，闭 $ 前面不能有空白、后面不能紧跟数字。
  // 没有这条，"Adult Economy $232 $275" 这种价目表会被当成公式，
  // 两个 $ 消失、数字被渲染 —— 英语卷的价格题实测踩过。
  function inlineMath(text, put) {
    var out = '', i = 0, n = text.length;
    while (i < n) {
      var start = text.indexOf('$', i);
      if (start < 0) { out += text.slice(i); break; }
      out += text.slice(i, start);
      var after = text.charAt(start + 1);
      if (!after || /\s/.test(after)) { out += '$'; i = start + 1; continue; }
      var end = -1;
      for (var j = start + 1; j < n; j++) {
        var c = text.charAt(j);
        if (c === '\n') break;
        if (c !== '$') continue;
        if (!/\s/.test(text.charAt(j - 1)) && !/^\d/.test(text.charAt(j + 1) || '')) end = j;
        break;                       // 只认同一行的第一个候选，不合格就放弃这个开 $
      }
      if (end < 0) { out += '$'; i = start + 1; continue; }
      out += put(text.slice(start + 1, end), false);
      i = end + 1;
    }
    return out;
  }

  // 把 $…$ / $$…$$ 换成占位符，返回 { text, store }
  function extract(text) {
    var store = [];
    function put(tex, display) {
      store.push({ tex: tex.trim(), display: display });
      return SENTINEL + 'M' + (store.length - 1) + SENTINEL;
    }
    // 围栏代码块里的 $ 不是公式：按 ``` 切成奇数段跳过
    var parts = text.split(/(```[\s\S]*?```)/);
    for (var i = 0; i < parts.length; i++) {
      if (i % 2 === 1) continue;
      var s = parts[i];
      s = s.replace(/\$\$([\s\S]+?)\$\$/g, function (m, tex) { return put(tex, true); });
      parts[i] = inlineMath(s, put);
    }
    return { text: parts.join(''), store: store };
  }

  function isSkipped(node) {
    var p = node.parentNode;
    return !!p && /^(CODE|PRE|SCRIPT|STYLE|TEXTAREA)$/.test(p.nodeName);
  }

  function collect(root) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    var nodes = [], n;
    while ((n = walker.nextNode())) {
      if (!isSkipped(n)) nodes.push(n);
    }
    return nodes;
  }

  function makeSpan(tex, display) {
    var span = document.createElement('span');
    try {
      katex.render(tex, span, { throwOnError: false, displayMode: !!display });
    } catch (e) {
      span.textContent = (display ? '$$' : '$') + tex + (display ? '$$' : '$');
    }
    return span;
  }

  // 把占位符换成公式
  function render(root, store) {
    if (!store || !store.length) return;
    function go() {
      if (!global.katex) return setTimeout(go, 100);
      collect(root).forEach(function (node) {
        var txt = node.nodeValue;
        if (!txt || txt.indexOf(SENTINEL) < 0) return;
        PLACEHOLDER.lastIndex = 0;
        var frag = document.createDocumentFragment(), m, last = 0;
        while ((m = PLACEHOLDER.exec(txt))) {
          if (m.index > last) frag.appendChild(document.createTextNode(txt.slice(last, m.index)));
          var item = store[+m[1]];
          frag.appendChild(makeSpan(item.tex, item.display));
          last = m.index + m[0].length;
        }
        if (last < txt.length) frag.appendChild(document.createTextNode(txt.slice(last)));
        node.parentNode.replaceChild(frag, node);
      });
      // 只包一个块级公式的 <p> 拆掉，免得外面多一层行距
      Array.prototype.forEach.call(root.querySelectorAll('p'), function (p) {
        if (p.childNodes.length === 1 && p.firstChild.nodeType === 1 &&
            p.firstChild.classList.contains('katex-display')) {
          p.parentNode.replaceChild(p.firstChild, p);
        }
      });
    }
    go();
  }

  // 静态 HTML 用：每个文本节点单独走一遍 extract，再按占位符还原
  function typeset(root) {
    function go() {
      if (!global.katex) return setTimeout(go, 100);
      collect(root).forEach(function (node) {
        var txt = node.nodeValue;
        if (!txt || txt.indexOf('$') < 0) return;
        var parsed = extract(txt);
        if (!parsed.store.length) return;
        PLACEHOLDER.lastIndex = 0;
        var frag = document.createDocumentFragment(), m, last = 0;
        while ((m = PLACEHOLDER.exec(parsed.text))) {
          if (m.index > last) frag.appendChild(document.createTextNode(parsed.text.slice(last, m.index)));
          var item = parsed.store[+m[1]];
          frag.appendChild(makeSpan(item.tex, item.display));
          last = m.index + m[0].length;
        }
        if (last < parsed.text.length) frag.appendChild(document.createTextNode(parsed.text.slice(last)));
        node.parentNode.replaceChild(frag, node);
      });
    }
    go();
  }

  global.kbMath = { extract: extract, render: render, typeset: typeset, SENTINEL: SENTINEL };
})(window);
