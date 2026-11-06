from pathlib import Path
from html import escape as e
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT
LANGS=('en','ja','ko','zh')
NAMES={'ja':'日本語','ko':'한국어','zh':'简体中文'}
META={
 'biosphere':{'label':'Biosphere','simple':'Living things','accent':'#37654a','tint':'#edf4ed','description':'Plants, animals, people—and every living thing.','hero':'Earth’s living world','number':'01'},
 'hydrosphere':{'label':'Hydrosphere','simple':'Water','accent':'#25688e','tint':'#edf5fa','description':'Rivers, oceans, ice, and water on the move.','hero':'Water everywhere on Earth','number':'02'},
 'geosphere':{'label':'Geosphere','simple':'Land and rock','accent':'#865a26','tint':'#f8f0e5','description':'From the soil under your feet to rocks deep inside Earth.','hero':'The ground beneath our feet','number':'03'},
 'atmosphere':{'label':'Atmosphere','simple':'Air','accent':'#306c7b','tint':'#edf5f7','description':'The invisible blanket of gases around our planet.','hero':'The invisible world around us','number':'04'}
}
ORDER=list(META)
ASSETS=OUT/'assets'/'images'
ASSETS.mkdir(parents=True,exist_ok=True)
READERS={sphere:json.loads((ROOT/'content'/f'{sphere}.json').read_text()) for sphere in ORDER}

def header(active=''):
 nav=''.join(f'<a href="{s}.html"'+(' aria-current="page"' if s==active else '')+f'>{m["label"]}</a>' for s,m in META.items())
 return '<a class="skip" href="#main">Skip to reading</a><header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">◎</span><span><strong>Earth Explorers</strong><small>Grade 4 · Our connected planet</small></span></a><nav class="nav" aria-label="Earth’s spheres">'+nav+'</nav></div></header>'

def footer():
 return '<footer class="site-footer"><div class="shell footer-inner"><p>Earth Explorers · Grade 4 EAL<br>Read in English. Make meaning in your language.</p><p><a href="credits.html">Sources &amp; image credits</a> · <a href="https://github.com/LenguajeLabs-design/Grade-4-The-Earth-Spheres">GitHub</a></p></div></footer>'

def language_select():
 return '<select id="language"><option value="en">English only</option><option value="ja">日本語 · Japanese</option><option value="ko">한국어 · Korean</option><option value="zh">简体中文 · Chinese</option></select>'

def document(title,body,data=None,style=''):
 serialized=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c') if data else ''
 script=f'<script id="reader-data" type="application/json">{serialized}</script><script src="app.js?v=20261106-toolbar" defer></script>' if data else ''
 return f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Explore Earth’s four spheres with illustrated English readers, Japanese, Korean and Chinese paragraph translations, and read-aloud support."><meta name="theme-color" content="#102f3a"><title>{e(title)} | Earth Explorers</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="styles.css?v=20261106-toolbar"></head><body{(" style="+chr(34)+style+chr(34)) if style else ""}>{body}{script}</body></html>\n'

def localized(data,values,key=None):
 key=key or 'l'+str(len(data['localized']))
 data['localized'][key]={lang:values[lang] for lang in ('ja','ko','zh')}
 return f'data-localized="{key}" hidden'

def paragraph(data,en,tr,ident):
 data['paragraphs'].append({'id':ident,'en':en,**tr})
 return f'<div class="paragraph-block" id="{ident}"><p>{e(en)}</p><button class="listen" type="button" data-speak="en" aria-label="Read this English paragraph">▶ Listen in English</button></div>'

