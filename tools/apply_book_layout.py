"""Adapt the user's Grade 5 four-section reader structure for Grade 4."""
from pathlib import Path
from html import escape as e
import json,runpy

ROOT=Path(__file__).resolve().parents[1]
g=runpy.run_path(str(ROOT/'tools'/'build_site.py'))
META,READERS,ORDER=g['META'],g['READERS'],g['ORDER']
document,header,footer,tools=g['document'],g['header'],g['footer'],g['tools']
localized,paragraph=g['localized'],g['paragraph']
LANGS=g['LANGS']
GROUPS=[(0,),(1,2),(3,4),(5,)]
LABELS=['Discover','Explore','Connect','Your mission']

def toolkit(d,data):
 out='<section class="toolkit" id="toolkit" aria-labelledby="toolkit-title"><h2 id="toolkit-title">Your scientist toolkit</h2><h3>5 words to remember</h3><div class="word-list">'
 for j,(word,meaning) in enumerate(d['en']['vocab']):
  wa=localized(data,{lang:d[lang]['vocab'][j][0] for lang in ('ja','ko','zh')})
  ma=localized(data,{lang:d[lang]['vocab'][j][1] for lang in ('ja','ko','zh')})
  out+=f'<div class="word" id="word-{j}"><h4>{e(word)}</h4><p>{e(meaning)}</p><button class="listen" type="button" data-speak="en" data-word-en="{j}" aria-label="Hear {e(word)} in English">▶ Listen</button><div class="translated-word" data-support hidden><h4 {wa}></h4><p {ma}></p><button class="listen" type="button" data-speak="home" data-word-home="{j}">▶ Listen</button></div></div>'
 out+='</div><h3>Think like a scientist</h3><ol class="question-list">'
 for j,q in enumerate(d['en']['questions']):
  attrs=localized(data,{lang:d[lang]['questions'][j] for lang in ('ja','ko','zh')})
  out+=f'<li>{e(q)}<p class="question-translation" {attrs}></p></li>'
 attrs=localized(data,{lang:d[lang]['frame'] for lang in ('ja','ko','zh')})
 return out+f'</ol><h3>Talk like a scientist</h3><div class="frame"><p>{e(d["en"]["frame"])}</p><p class="frame-translation" {attrs}></p></div></section>'

