(() => {
  'use strict';
  const data=JSON.parse(document.getElementById('reader-data').textContent);
  const locales={en:'en-US',ja:'ja-JP',ko:'ko-KR',zh:'zh-CN'};
  const labels={ja:{name:'日本語',show:'訳を表示',hide:'訳を隠す'},ko:{name:'한국어',show:'번역 보기',hide:'번역 숨기기'},zh:{name:'简体中文',show:'显示翻译',hide:'隐藏翻译'}};
  const prefs={get(key,fallback){try{return localStorage.getItem('earth-explorers-'+key)||fallback;}catch{return fallback;}},set(key,value){try{localStorage.setItem('earth-explorers-'+key,value);}catch{}}};
  const language=document.getElementById('language'),size=document.getElementById('text-size'),all=document.getElementById('translations-all');
  let code=prefs.get('language','en');if(!locales[code])code='en';language.value=code;
  const translations=data.paragraphs.map(p=>{
    const block=document.getElementById(p.id),support=document.createElement('div'),head=document.createElement('div'),tag=document.createElement('span'),toggle=document.createElement('button'),text=document.createElement('p');
    support.className='translation';head.className='translation-head';toggle.type='button';text.id=p.id+'-translation';toggle.setAttribute('aria-controls',text.id);
    head.append(tag,toggle);support.append(head,text);block.append(support);
    toggle.addEventListener('click',()=>{text.hidden=!text.hidden;toggle.setAttribute('aria-expanded',String(!text.hidden));toggle.textContent=text.hidden?labels[code].show:labels[code].hide;});
    return {p,support,tag,toggle,text};
  });
  function render(){
    translations.forEach(({p,support,tag,toggle,text})=>{support.hidden=code==='en';if(code==='en')return;support.lang=locales[code];tag.textContent=labels[code].name;text.textContent=p[code];text.hidden=true;toggle.textContent=labels[code].show;toggle.setAttribute('aria-expanded','false');});
    document.querySelectorAll('[data-localized]').forEach(el=>{el.hidden=code==='en';if(code!=='en'){el.textContent=data.localized[el.dataset.localized][code];el.lang=locales[code];}});
    all.hidden=code==='en';all.setAttribute('aria-pressed','false');all.textContent='Show all translations';
  }
  function textSize(){document.documentElement.style.setProperty('--reading-size',size.value+'px');}
  const savedSize=prefs.get('size','20');if(['20','23','26'].includes(savedSize))size.value=savedSize;textSize();
  language.addEventListener('change',()=>{code=language.value;prefs.set('language',code);render();});
  size.addEventListener('change',()=>{prefs.set('size',size.value);textSize();});
  all.addEventListener('click',()=>{const open=all.getAttribute('aria-pressed')!=='true';translations.forEach(({text,toggle})=>{text.hidden=!open;toggle.textContent=open?labels[code].hide:labels[code].show;toggle.setAttribute('aria-expanded',String(open));});all.setAttribute('aria-pressed',String(open));all.textContent=open?'Hide all translations':'Show all translations';});
  document.getElementById('print-reader').addEventListener('click',()=>window.print());
  const settings=document.querySelector('.reading-settings');
  document.addEventListener('pointerdown',event=>{if(settings.open&&!settings.contains(event.target))settings.open=false;});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&settings.open){settings.open=false;settings.querySelector('summary').focus();}});
  render();
})();