def tools():
 return ('<div class="tools" role="region" aria-label="Reading and listening tools">'
  '<div class="tools-main"><div class="tool-group language-group"><label for="language">Home language</label>'+language_select()+'</div>'
  '<div class="playback-controls" id="playback-controls" hidden><button id="pause" type="button" disabled>Pause</button><button id="stop" type="button" disabled>Stop</button></div>'
  '<details class="reading-settings"><summary>Reading settings</summary><div class="settings-panel">'
  '<div class="settings-grid"><div class="tool-group"><label for="rate">Reading speed</label><select id="rate"><option value="0.7">Slower</option><option value="0.85" selected>Gentle</option><option value="1">Normal</option></select></div>'
  '<div class="tool-group"><label for="text-size">Text size</label><select id="text-size"><option value="20">Comfortable</option><option value="23">Larger</option><option value="26">Largest</option></select></div></div>'
  '<div class="settings-actions"><button id="translations-all" type="button" aria-pressed="false" hidden>Show all translations</button><button id="print-reader" class="print" type="button">Print reader ↗</button></div>'
  '<div class="voice-fields"><div class="tool-group"><label for="english-voice">English voice</label><select id="english-voice"></select></div><div class="tool-group" id="home-voice-group" hidden><label for="home-voice">Home-language voice</label><select id="home-voice"></select></div></div>'
  '<p class="voice-note" id="voice-note">Included narration is available in all four languages. Optional voices come from your device.</p>'
  '</div></details></div><span class="audio-status" id="audio-status" role="status" aria-live="polite"></span></div>')

for sphere in ORDER:
 d=READERS[sphere];m=META[sphere]
 data={'paragraphs':[],'localized':{},'sections':[],'words':{lang:d[lang]['vocab'] for lang in LANGS}}
 title_attrs=localized(data,{lang:d[lang]['coverTitle'] for lang in ('ja','ko','zh')})
 body=header(sphere)+f'<main id="main" class="shell"><div class="breadcrumb"><a href="index.html">All spheres</a> / {m["label"]}</div><section class="reader-hero" aria-label="Reader introduction"><div><p class="eyebrow">{m["number"]} / {m["simple"]} · Earth science</p><h1>The {m["label"]}</h1><p class="home-title" {title_attrs}></p><p class="intro">{e(d["en"]["subtitle"])}. Six short reads to explore, listen, and connect.</p></div><div><img src="assets/images/{sphere}-2.webp" alt="{e(d["en"]["pages"][0]["caption"].replace("LOOK: ",""))} — illustration" width="724" height="436" fetchpriority="high"><p class="hero-credit">Illustration from the Earth Explorers reader</p></div></section>'+tools()
 links=''.join(f'<li><a href="#section-{i+1}">{i+1:02d} &nbsp; {e(p["title"])}</a></li>' for i,p in enumerate(d['en']['pages']))
 body+='<div class="reader-layout"><aside class="reader-index" aria-label="Reader contents"><p class="eyebrow">In this reader</p><ol>'+links+'</ol><a class="finish-link" href="#toolkit">↘ Words &amp; questions</a></aside><div>'
 for i,en in enumerate(d['en']['pages']):
  ident=f'section-{i+1}'
  attrs=localized(data,{lang:d[lang]['pages'][i]['title'] for lang in ('ja','ko','zh')})
  body+=f'<article class="reading-section" id="{ident}" aria-labelledby="{ident}-title"><div class="section-top"><span class="section-num">{i+1:02d} / EXPLORE</span><h2 id="{ident}-title">{e(en["title"])}</h2><p class="title-translation" {attrs}></p><button class="section-play" type="button" data-section-en="{i}" data-speak="en">▶ Listen to this section</button> <button class="section-play" type="button" data-section-home="{i}" data-speak="home" hidden></button></div>'
  attrs=localized(data,{lang:d[lang]['pages'][i]['caption'] for lang in ('ja','ko','zh')})
  diagram_class=' class="diagram"' if i>=4 and sphere!='atmosphere' else ''
  body+=f'<figure{diagram_class}><img src="assets/images/{sphere}-{i+2}.webp" alt="{e(en["caption"].replace("LOOK: ",""))} — illustration" loading="lazy" width="724" height="458"><figcaption>{e(en["caption"])} <span aria-hidden="true">·</span> Illustration<span class="title-translation" {attrs}></span></figcaption></figure><div class="section-body">'
  paragraph_ids=[]
  for j,text in enumerate(en['body']):
   pid=f'{ident}-paragraph-{j+1}';paragraph_ids.append(pid)
   body+=paragraph(data,text,{lang:d[lang]['pages'][i]['body'][j] for lang in ('ja','ko','zh')},pid)
  record={'id':ident,'title':{lang:d[lang]['pages'][i]['title'] for lang in LANGS},'paragraphIds':paragraph_ids}
  if en.get('chips'):
   body+='<div class="sphere-chips" aria-label="The four spheres">'+''.join(f'<span>{e(chip)}</span>' for chip in en['chips'])+'</div>'
  if en.get('diagram'):
   record['diagram']={lang:d[lang]['pages'][i]['diagram'] for lang in LANGS}
   body+=f'<div class="callout" id="{ident}-key"><strong>{e(en["label"])} · DIAGRAM KEY</strong><ul class="diagram-key">'
   for j,keytext in enumerate(en['diagram']):
    attrs=localized(data,{lang:d[lang]['pages'][i]['diagram'][j] for lang in ('ja','ko','zh')})
    body+=f'<li><p>{e(keytext)}</p><p class="key-translation" {attrs}></p></li>'
   body+='</ul></div>'
  else:
   pid=f'{ident}-callout';paragraph_ids.append(pid)
   body+=f'<div class="callout"><strong>{e(en["label"])}</strong>'+paragraph(data,en['callout'],{lang:d[lang]['pages'][i]['callout'] for lang in ('ja','ko','zh')},pid)+'</div>'
  data['sections'].append(record)
  body+='</div></article>'
 body+='<section class="toolkit" id="toolkit" aria-labelledby="toolkit-title"><p class="eyebrow">YOUR SCIENTIST TOOLKIT</p><h2 id="toolkit-title">Five words to take with you</h2><div class="word-list">'
 for j,(word,meaning) in enumerate(d['en']['vocab']):
  wa=localized(data,{lang:d[lang]['vocab'][j][0] for lang in ('ja','ko','zh')})
  ma=localized(data,{lang:d[lang]['vocab'][j][1] for lang in ('ja','ko','zh')})
  body+=f'<div class="word" id="word-{j}"><h4>{e(word)}</h4><p>{e(meaning)}</p><button class="listen" type="button" data-speak="en" data-word-en="{j}" aria-label="Hear {e(word)} in English">▶ Listen</button><div class="translated-word" data-support hidden><h4 {wa}></h4><p {ma}></p><button class="listen" type="button" data-speak="home" data-word-home="{j}">▶ Listen</button></div></div>'
 body+='</div><h3>Think like a scientist</h3><ol class="question-list">'
 for j,q in enumerate(d['en']['questions']):
  attrs=localized(data,{lang:d[lang]['questions'][j] for lang in ('ja','ko','zh')})
  body+=f'<li>{e(q)}<p class="question-translation" {attrs}></p></li>'
 attrs=localized(data,{lang:d[lang]['frame'] for lang in ('ja','ko','zh')})
 body+=f'</ol><h3>Try saying it</h3><div class="frame"><p>{e(d["en"]["frame"])}</p><p class="frame-translation" {attrs}></p></div></section>'
 next_sphere=ORDER[(ORDER.index(sphere)+1)%4]
 body+=f'<div class="next-spheres"><a href="index.html">← All four spheres</a><a href="{next_sphere}.html">Explore the {META[next_sphere]["label"]} →</a></div></div></div></main>'+footer()
 (OUT/f'{sphere}.html').write_text(document('The '+m['label'],body,data,f'--accent:{m["accent"]};--tint:{m["tint"]}'))