for sphere in ORDER:
 d=READERS[sphere];m=META[sphere]
 data={'paragraphs':[],'localized':{},'sections':[],'words':{lang:d[lang]['vocab'] for lang in LANGS}}
 body=header(sphere)+f'<main id="main" class="shell book-main"><div class="book-intro"><a href="index.html">← All four spheres</a><span>THE {m["label"].upper()} / GRADE 4</span></div>'
 body+=tools()
 body+='<nav class="book-nav" aria-label="Reader sections">'+''.join(f'<a href="#section-{i+1}">{i+1:02d} {label}</a>' for i,label in enumerate(LABELS))+'</nav>'
 for gi,indices in enumerate(GROUPS):
  ident=f'section-{gi+1}'
  body+=f'<article class="reading-section book-page" id="{ident}" aria-labelledby="{ident}-title">'
  if gi==0:
   ta=localized(data,{lang:d[lang]['coverTitle'] for lang in ('ja','ko','zh')})
   body+=f'<div class="book-hero" style="background-image:linear-gradient(0deg,#081b2bd9,#081b2b08),url(assets/images/{sphere}-2.webp)"><div class="eyebrow">EARTH EXPLORERS / SCIENCE READER</div><h1>The {m["label"]}</h1><p class="book-subtitle">{e(d["en"]["subtitle"])}</p><p class="book-home-title" {ta}></p></div>'
  body+='<div class="book-content">'
  first=indices[0]
  body+=f'<div class="book-section-heading"><p class="eyebrow">{gi+1:02d} / {LABELS[gi].upper()}</p><div><button class="section-play" type="button" data-section-en="{gi}" data-speak="en">▶ Read section</button> <button class="section-play" type="button" data-section-home="{gi}" data-speak="home" hidden></button></div></div>'
  record={'id':ident,'title':{lang:d[lang]['pages'][first]['title'] for lang in LANGS},'paragraphIds':[]}
  for si in indices:
   en=d['en']['pages'][si]
   attrs=localized(data,{lang:d[lang]['pages'][si]['title'] for lang in ('ja','ko','zh')})
   heading='h2' if si==first else 'h3'
   heading_id=f' id="{ident}-title"' if si==first else ''
   body+=f'<div class="book-topic"><{heading}{heading_id}>{e(en["title"])}</{heading}><p class="title-translation" {attrs}></p>'
   # Two topics share a page, like the Grade 5 reader. Keep diagrams wide.
   photo=gi in (1,2) and not en.get('diagram')
   if photo:body+='<div class="book-topic-grid"><div>'
   for j,text in enumerate(en['body']):
    pid=f'topic-{si+1}-paragraph-{j+1}';record['paragraphIds'].append(pid)
    body+=paragraph(data,text,{lang:d[lang]['pages'][si]['body'][j] for lang in ('ja','ko','zh')},pid)
   if photo:
    ca=localized(data,{lang:d[lang]['pages'][si]['caption'] for lang in ('ja','ko','zh')})
    body+=f'</div><figure><img src="assets/images/{sphere}-{si+2}.webp" alt="{e(en["caption"].replace("LOOK: ",""))} — illustration" width="724" height="458" loading="lazy"><figcaption>{e(en["caption"])} · Illustration<span {ca}></span></figcaption></figure></div>'
   if en.get('diagram'):
    record['diagram']={lang:d[lang]['pages'][si]['diagram'] for lang in LANGS}
    body+=f'<figure class="diagram"><img src="assets/images/{sphere}-{si+2}.webp" alt="{e(en["caption"])} — simplified diagram" loading="lazy" width="1453" height="920"><figcaption>{e(en["caption"])} · Diagram from the classroom reader</figcaption></figure><div class="callout" id="{ident}-key"><strong>{e(en["label"])} · DIAGRAM KEY</strong><ul class="diagram-key">'
    for j,keytext in enumerate(en['diagram']):
     ka=localized(data,{lang:d[lang]['pages'][si]['diagram'][j] for lang in ('ja','ko','zh')})
     body+=f'<li><p>{e(keytext)}</p><p class="key-translation" {ka}></p></li>'
    body+='</ul></div>'
   else:
    pid=f'topic-{si+1}-callout';record['paragraphIds'].append(pid)
    body+=f'<div class="callout"><strong>{e(en["label"])}</strong>'+paragraph(data,en['callout'],{lang:d[lang]['pages'][si]['callout'] for lang in ('ja','ko','zh')},pid)+'</div>'
   if en.get('chips'):body+='<div class="sphere-chips">'+''.join('<span>'+e(s)+'</span>' for s in en['chips'])+'</div>'
   body+='</div>'
  if gi==3:
   body+=toolkit(d,data)
   record['extra']={lang:[*['. '.join(pair) for pair in d[lang]['vocab']],*d[lang]['questions'],d[lang]['frame']] for lang in LANGS}
  data['sections'].append(record)
  body+=f'</div><div class="book-page-footer"><span>Earth Explorers · {m["label"]} · Grade 4</span><span>{gi+1:02d} / 04</span></div></article>'
 next_sphere=ORDER[(ORDER.index(sphere)+1)%4]
 body+=f'<div class="next-spheres"><a href="index.html">← All four spheres</a><a href="{next_sphere}.html">Explore the {META[next_sphere]["label"]} →</a></div></main>'+footer()
 narration_path=ROOT/'content'/'narration.json'
 if narration_path.exists():
  narration=json.loads(narration_path.read_text())
  wanted={lang:set(p[lang] for p in data['paragraphs']) for lang in LANGS}
  for lang in LANGS:
   for section in data['sections']:
    wanted[lang].add(section['title'][lang]);wanted[lang].update(section.get('diagram',{}).get(lang,[]));wanted[lang].update(section.get('extra',{}).get(lang,[]))
   for pair in data['words'][lang]:wanted[lang].update(('. '.join(pair),'。 '.join(pair)))
  data['narration']={lang:{text:narration[lang][text] for text in sorted(wanted[lang])} for lang in LANGS}
 page=document('The '+m['label'],body,data,f'--accent:{m["accent"]};--tint:{m["tint"]}')
 page=page.replace('<body style=','<body class="reader-paper" style=')
 (ROOT/f'{sphere}.html').write_text(page)
print('Applied Grade 5-inspired four-section reader layout to all four spheres.')
