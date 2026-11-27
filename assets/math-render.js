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
      s = s.replace(/\$([^$\n]+?)\$/g, function (m, tex) { return put(tex, false); });
      parts[i] = s;
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

  // 静态 HTML 用：直接扫文本节点，先认 $$…$$ 再认 $…$
  function typeset(root) {
    function go() {
      if (!global.katex) return setTimeout(go, 100);
      collect(root).forEach(function (node) {
        var txt = node.nodeValue;
        if (!txt || txt.indexOf('$') < 0) return;
        var frag = document.createDocumentFragment();
        var re = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g;
        var m, last = 0;
        while ((m = re.exec(txt))) {
          if (m.index > last) frag.appendChild(document.createTextNode(txt.slice(last, m.index)));
          var display = m[1] !== undefined;
          frag.appendChild(makeSpan(display ? m[1] : m[2], display));
          last = m.index + m[0].length;
        }
        if (last < txt.length) frag.appendChild(document.createTextNode(txt.slice(last)));
        if (last > 0) node.parentNode.replaceChild(frag, node);
      });
    }
    go();
  }

  global.kbMath = { extract: extract, render: render, typeset: typeset, SENTINEL: SENTINEL };
})(window);