home={'localized':{}}
body=header()+'<main id="main"><section class="shell home-hero"><div><p class="eyebrow">GRADE 4 / EARTH SCIENCE</p><h1>One Earth.<br>Everything <em>connects.</em></h1><p class="intro">Explore the living things, water, land, and air that make our planet home.</p><div class="intro-route"><span>1</span> Choose a sphere <span>2</span> Read &amp; listen <span>3</span> Make connections</div></div><div class="hero-visual"><img src="assets/images/atmosphere-2.webp" alt="Illustration of Earth’s curved horizon and the blue atmosphere above it" width="768" height="462" fetchpriority="high"><div class="visual-tag">AIR &nbsp; / &nbsp; WATER &nbsp; / &nbsp; LAND &nbsp; / &nbsp; LIFE</div></div></section><section class="shell" aria-labelledby="choose-title"><div class="section-head"><h2 id="choose-title">Where will you explore?</h2><p>Four readers. One connected world.</p></div><div class="home-language"><label for="language">Choose your home language</label>'+language_select()+'</div><div class="sphere-grid">'
for s,m in META.items():
 attrs=localized(home,{lang:READERS[s][lang]['coverTitle'] for lang in ('ja','ko','zh')})
 body+=f'<a class="sphere-card" style="--accent:{m["accent"]}" href="{s}.html"><img src="assets/images/{s}-2.webp" alt="{e(READERS[s]["en"]["pages"][0]["caption"].replace("LOOK: ",""))} — illustration" width="724" height="436" loading="lazy"><div class="card-content"><div class="card-number">{m["number"]} / {m["simple"].upper()}</div><h3>{m["label"]}</h3><p class="home-title" {attrs}></p><p>{e(m["description"])}</p><span class="card-link">Open reader <span aria-hidden="true">↗</span></span></div></a>'
