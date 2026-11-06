"""Check publishability, navigation and complete multilingual reading records."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import json

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,path):
        super().__init__(convert_charrefs=True)
        self.path=path;self.ids=set();self.links=[];self.assets=[];self.script=False;self.json='';self.sections=0
        self.feed(path.read_text())
    def handle_starttag(self,tag,pairs):
        a=dict(pairs)
        if a.get('id'):
            assert a['id'] not in self.ids,(self.path.name,'duplicate id',a['id'])
            self.ids.add(a['id'])
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag in ('img','script') and a.get('src'):self.assets.append(a['src'])
        if tag=='link' and a.get('href'):self.assets.append(a['href'])
        if tag=='img':assert a.get('alt'),(self.path.name,'image has no alt text')
        if tag=='script' and a.get('id')=='reader-data':self.script=True
        if tag=='article' and 'book-page' in a.get('class',''):self.sections+=1
    def handle_endtag(self,tag):
        if tag=='script':self.script=False
    def handle_data(self,text):
        if self.script:self.json+=text

pages={p.name:Page(p) for p in ROOT.glob('*.html')}
for name,page in pages.items():
    for raw in page.assets+page.links:
        u=urlsplit(raw)
        if u.scheme or u.netloc:continue
        target=ROOT/unquote(u.path) if u.path else page.path
        assert target.exists(),(name,'missing local link',raw)
        if u.fragment and target.suffix=='.html':
            assert u.fragment in pages[target.name].ids,(name,'missing anchor',raw)
    if name=='earthquakes-volcanoes.html':
        d=json.loads(page.json)
        assert d['audio'] is False and d['kind']=='extension'
        assert 'data-speak' not in page.path.read_text()
        assert len(d['paragraphs'])==9
        for record in d['paragraphs']:
            assert record['id'] in page.ids
            assert all(record.get(lang,'').strip() for lang in ('en','ja','ko','zh'))
        assert 'earthquakes-volcanoes.html' in pages['geosphere.html'].links
        print(name,': nine translated paragraphs; reading-only extension and Geosphere link valid')
    elif name not in ('index.html','credits.html'):
        d=json.loads(page.json)
        assert page.sections==4,(name,'expected four reading sections')
        assert len(d['sections'])==4
        assert len(d['words']['en'])==5
        for p in d['paragraphs']:
            assert p['id'] in page.ids
            assert all(isinstance(p.get(lang),str) and p[lang].strip() for lang in ('en','ja','ko','zh')),(name,'missing paragraph translation',p['id'])
        for s in d['sections']:
            assert s['id'] in page.ids
            assert all(s['title'].get(lang) for lang in ('en','ja','ko','zh'))
        for lang in ('en','ja','ko','zh'):
            clips=d['narration'][lang]
            spoken={p[lang] for p in d['paragraphs']}
            for s in d['sections']:
                spoken.add(s['title'][lang])
                spoken.update(s.get('diagram',{}).get(lang,[]))
                spoken.update(s.get('extra',{}).get(lang,[]))
            for pair in d['words'][lang]:
                spoken.update(('. '.join(pair),'。 '.join(pair)))
            assert spoken <= clips.keys(),(name,'missing narration',lang)
            for text,raw in clips.items():
                asset=ROOT/raw
                assert asset.exists() and asset.stat().st_size>4500,(name,'missing or empty audio',raw)
        print(name,': four sections,',len(d['paragraphs']),'complete multilingual paragraphs, five vocabulary entries; links and assets valid')
assert (ROOT/'.nojekyll').exists()
print(len(pages),'HTML pages checked. GitHub Pages project-relative links are valid.')
print('The original four readers retain their narration in all four languages; the extension has no audio.')
