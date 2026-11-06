"""Build the reading-only multilingual earthquakes and volcanoes extension."""
from pathlib import Path
from html import escape as e
import json

ROOT=Path(__file__).resolve().parents[1]
LANGS=('en','ja','ko','zh')

def build_extension(g):
    content=json.loads((ROOT/'content/earthquakes-volcanoes.json').read_text())
    data={'kind':'extension','audio':False,'paragraphs':[],'localized':{}}
    def translated(record,tag='p',css='support-text'):
        attrs=g['localized'](data,{lang:record[lang] for lang in LANGS[1:]})
        return f'<{tag} class="{css}" {attrs}></{tag}>'
    def pair(record,tag='p',css=''):
        support_tag='p' if tag in ('h2','h3') else tag
        return f'<{tag}'+(f' class="{css}"' if css else '')+'>'+e(record['en'])+f'</{tag}>'+translated(record,support_tag)
    def paragraph(record,ident):
        data['paragraphs'].append({'id':ident,**record})
        return f'<div class="paragraph-block" id="{ident}"><p>{e(record["en"])}</p></div>'
    def section_start(ident,title,number):
        return f'<article class="reading-section book-page extension-section" id="{ident}" aria-labelledby="{ident}-title"><div class="book-content"><p class="eyebrow">{number:02d} / GEOSPHERE EXPLORER</p><h2 id="{ident}-title">{e(title["en"])}</h2>'+translated(title)
    body=g['header']('geosphere')+'<main id="main" class="shell book-main"><div class="book-intro"><a href="geosphere.html">← Back to the Geosphere</a><span>GRADE 4 / SUPPORTED READER</span></div>'
    body+='<div class="tools" role="region" aria-label="Reading tools"><div class="tools-main"><div class="tool-group language-group"><label for="language">Home language</label>'+g['language_select']()+'</div><details class="reading-settings"><summary>Reading settings</summary><div class="settings-panel"><div class="tool-group"><label for="text-size">Text size</label><select id="text-size"><option value="20">Comfortable</option><option value="23">Larger</option><option value="26">Largest</option></select></div><div class="settings-actions"><button id="translations-all" type="button" aria-pressed="false" hidden>Show all translations</button><button id="print-reader" class="print" type="button">Print reader ↗</button></div></div></details></div></div>'
    short=['Moving plates','Earthquakes','Volcanoes','Compare & explain']
    body+='<nav class="book-nav" aria-label="Extension sections">'+''.join(f'<a href="#{s["id"]}">{i+1:02d} {short[i]}</a>' for i,s in enumerate(content['sections']))+'</nav>'
    body+='<section class="extension-cover"><div class="book-hero extension-hero"><p class="eyebrow">GEOSPHERE / EARTH IN MOTION</p><h1>'+e(content['title']['en'])+'</h1>'+translated(content['title'],'p','book-home-title')+'<p class="book-subtitle">'+e(content['subtitle']['en'])+'</p>'+translated(content['subtitle'])+'</div><div class="extension-intro">'+pair(content['intro'])+'<p class="reading-badge">Short passages · Visual models · Explain with evidence</p></div></section>'
    for i,section in enumerate(content['sections']):
        body+=section_start(section['id'],section['title'],i+1)
        for j,p in enumerate(section['paragraphs']):body+=paragraph(p,f'{section["id"]}-paragraph-{j+1}')
        if section['id']=='earthquakes':
            body+='<div class="earthquake-steps">'+pair({'en':'Follow the steps','ja':'順番を確かめよう','ko':'순서대로 살펴봐요','zh':'按顺序观察'},'h3')+'<ol>'
            for j,step in enumerate(content['sequence']):body+=f'<li><span class="step-number" aria-hidden="true">{j+1}</span><div>'+pair(step)+'</div></li>'
            body+='</ol></div>'
        if section['id']=='volcanoes':
            body+='''<figure class="volcano-model"><svg viewBox="0 0 760 430" role="img" aria-labelledby="volcano-model-title volcano-model-desc" xmlns="http://www.w3.org/2000/svg"><title id="volcano-model-title">A simplified volcano cross-section</title><desc id="volcano-model-desc">Magma below the ground rises through a passage in a volcano. At the surface it is called lava. Ash and gases rise above the opening. The model is not to scale.</desc><defs><marker id="rise-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="none" stroke="#a94328" stroke-width="1.5"/></marker></defs><rect width="760" height="430" rx="14" fill="#f0f7fa"/><path d="M0 270H760V430H0Z" fill="#d7b995"/><path d="M98 270L299 98L339 112L380 96L590 270Z" fill="#96745d"/><path d="M127 270L299 124L329 137L378 123L559 270" fill="none" stroke="#c9ac8d" stroke-width="14"/><path d="M300 111L315 165L286 198L310 227" fill="none" stroke="#d94c28" stroke-width="14" stroke-linecap="round"/><ellipse cx="342" cy="359" rx="93" ry="39" fill="#d94c28" stroke="#a94328" stroke-width="3"/><path d="M338 327L328 276L347 220L330 165L335 116" fill="none" stroke="#d94c28" stroke-width="23" stroke-linecap="round"/><path d="M373 105L414 145L466 167L488 207L543 232" fill="none" stroke="#ec6231" stroke-width="12" stroke-linecap="round"/><path d="M337 87Q310 54 334 31M359 87Q387 57 368 29" fill="none" stroke="#74848b" stroke-width="7" stroke-linecap="round"/><circle cx="318" cy="37" r="5" fill="#74848b"/><circle cx="388" cy="48" r="5" fill="#74848b"/><circle cx="351" cy="17" r="4" fill="#74848b"/><path d="M336 287V205" stroke="#a94328" stroke-width="3" fill="none" marker-end="url(#rise-arrow)"/><g fill="#102f3a" font-family="Arial,sans-serif" font-size="22" font-weight="600"><text x="474" y="53">Ash + gases</text><text x="556" y="185">Lava</text><text x="509" y="360">Magma</text><text x="24" y="302" font-size="17">Earth’s surface</text></g><g fill="none" stroke="#425a68" stroke-width="2"><path d="M464 49H404L381 58"/><path d="M547 179H505L476 177"/><path d="M495 353H440"/><path d="M99 307V274"/></g></svg></figure>'''
            body+=pair({'en':'Simplified model · Not to scale','ja':'簡単にしたモデルです。実際の大きさの比率とは異なります。','ko':'간단하게 나타낸 모형이며, 실제 크기 비율과 달라요.','zh':'简化模型，未按实际比例绘制。'},'p','model-caption')
            body+='<div class="diagram-key extension-key">'
            for row in content['diagramKey']:body+='<div>'+pair(row)+'</div>'
            body+='</div>'
        if section['id']=='connections':
            comparisons=[
              {'en':'Earthquake: rocks suddenly move, and the ground shakes.','ja':'地震：岩石が突然動き、地面が揺れます。','ko':'지진: 암석이 갑자기 움직이고 땅이 흔들려요.','zh':'地震：岩石突然移动，地面发生震动。'},
              {'en':'Volcanic eruption: material comes out through an opening in Earth’s surface.','ja':'火山の噴火：地表の開口部から物質が出てきます。','ko':'화산 분출: 지구 표면의 분출구를 통해 물질이 나와요.','zh':'火山喷发：物质通过地球表面的开口喷出。'}]
            body+='<div class="compare-cards">'+''.join('<div>'+pair(row)+'</div>' for row in comparisons)+'</div>'
        body+='</div></article>'
    body+='<section class="extension-toolkit" id="word-bank" aria-labelledby="word-bank-title"><h2 id="word-bank-title">Words to help you explain</h2>'+translated({'en':'Words to help you explain','ja':'説明に役立つ言葉','ko':'설명할 때 도움이 되는 낱말','zh':'帮助你解释的词语'})+'<div class="extension-vocabulary">'
    for word in content['vocabulary']:
        body+='<div><h3>'+e(word['en'][0])+'</h3><p>'+e(word['en'][1])+'</p>'+translated({lang:word[lang][0]+' — '+word[lang][1] for lang in LANGS})+'</div>'
    body+='</div>'+pair({'en':'Think, point and explain','ja':'考えて、指さして、説明しよう','ko':'생각하고 가리키며 설명해 봐요','zh':'想一想，指一指，解释一下'},'h2')+'<ol class="extension-questions">'
    for q in content['questions']:body+='<li>'+pair(q)+'</li>'
    body+='</ol>'+pair({'en':'Try these sentence frames','ja':'文の型を使ってみよう','ko':'이 문장 틀을 사용해 봐요','zh':'试着使用这些句型'},'h2')+'<div class="extension-frames">'
    for f in content['frames']:body+='<div>'+pair(f)+'</div>'
    body+='</div></section><details class="extension-notes"><summary>Teacher notes & sources</summary><p>Designed to support Grade 4 learners working around WIDA levels 2–3: preview vocabulary, follow illustrated sequences, match causes with effects, and explain using sentence frames. Partners can discuss the models before writing. These are classroom language supports, not an official WIDA text rating.</p><p>English stays visible when translations are opened. Translations have not had independent native-speaker review. The volcano scene is an illustration from the existing classroom reader; the cross-section is a simplified model.</p><ul><li><a href="https://www.usgs.gov/faqs/what-earthquake-and-what-causes-them-happen">USGS: What causes an earthquake?</a></li><li><a href="https://www.usgs.gov/faqs/are-tectonic-plates-floating-magma">USGS: Plates and the mostly solid mantle</a></li><li><a href="https://spaceplace.nasa.gov/earthquakes/en/">NASA Space Place: What is an earthquake?</a></li><li><a href="https://spaceplace.nasa.gov/volcanoes2/en/">NASA Space Place: What is a volcano?</a></li><li><a href="https://pubs.usgs.gov/fs/fs027-00/">USGS: Volcanic ash</a></li><li><a href="https://wida.wisc.edu/resources/can-do-descriptors-key-uses-edition-grades-4-5">WIDA: Grades 4–5 Can Do Descriptors</a></li></ul></details><div class="next-spheres"><a href="geosphere.html">← Back to the Geosphere</a><a href="index.html">Explore all four spheres →</a></div></main>'+g['footer']()
    page=g['document']('Earthquakes & Volcanoes',body,data,'--accent:#865a26;--tint:#f8f0e5')
    page=page.replace('<body style=','<body class="reader-paper geosphere-extension" style=')
    page=page.replace('</head>','<link rel="stylesheet" href="geosphere-extension.css?v=20261106"></head>')
    page=page.replace('src="app.js?v=20261106-toolbar"','src="extension.js?v=20261106"')
    page=page.replace('Explore Earth’s four spheres with illustrated English readers, Japanese, Korean and Chinese paragraph translations, and read-aloud support.','Explore earthquakes and volcanoes with short English passages, Japanese, Korean and Chinese translations, diagrams and sentence frames.')
    (ROOT/'earthquakes-volcanoes.html').write_text(page)