body+='</div></section><section class="connection-band"><div class="shell connection-inner"><div><p class="eyebrow">FOLLOW A CONNECTION</p><h2>Nothing on Earth works alone.</h2><p>A tree grows in soil, takes in water, and uses gases from the air. One tree connects all four spheres.</p></div><div class="chain" aria-label="Air, water and soil help a tree grow"><span>Air</span><b aria-hidden="true">+</b><span>Water</span><b aria-hidden="true">+</b><span>Soil</span><b aria-hidden="true">→</b><span>A living tree</span></div></div></section></main>'+footer()
(OUT/'index.html').write_text(document('Our connected planet',body,home))

body=header()+'<main class="shell credit-page" id="main"><p class="eyebrow">EARTH EXPLORERS / ABOUT THIS READER</p><h1>Sources &amp; image credits</h1><p>These four readers adapt the English texts and Japanese, Korean and Simplified Chinese translations prepared for the Grade 4 Earth’s Spheres unit.</p><h2>Illustrations</h2><p>The images are illustrations from the original Earth Explorers readers. The realistic scenes are photorealistic illustrations, rather than photographs documenting particular places or events. Diagrams are simplified models. Images are stored with the website so reading does not depend on a separate image service.</p><h2>Science references</h2><ul><li><a href="https://gpm.nasa.gov/education/node/173">NASA: Connect the Spheres</a></li><li><a href="https://scied.ucar.edu/learning-zone/earth-system">UCAR: Earth as a System</a></li><li><a href="https://www.usgs.gov/special-topics/water-science-school">USGS Water Science School</a></li><li><a href="https://www.usgs.gov/programs/ecosystems">USGS Ecosystems Mission Area</a></li><li><a href="https://www.nps.gov/subjects/geology/">National Park Service: Geology</a></li><li><a href="https://www.weather.gov/safety/lightning">NOAA / National Weather Service: Lightning Safety</a></li></ul><h2>Language and listening</h2><p>English stays visible. Choose a home language to see its translation after each paragraph. Use the Listen buttons for an individual paragraph or a whole section. Included synthetic narration covers English (Samantha), Japanese (Kyoko), Korean (Yuna) and Chinese (Tingting). Whole-paragraph recordings are stored with the site and play at a gentle pace by default. Optional device voices depend on the browser and installed voices, and some may use an internet service. Written translations always remain available.</p><p>Japanese readings in parentheses support selected science terms. The translated texts have not had independent native-speaker review.</p><h2>For teachers</h2><p>The main texts use the short passages from the classroom readers. They have not been independently assigned a WIDA or Lexile level. The geosphere definition includes Earth’s rocks, land and interior, consistent with the section on molten rock. In this four-sphere model, ice is included in the hydrosphere; other resources may name the cryosphere separately.</p><p>The site does not ask students to sign in or submit personal information. Reading-language, speed, size and voice preferences are saved only in the browser. Hosting and device speech services operate under their own policies.</p><p><a href="index.html">← Back to all four spheres</a></p></main>'+footer()
(OUT/'credits.html').write_text(document('Sources and image credits',body))
(OUT/'assets'/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="32" fill="#102f3a"/><circle cx="32" cy="32" r="20" fill="none" stroke="#d4e8d8" stroke-width="3"/><ellipse cx="32" cy="32" rx="9" ry="20" fill="none" stroke="#d4e8d8" stroke-width="2"/><path d="M12 32h40" stroke="#d4e8d8" stroke-width="2"/></svg>')
(OUT/'.nojekyll').touch()
print('Built home, four complete multilingual readers and credits; 24 optimized local illustrations.')
