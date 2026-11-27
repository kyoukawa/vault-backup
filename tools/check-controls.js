// 控件回归检查：每页断言搜索框/按钮的实际计算样式，防止 CSS 解析错误静默失效
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const chrome = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const ROOT = "C:/Users/chuan/Documents/知识库";
const BASE = "http://127.0.0.1:8099/";

// 期望值（gxwtf 规格）
const EXP = {
  inputRadius: "10px",
  inputHeight: "32px",
  btnRadius: "8px",
  ctlHeight: "32px",
  ringWidth: "3px"
};

const PAGES = [
  ["exam.html", "搜索框、筛选芯片、更多按钮"],
  ["index.html", "搜索框、主入口卡片"],
  ["view.html?file=chem-elements", "搜索框"],
  ["writing-ocr.html", "搜索框、菜单按钮"],
  ["goal-board.html", "无控件"],
  ["latest.html", "无控件"]
];

// 注入到每页的探针：等 kb-ui 注入完再量。
// 两种形态都要认：共享组件 .kb-search（kb-ui.js 注入）、页面自带的 #q。
const PROBE = `
<script>
(function poll(n){
  var s = document.querySelector('.kb-search');
  var inp = s ? s.querySelector('input') : document.querySelector('#q, input.kb-input');
  if (!inp && n > 0) return setTimeout(function(){ poll(n-1); }, 80);
  setTimeout(function(){
    var out = {};
    if (s) out.search_display = getComputedStyle(s).display;
    if (inp) {
      var ci = getComputedStyle(inp);
      out.input_id = inp.id || inp.className;
      out.input_height = ci.height;
      out.input_radius = ci.borderRadius;
      out.input_font = ci.fontSize;
    }
    var btn = document.querySelector('.kb-btn, .more, .fc button');
    if (btn) {
      var cb = getComputedStyle(btn);
      out.btn_height = cb.height;
      out.btn_radius = cb.borderRadius;
    }
    // 焦点环：:focus-visible 不会被程序化 focus() 触发（headless 限制），
    // 所以这里只做静态检查——确认样式表里确实有 3px ring 规则、且没有 2px outline。
    var fv = document.querySelector('.kb-search, .kb-search input, #q, .kb-input')
      || document.body;
    out.has_ring_rule = false;
    out.has_old_outline = false;
    for (var i = 0; i < document.styleSheets.length; i++) {
      var ss = document.styleSheets[i], rules;
      try { rules = ss.cssRules; } catch (e) { continue; }
      for (var j = 0; j < rules.length; j++) {
        var rr = rules[j];
        if (!rr.cssText) continue;
        if (/focus/.test(rr.selectorText || '') && (rr.style.boxShadow || '').indexOf('--ring-w') >= 0) out.has_ring_rule = true;
        if (/focus/.test(rr.selectorText || '') && /2px/.test(rr.style.outlineWidth || '')) out.has_old_outline = true;
      }
    }
    if (!inp && !btn) out.note = '本页无协作控件';
    var d = document.createElement('div');
    d.id = '__kbprobe';
    d.textContent = JSON.stringify(out);
    d.style.display = 'none';
    document.body.appendChild(d);
  }, 200);
})(80);
</script>`;

function probe(page) {
  // 必须放 vault 根目录：放 .tmp/ 会让页面里 assets/… 的相对路径全 404。
  // 用 .tmp_ 前缀，.gitignore 里已有该规则，不会被提交。
  const tmpName = ".tmp_probe-" + page.replace(/[?=&\/]/g, "_") + ".html";
  const src = path.join(ROOT, page.split("?")[0]);
  let html = fs.readFileSync(src, "utf8");
  html = html.replace("</body>", PROBE + "</body>");
  fs.writeFileSync(path.join(ROOT, tmpName), html, "utf8");
  const dom = execSync(
    `"${chrome}" --headless=new --disable-gpu --window-size=1100,900 --virtual-time-budget=9000 --dump-dom "${BASE}${tmpName}"`,
    { maxBuffer: 32 * 1024 * 1024 }
  ).toString();
  fs.unlinkSync(path.join(ROOT, tmpName));
  const m = dom.match(/<div id="__kbprobe"[^>]*>([\s\S]*?)<\/div>/);
  if (!m) return { error: "探针未产出（页面 JS 没跑起来？）" };
  try { return JSON.parse(m[1].replace(/&quot;/g, '"')); } catch (e) { return { error: "解析失败: " + m[1] }; }
}

const failures = [];
console.log("控件回归检查（gxwtf 规格）\n");

for (const [page, desc] of PAGES) {
  let r;
  try { r = probe(page); } catch (e) { r = { error: e.message }; }
  const line = [];
  if (r.error) { line.push("  ✗ " + r.error); failures.push(page + ": " + r.error); }
  else {
    if (r.search_display !== undefined && r.search_display !== "flex") {
      line.push("  ✗ .kb-search display=" + r.search_display + "（应为 flex，CSS 可能被吃掉）");
      failures.push(page + " display");
    }
    if (r.input_radius !== undefined) {
      if (r.input_radius !== EXP.inputRadius) { line.push("  ✗ 输入框圆角 " + r.input_radius + "（应 " + EXP.inputRadius + "）"); failures.push(page + " input-radius"); }
      if (r.input_height !== EXP.inputHeight) { line.push("  ✗ 输入框高 " + r.input_height + "（应 " + EXP.inputHeight + "）"); failures.push(page + " input-height"); }
      if (r.input_radius === EXP.inputRadius && r.input_height === EXP.inputHeight) line.push("  ✓ 输入框#" + r.input_id + " " + r.input_height + " / 圆角 " + r.input_radius);
    }
    if (r.btn_radius !== undefined) {
      if (r.btn_radius !== EXP.btnRadius) { line.push("  ✗ 按钮圆角 " + r.btn_radius + "（应 " + EXP.btnRadius + "）"); failures.push(page + " btn-radius"); }
      else line.push("  ✓ 按钮 " + r.btn_height + " / 圆角 " + r.btn_radius);
    }
    // 焦点环规则：样式表里必须有 3px ring，且不能有 2px outline
    if (r.has_ring_rule !== undefined && (r.input_radius !== undefined || r.btn_radius !== undefined)) {
      if (!r.has_ring_rule) {
        line.push("  ✗ 样式表里找不到 3px focus ring 规则");
        failures.push(page + " no-ring-rule");
      } else if (r.has_old_outline) {
        line.push("  ✗ 仍有 2px outline 焦点框（会切圆角）");
        failures.push(page + " old-outline");
      } else {
        line.push("  ✓ 焦点环：3px ring，无旧 outline");
      }
    }
    if (r.note) line.push("  – " + r.note);
    if (r.search_display === undefined && r.input_radius === undefined && r.btn_radius === undefined && !r.note) {
      line.push("  – 本页无协作控件");
    }
  }
  console.log(page + "  (" + desc + ")");
  line.forEach(l => console.log(l));
}

console.log("\n" + (failures.length === 0
  ? "全部通过：" + PAGES.length + " 个页面"
  : "失败 " + failures.length + " 项：\n  " + failures.join("\n  ")));
process.exit(failures.length ? 1 : 0);
