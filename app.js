(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('reader-data').textContent);
  const locales = {en:'en-US',ja:'ja-JP',ko:'ko-KR',zh:'zh-CN'};
  const names = {en:'English',ja:'日本語',ko:'한국어',zh:'简体中文'};
  const listenLabels = {en:'Listen',ja:'聞く',ko:'듣기',zh:'朗读'};
  const ui = {
    ja:{hide:'訳を隠す',show:'訳を表示',section:'この部分を聞く'},
    ko:{hide:'번역 숨기기',show:'번역 보기',section:'이 부분 듣기'},
    zh:{hide:'隐藏翻译',show:'显示翻译',section:'朗读本节'}
  };
  const language = document.getElementById('language');
  const status = document.getElementById('audio-status');
  const pause = document.getElementById('pause');
  const stop = document.getElementById('stop');
  const rate = document.getElementById('rate');
  const englishVoice = document.getElementById('english-voice');
  const homeVoice = document.getElementById('home-voice');
  const hasSpeech = 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
  const synth = hasSpeech ? window.speechSynthesis : null;
  const prefs = {get(key,fallback){try{return localStorage.getItem('earth-explorers-'+key)||fallback;}catch{return fallback;}},set(key,value){try{localStorage.setItem('earth-explorers-'+key,value);}catch{}}};
  let code = prefs.get('language','en');
  if (!locales[code]) code='en';
  let voices=[], generation=0, currentUtterance=null, narrationPlayer=null, playbackKind=null, playing=false, paused=false, highlighted=null;
  language.value=code;
  const savedRate=prefs.get('rate','0.85');
  if(rate && [...rate.options].some(o=>o.value===savedRate))rate.value=savedRate;
  const size=document.getElementById('text-size');
  const savedSize=prefs.get('size','20');
  if(size && ['20','23','26'].includes(savedSize)){size.value=savedSize;document.documentElement.style.setProperty('--reading-size',savedSize+'px');}
  const baseLang=lang=>lang.toLowerCase().replace('_','-').split('-')[0];
  const novelty=/^(Albert|Bad News|Bahh|Bells|Boing|Bubbles|Cellos|Good News|Hysterical|Jester|Junior|Organ|Superstar|Trinoids|Whisper|Wobble|Zarvox)$/i;
  function matchingVoices(lang){return voices.filter(v=>baseLang(v.lang)===lang&&!novelty.test(v.name));}
  function selectVoice(lang){
    const selected=prefs.get('voice-'+lang,'');
    const options=matchingVoices(lang);
    const rank=v=>(/natural|premium|enhanced|neural/i.test(v.name)?100:0)+(/Google.*English|Samantha|Daniel|Karen|Moira|Kyoko|Yuna|Tingting/i.test(v.name)?40:0)+(v.lang.toLowerCase()===locales[lang].toLowerCase()?20:0)+(v.localService?5:0);
    return options.find(v=>v.voiceURI===selected)||options.sort((a,b)=>rank(b)-rank(a))[0]||null;
  }
  function voiceOptions(select,lang){
    if(!select)return;
    select.replaceChildren();
    const list=matchingVoices(lang);
    if(data.narration?.[lang]){
      select.add(new Option('Included narration (recommended)',''));
      list.forEach(v=>select.add(new Option(v.name+' · '+v.lang,v.voiceURI)));
      select.disabled=false;
      const chosen=prefs.get('voice-'+lang,'');select.value=list.some(v=>v.voiceURI===chosen)?chosen:'';
      return;
    }
    if(!list.length){select.add(new Option(hasSpeech?'No matching voice available':'Read-aloud unavailable',''));select.disabled=true;return;}
    select.disabled=false;
    list.forEach(v=>select.add(new Option(v.name+' · '+v.lang,v.voiceURI)));
    select.value=selectVoice(lang).voiceURI;
  }
  function updateVoices(){
    voices=hasSpeech?synth.getVoices():[];
    voiceOptions(englishVoice,'en');
    const group=document.getElementById('home-voice-group');
    if(group)group.hidden=code==='en';
    if(code!=='en')voiceOptions(homeVoice,code);
    document.querySelectorAll('[data-speak]').forEach(button=>{
      const lang=button.dataset.speak==='home'?code:'en';
      const available=Boolean(data.narration?.[lang]) || (hasSpeech && (lang==='en'||matchingVoices(lang).length>0));
      button.disabled=!available;
      if(!available)button.title=hasSpeech?names[lang]+' voice is not available on this device.':'Read-aloud is not supported by this browser.';
      else button.removeAttribute('title');
    });
    const note=document.getElementById('voice-note');
    if(note)note.textContent=data.narration?'Included narration gives you the same clear voice on different devices. You can also choose a device voice.':!hasSpeech?'Read-aloud is unavailable in this browser. You can still read and print every page.':code!=='en'&&!matchingVoices(code).length?names[code]+' audio is not available on this device. English audio and written translations are available.':'Clear device voices are selected automatically. You can choose another voice here.';
  }
  function clearHighlight(){if(highlighted)highlighted.classList.remove('speaking');highlighted=null;}
  function highlight(target,lang){
    clearHighlight();highlighted=document.getElementById(target);
    if(!highlighted)return;
    if(lang!=='en'&&highlighted.classList.contains('translation-content')){
      highlighted.hidden=false;const toggle=highlighted.parentElement.querySelector('.translation-head button');
      if(toggle){toggle.setAttribute('aria-expanded','true');toggle.textContent=ui[lang].hide;}
    }
    highlighted.classList.add('speaking');
  }
  function controls(active){
    playing=active;if(pause)pause.disabled=!active;if(stop)stop.disabled=!active;
    const group=document.getElementById('playback-controls');if(group)group.hidden=!active;
  }
  function stopSpeech(message=''){
    generation++;if(synth)synth.cancel();
    if(narrationPlayer){narrationPlayer.pause();narrationPlayer.removeAttribute('src');narrationPlayer.load();narrationPlayer=null;}
    playbackKind=null;currentUtterance=null;paused=false;controls(false);clearHighlight();
    if(pause)pause.textContent='Pause';if(status)status.textContent=message;
  }
  function cleanSpeech(text,lang){
    let value=text.replace(/_{2,}/g,' blank ');
    if(lang==='ja')value=value.replace(/([\p{Script=Han}]+)（([\p{Script=Hiragana}]+)）/gu,'$2');
    return value.replace(/\s+/g,' ').trim();
  }
  function chunks(text,lang){
    const sentences=cleanSpeech(text,lang).match(/[^.!?。！？]+[.!?。！？]?/g)||[];
    return sentences.flatMap(sentence=>{
      const pieces=[];let rest=sentence.trim();
      while(rest.length>220){let cut=rest.lastIndexOf(' ',200);if(cut<80)cut=200;pieces.push(rest.slice(0,cut));rest=rest.slice(cut).trim();}
      if(rest)pieces.push(rest);return pieces;
    });
  }
  function speakWithDevice(items,lang,label){
    if(!hasSpeech)return;
    stopSpeech('Preparing audio…');
    playbackKind='device';
    const token=generation,voice=selectVoice(lang);
    if(lang!=='en'&&!voice){status.textContent=names[lang]+' audio is not available on this device. Try English audio.';return;}
    const queue=items.flatMap(item=>chunks(item.text,lang).map(text=>({text,target:item.target})));
    function next(){
      if(token!==generation)return;
      if(!queue.length){currentUtterance=null;paused=false;controls(false);clearHighlight();pause.textContent='Pause';status.textContent='Finished reading. You can listen again.';return;}
      const item=queue.shift(),utterance=new SpeechSynthesisUtterance(item.text);
      currentUtterance=utterance;utterance.lang=locales[lang];utterance.rate=Number(rate?.value||.85);
      if(voice)utterance.voice=voice;
      utterance.onstart=()=>{
        if(token!==generation)return;highlight(item.target,lang);controls(true);status.textContent='Reading '+label+' · '+names[lang];
      };
      utterance.onend=next;
      utterance.onerror=event=>{
        if(token!==generation)return;
        const message=event.error==='not-allowed'?'Tap Listen to start the audio.':'That voice could not play. Choose another voice in Voice options.';
        stopSpeech(message);
      };
      synth.speak(utterance);
    }
    next();
  }
  function speak(items,lang,label){
    const clips=data.narration?.[lang];
    if(prefs.get('voice-'+lang,'')||!clips||!items.every(item=>clips[item.text])){speakWithDevice(items,lang,label);return;}
    stopSpeech('Preparing narration…');playbackKind='recorded';
    const token=generation;let cursor=0;
    function next(){
      if(token!==generation)return;
      if(cursor>=items.length){narrationPlayer=null;playbackKind=null;paused=false;controls(false);clearHighlight();pause.textContent='Pause';status.textContent='Finished reading. You can listen again.';return;}
      const index=cursor++,item=items[index],player=new Audio(clips[item.text]);narrationPlayer=player;
      player.preload='auto';player.playbackRate=Number(rate?.value||.85)/.85;
      player.onplaying=()=>{if(token!==generation)return;highlight(item.target,lang);controls(true);status.textContent='Reading '+label+' · '+names[lang];};
      player.onended=next;
      function fallback(){if(token!==generation)return;if(hasSpeech)speakWithDevice(items.slice(index),lang,label);else stopSpeech('This audio could not load. Check the connection and tap Listen again.');}
      player.onerror=fallback;
      player.play().catch(error=>{if(token!==generation)return;if(error.name==='NotAllowedError')stopSpeech('Tap Listen to start the audio.');else fallback();});
    }
    next();
  }
  const translations=[];
  if(data.paragraphs){
    data.paragraphs.forEach(p=>{
      const block=document.getElementById(p.id);
      const translation=document.createElement('div');translation.className='translation';translation.hidden=true;
      const head=document.createElement('div');head.className='translation-head';
      const tag=document.createElement('span');
      const toggle=document.createElement('button');toggle.type='button';
      const content=document.createElement('div');content.className='translation-content';content.id=p.id+'-translation';
      const text=document.createElement('p');
      const button=document.createElement('button');button.type='button';button.className='listen';button.dataset.speak='home';
      content.append(text,button);head.append(tag,toggle);translation.append(head,content);block.append(translation);
      toggle.setAttribute('aria-controls',content.id);toggle.setAttribute('aria-expanded','true');
      toggle.addEventListener('click',()=>{content.hidden=!content.hidden;toggle.setAttribute('aria-expanded',String(!content.hidden));toggle.textContent=content.hidden?ui[code].show:ui[code].hide;});
      button.addEventListener('click',()=>speak([{text:p[code],target:content.id}],code,'paragraph'));
      translations.push({p,translation,tag,toggle,content,text,button});
      block.querySelector('[data-speak="en"]').addEventListener('click',()=>speak([{text:p.en,target:p.id}], 'en','paragraph'));
    });
  }
  function renderLanguage(){
    document.querySelectorAll('[data-support]').forEach(el=>{el.hidden=code==='en';});
    translations.forEach(({p,translation,tag,toggle,content,text,button})=>{
      translation.hidden=code==='en';if(code==='en')return;
      translation.lang=locales[code];tag.textContent=names[code];text.textContent=p[code];
      content.hidden=true;toggle.setAttribute('aria-expanded','false');toggle.textContent=ui[code].show;
      button.textContent='▶ '+listenLabels[code];button.setAttribute('aria-label','Read this translation in '+names[code]);
    });
    document.querySelectorAll('[data-localized]').forEach(el=>{
      const record=data.localized[el.dataset.localized];el.hidden=code==='en';
      if(code!=='en'){el.textContent=record[code];el.lang=locales[code];}
    });
    document.querySelectorAll('[data-section-home]').forEach(button=>{button.hidden=code==='en';if(code!=='en'){button.textContent='▶ '+ui[code].section;button.lang=locales[code];}});
    document.querySelectorAll('[data-home-pdf]').forEach(link=>{link.hidden=code==='en';});
    const allButton=document.getElementById('translations-all');
    if(allButton){allButton.hidden=code==='en';allButton.textContent='Show all translations';allButton.setAttribute('aria-pressed','false');}
    updateVoices();
  }
  function readSection(index,lang){
    const section=data.sections[index];
    const items=[{text:section.title[lang],target:section.id}];
    section.paragraphIds.forEach(id=>{const p=data.paragraphs.find(p=>p.id===id);items.push({text:p[lang],target:lang==='en'?id:id+'-translation'});});
    if(section.diagram)items.push(...section.diagram[lang].map(text=>({text,target:section.id+'-key'})));
    if(section.extra)items.push(...section.extra[lang].map(text=>({text,target:'toolkit'})));
    speak(items,lang,'section '+(index+1));
  }
  document.querySelectorAll('[data-section-en]').forEach(b=>b.addEventListener('click',()=>readSection(Number(b.dataset.sectionEn),'en')));
  document.querySelectorAll('[data-section-home]').forEach(b=>b.addEventListener('click',()=>readSection(Number(b.dataset.sectionHome),code)));
  if(data.words){document.querySelectorAll('[data-word-en]').forEach(b=>b.addEventListener('click',()=>{const i=Number(b.dataset.wordEn);speak([{text:data.words.en[i].join('. '),target:'word-'+i}],'en','word');}));document.querySelectorAll('[data-word-home]').forEach(b=>b.addEventListener('click',()=>{const i=Number(b.dataset.wordHome);speak([{text:data.words[code][i].join('。 '),target:'word-'+i}],code,'word');}));}
  language.addEventListener('change',()=>{stopSpeech();code=language.value;prefs.set('language',code);renderLanguage();});
  document.getElementById('translations-all')?.addEventListener('click',event=>{
    const button=event.currentTarget,open=button.getAttribute('aria-pressed')!=='true';
    translations.forEach(({content,toggle})=>{content.hidden=!open;toggle.setAttribute('aria-expanded',String(open));toggle.textContent=open?ui[code].hide:ui[code].show;});
    button.setAttribute('aria-pressed',String(open));button.textContent=open?'Hide all translations':'Show all translations';
  });
  if(pause)pause.addEventListener('click',()=>{
    if(!playing)return;
    if(playbackKind==='recorded'){
      if(paused){narrationPlayer?.play().catch(()=>stopSpeech('Tap Listen to start again.'));paused=false;pause.textContent='Pause';status.textContent='Reading resumed.';}
      else{narrationPlayer?.pause();paused=true;pause.textContent='Resume';status.textContent='Paused. Tap Resume to continue.';}
      return;
    }
    if(paused){synth.resume();paused=false;pause.textContent='Pause';status.textContent='Reading resumed.';}else{synth.pause();paused=true;pause.textContent='Resume';status.textContent='Paused. Tap Resume to continue.';}
  });
  if(stop)stop.addEventListener('click',()=>stopSpeech());
  if(rate)rate.addEventListener('change',()=>{prefs.set('rate',rate.value);stopSpeech('Speed changed. Tap Listen to start again.');});
  if(size)size.addEventListener('change',()=>{prefs.set('size',size.value);document.documentElement.style.setProperty('--reading-size',size.value+'px');});
  for(const [select,lang] of [[englishVoice,'en'],[homeVoice,'home']])if(select)select.addEventListener('change',()=>{prefs.set('voice-'+(lang==='home'?code:lang),select.value);stopSpeech('Voice selected. Tap Listen to start.');});
  document.getElementById('print-reader')?.addEventListener('click',()=>{stopSpeech();window.print();});
  const settings=document.querySelector('.reading-settings');
  if(settings){
    document.addEventListener('pointerdown',event=>{if(settings.open&&!settings.contains(event.target))settings.open=false;});
    document.addEventListener('keydown',event=>{if(event.key==='Escape'&&settings.open){settings.open=false;settings.querySelector('summary').focus();}});
  }
  window.addEventListener('pagehide',()=>{if(synth)synth.cancel();if(narrationPlayer)narrationPlayer.pause();});
  if(synth)synth.addEventListener('voiceschanged',updateVoices);
  renderLanguage();
})();
