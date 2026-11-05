"""Create consistent, cached narration using installed macOS system voices."""
from pathlib import Path
import json,re,hashlib,subprocess,concurrent.futures,time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'audio'
CACHE=ROOT/'qa'/'audio-cache'
OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
VOICES={'en':('Samantha',150),'ja':('Kyoko',165),'ko':('Yuna',155),'zh':('Tingting',165)}
BLANK={'en':'blank','ja':'空欄','ko':'빈칸','zh':'空白'}
texts={lang:set() for lang in VOICES}
for path in ROOT.glob('*sphere.html'):
    match=re.search(r'<script id="reader-data" type="application/json">(.*?)</script>',path.read_text(),re.S)
    d=json.loads(match.group(1))
    for lang in VOICES:
        texts[lang].update(p[lang] for p in d['paragraphs'])
        for section in d['sections']:
            texts[lang].add(section['title'][lang])
            texts[lang].update(section.get('diagram',{}).get(lang,[]))
            texts[lang].update(section.get('extra',{}).get(lang,[]))
        for pair in d['words'][lang]:
            texts[lang].add('. '.join(pair))
            texts[lang].add('。 '.join(pair))

def clean(text,lang):
    text=re.sub(r'_{2,}',f' {BLANK[lang]} ',text)
    if lang=='ja':text=re.sub(r'[\u4e00-\u9fff]+（([\u3040-\u309f]+)）',r'\1',text)
    return re.sub(r'\s+',' ',text).strip()

manifest={lang:{} for lang in VOICES}
jobs=[]
for lang in VOICES:
    voice,rate=VOICES[lang]
    for text in sorted(texts[lang]):
        spoken=clean(text,lang)
        digest=hashlib.sha256(f'v1|{voice}|{rate}|{spoken}'.encode()).hexdigest()[:16]
        name=f'{lang}-{digest}.m4a'
        manifest[lang][text]='assets/audio/'+name
        jobs.append((lang,voice,rate,spoken,name))

def build(job):
    lang,voice,rate,spoken,name=job
    target=OUT/name
    if target.exists() and target.stat().st_size>4500:return
    stem=Path(name).stem
    source=CACHE/(stem+'.txt');aiff=CACHE/(stem+'.aiff')
    source.write_text(spoken)
    subprocess.run(['/usr/bin/say','-v',voice,'-r',str(rate),'-f',str(source),'-o',str(aiff)],check=True,capture_output=True,timeout=40)
    assert aiff.stat().st_size>5000,('Empty speech',voice,spoken)
    subprocess.run(['/usr/bin/afconvert','-f','m4af','-d','aac','-b','64000',str(aiff),str(target)],check=True,capture_output=True,timeout=25)
    assert target.stat().st_size>4500,('Empty narration',name)
    aiff.unlink()

print('Preparing',len(jobs),'narration clips in four languages.',flush=True)
# Separate files and voice sessions are independent. Limit concurrency for the OS speech service.
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for i,_ in enumerate(pool.map(build,jobs),1):
        if i%25==0 or i==len(jobs):print(f'{i}/{len(jobs)} narration clips ready',flush=True)
(ROOT/'content'/'narration.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Narration manifest saved. Audio size:',round(sum(p.stat().st_size for p in OUT.glob('*.m4a'))/1048576,1),'MB',flush=True)
