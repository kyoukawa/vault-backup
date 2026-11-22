/* Theme toggle: GitHub light/dark. Injected into every page via <script defer>. */
(function(){
  function apply(t){
    document.documentElement.setAttribute('data-theme',t);
    try{localStorage.setItem('kb-theme',t);}catch(e){}
    var b=document.getElementById('theme-toggle');
    if(b) b.textContent=(t==='dark')?'\u2600':'\u263D'; // sun in dark, moon in light
  }
  function init(){
    var saved=null; try{saved=localStorage.getItem('kb-theme');}catch(e){}
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
