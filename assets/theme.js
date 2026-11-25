/* Theme toggle: warm light / warm dark, following the Claude palette.
   Injected into every page via <script defer>.
   URL override: ?theme=light or ?theme=dark (also writes to localStorage). */
(function(){
  function apply(t){
    document.documentElement.setAttribute('data-theme',t);
    try{localStorage.setItem('kb-theme',t);}catch(e){}
    var b=document.getElementById('theme-toggle');
    if(b){
      b.textContent=(t==='dark')?'☀':'☽'; // sun in dark, moon in light
      b.setAttribute('aria-pressed', t==='dark'?'true':'false');
    }
  }
  function init(){
    var saved=null; try{saved=localStorage.getItem('kb-theme');}catch(e){}
    // ?theme=light|dark wins over stored preference
    var q=null;
    try{ q=new URLSearchParams(location.search).get('theme'); }catch(e){}
    if(q==='light'||q==='dark') saved=q;
    var sys=(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches)?'dark':'light';
    apply(saved||sys);
    if(document.getElementById('theme-toggle')) return;
    var b=document.createElement('button');
    b.id='theme-toggle'; b.type='button';
    b.setAttribute('aria-label','切换深色/浅色主题');
    b.title='切换深色 / 浅色';
    b.onclick=function(){
      var cur=document.documentElement.getAttribute('data-theme');
      apply(cur==='dark'?'light':'dark');
    };
    document.body.appendChild(b);
    apply(document.documentElement.getAttribute('data-theme')||'light');
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
  else init();
})();
