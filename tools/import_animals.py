from pathlib import Path
import json, re, pathlib, time, html, io, zipfile
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image, ImageOps
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'review'; OUT.mkdir(exist_ok=True)
s=requests.Session(); s.headers['User-Agent']='WildDominionPhotoReview/1.1 (https://github.com/Vrsbenecq/Wild-dominion)'
s.mount('https://',HTTPAdapter(max_retries=Retry(total=3,backoff_factor=2,status_forcelist=[429,500,502,503,504],respect_retry_after_header=True)))
API='https://commons.wikimedia.org/w/api.php'
def clean(v): return html.unescape(re.sub('<[^>]+>',' ',v)).strip()
def get(**params):
    r=s.get(API,params={'format':'json','formatversion':2,**params},timeout=40);r.raise_for_status(); time.sleep(.4); d=r.json()
    if 'error' in d: raise RuntimeError(d['error'])
    return d.get('query',{}).get('pages',[])
import hashlib, argparse
from PIL import ImageDraw
BLOCK=re.compile(r'\b(illustration|drawing|diagram|cartoon|map|skull|skeleton|taxidermy|specimen|montage|collage|logo|stamp|fossil|painting|antlers?|footprints?|tracks|droppings|feathers?|nest|watermark|knitting|crochet|toy|sculpture)\b',re.I)
errors=[]
def api(url,**params):
    r=s.get(url,params=params,timeout=25); r.raise_for_status(); time.sleep(.6); return r.json()
def licence(v):
    v=str(v or '').lower().strip().rstrip('/').replace('http://','https://')
    if v in ('cc0','cc0 1.0','https://creativecommons.org/publicdomain/zero/1.0'): return 'CC0 1.0','https://creativecommons.org/publicdomain/zero/1.0/'
    m=re.fullmatch(r'(?:cc by |https://creativecommons.org/licenses/by/)(2\.0|2\.5|3\.0|4\.0)',v)
    if m: return 'CC BY '+m[1], 'https://creativecommons.org/licenses/by/'+m[1]+'/'
def make(url,author,lic,source,title,taxon,provider,score):
    l=licence(lic)
    if not l or not author or not source or not url.startswith('https://'): return None
    return dict(url=url,author=author,license=l[0],license_url=l[1],source=source,title=title,search_taxon=taxon,provider=provider,score=score,modifications='Resized and converted to WebP',status='candidate; manual review required')
def inat(taxon):
    endpoint='https://api.inaturalist.org/v1/'
    ts=api(endpoint+'taxa',q=taxon,per_page=30).get('results',[])
    t=next((x for x in ts if x.get('name','').casefold()==taxon.casefold() and x.get('is_active',True)),None)
    if not t: return
    for grade in ('research',):
        obs=api(endpoint+'observations',taxon_id=t['id'],quality_grade=grade,photos='true',photo_license='cc0,cc-by',per_page=100,order_by='votes').get('results',[])
        for o in obs:
            ot=o.get('taxon') or {}; ids=ot.get('ancestor_ids',[])
            if ot.get('id')!=t['id'] and t['id'] not in ids: continue
            if BLOCK.search(str(o.get('description') or '')): continue
            for p in o.get('photos',[]):
                code=p.get('license_code'); lic={'cc0':'CC0','cc-by':'CC BY 4.0'}.get(code)
                # iNaturalist CC BY is normally 4.0; verify exact version on photo page before publishing.
                url=p.get('url','').replace('/square.','/large.')
                c=make(url,p.get('attribution'),lic,f'https://www.inaturalist.org/photos/{p.get("id")}',ot.get('name',''),taxon,'iNaturalist',85 if grade=='research' else 65)
                if c:
                    c['observation']=str(o['id']); yield c; break

def commons(taxon):
    for q in ([dict(generator='search',gsrsearch='\"'+taxon+'\" underwater photograph filetype:bitmap',gsrnamespace=6,gsrlimit=100),dict(generator='search',gsrsearch=('swordfish underwater' if taxon=='Xiphias gladius' else 'narwhal whale swimming')+' filetype:bitmap',gsrnamespace=6,gsrlimit=100)] if taxon in MARINE else []) + [dict(generator='search',gsrsearch='"'+taxon+'" '+('underwater' if taxon in MARINE else 'wildlife')+' filetype:bitmap',gsrnamespace=6,gsrlimit=50),dict(generator='categorymembers',gcmtitle='Category:'+taxon,gcmtype='file',gcmlimit=50),dict(generator='search',gsrsearch='"'+taxon+'" filetype:bitmap',gsrnamespace=6,gsrlimit=50)]:
        for p in get(action='query',prop='imageinfo',iiprop='url|extmetadata|mime|size',iiurlwidth=1200,**q):
            i=p.get('imageinfo',[{}])[0]; m=i.get('extmetadata',{}); v=lambda k:clean(m.get(k,{}).get('value',''))
            desc=p['title']+' '+v('ImageDescription')+' '+v('Categories')
            if BLOCK.search(desc) or v('Restrictions') or taxon.casefold() not in desc.casefold(): continue
            if i.get('mime') not in ('image/jpeg','image/png','image/webp'): continue
            c=make(i.get('thumburl') or i.get('url',''),v('Artist'),v('LicenseUrl'),i.get('descriptionurl'),p['title'],taxon,'Wikimedia',70)
            if c: yield c

def gbif(taxon):
    root='https://api.gbif.org/v1/'
    t=api(root+'species/match',name=taxon,strict='true')
    if t.get('matchType')!='EXACT' or t.get('canonicalName','').casefold()!=taxon.casefold(): return
    for o in api(root+'occurrence/search',taxonKey=t['usageKey'],mediaType='StillImage',limit=60).get('results',[]):
        for p in o.get('media',[]):
            if p.get('type')!='StillImage' or BLOCK.search(str(p.get('title',''))+' '+str(p.get('description',''))): continue
            if o.get('basisOfRecord') not in ('HUMAN_OBSERVATION','OBSERVATION','MACHINE_OBSERVATION'): continue
            c=make(p.get('identifier',''),p.get('creator') or p.get('rightsHolder'),p.get('license'),p.get('references') or f'https://www.gbif.org/occurrence/{o["key"]}',o.get('scientificName',''),taxon,'GBIF',60)
            if c:
                c['observation']=str(o['key']); yield c; break


taxa='Panthera leo|Acinonyx jubatus|Loxodonta africana|Giraffa|Crocuta crocuta|Ceratotherium simum|Diceros bicornis|Equus quagga|Suricata suricatta|Syncerus caffer|Sagittarius serpentarius|Struthio camelus|Mellivora capensis|Canis lupus|Ursus arctos|Vulpes vulpes|Lynx lynx|Cervus elaphus|Sus scrofa|Meles meles|Alces alces|Procyon lotor|Bubo virginianus|Sciurus vulgaris|Ursus americanus|Panthera tigris tigris|Panthera onca|Gorilla gorilla|Pongo|Pan troglodytes|Bradypus|Okapia johnstoni|Tapirus|Harpia harpyja|Eunectes murinus|Dendrobatidae|Ramphastidae|Neofelis nebulosa|Orcinus orca|Carcharodon carcharias|Balaenoptera musculus|Megaptera novaeangliae|Tursiops truncatus|Enteroctopus dofleini|Mobula birostris|Chelonia mydas|Sphyrnidae|Xiphias gladius|Sphyraena barracuda|Enhydra lutris|Odobenus rosmarus|Ursus maritimus|Vulpes lagopus|Lepus arcticus|Ovibos moschatus|Rangifer tarandus|Bubo scandiacus|Monodon monoceros|Delphinapterus leucas|Phoca vitulina|Aptenodytes forsteri|Hydrurga leptonyx|Sterna paradisaea|Camelus dromedarius|Vulpes zerda|Leiurus quinquestriatus|Crotalus cerastes|Gopherus agassizii|Heloderma suspectum|Addax nasomaculatus|Caracal caracal|Felis margarita|Jaculus|Geococcyx californianus|Moloch horridus|Panthera uncia|Aquila chrysaetos|Capra ibex|Oreamnos americanus|Ovis canadensis|Ochotona|Vultur gryphus|Puma concolor|Ailurus fulgens|Hemitragus jemlahicus|Chinchilla|Falco peregrinus|Crocodylus porosus|Crocodylus niloticus|Hippopotamus amphibius|Alligator mississippiensis|Hydrochoerus hydrochaeris|Castor|Ornithorhynchus anatinus|Phoenicopterus|Ardea herodias|Bubalus bubalis|Varanus komodoensis|Ophiophagus hannah|Dynastinae'.split('|')


import os, statistics
from collections import Counter, defaultdict
from PIL import ImageFilter, ImageStat
TARGET={'Swordfish','Narwhal'}
def slug(n): return re.sub('[^a-z0-9]+','-',n.lower()).strip('-')
def atomic(path,obj):
    tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)); tmp.replace(path)
def phash(im):
    a=list(im.convert('L').resize((9,8)).getdata()); return sum((a[y*9+x]>a[y*9+x+1])<< (y*8+x) for y in range(8) for x in range(8))
def catalog():
    f=ROOT/'tools/animal_catalog.json'
    if f.exists():
        rows=json.loads(f.read_text())
        if len(rows)!=500 or len({r['name'] for r in rows})!=500 or any(not r.get('taxon') for r in rows): raise ValueError('Expected 500 unique named animals with taxonomy')
        return rows
    names=[n for group in re.findall(r"\['[^']+','[^']+','([^']+)'\]",(ROOT/'js/animals.js').read_text()) for n in group.split(',')]
    if len(names)!=len(taxa): raise ValueError('Expanded game requires tools/animal_catalog.json with name and taxon for every card')
    return [dict(name=n,taxon=t) for n,t in zip(names,taxa)]
def dashboard(records):
    data=json.dumps(records,ensure_ascii=False).replace('<','\\u003c')
    page="""<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><title>Wild Dominion review</title><style>body{background:#14291f;color:#eee;font:16px system-ui;margin:20px}a{color:#e4c77c}article{border-bottom:1px solid #647b68;padding:16px 0}.grid{display:flex;flex-wrap:wrap;gap:12px}.tile{width:220px}img{width:100%;height:150px;object-fit:contain}button,input{padding:10px;margin:5px}</style><h1>Wild Dominion photo review</h1><p>Check actual species and original photo licence before approving. Scores combine metadata, image quality and experimental CLIP classification; not proof of species or licence.</p><input id=q placeholder='Search animals'><button id=export>Export decisions JSON</button><main id=m></main><script>const data=DATA;let decisions={};try{decisions=JSON.parse(localStorage.getItem('wd-review')||'{}')}catch(e){};const m=document.querySelector('#m');function el(t,txt,parent){let e=document.createElement(t);e.textContent=txt;parent.append(e);return e}function render(){m.replaceChildren();for(const [name,cs] of Object.entries(data)){if(!name.toLowerCase().includes(q.value.toLowerCase()))continue;let a=el('article','',m);el('h2',name,a);let g=el('div','',a);g.className='grid';for(const c of cs){let t=el('div','',g);t.className='tile';let im=el('img','',t);im.src=c.path;im.loading='lazy';el('p',c.title+' | '+c.score+' | '+c.author+' | '+c.license,t);for(const [label,url] of [['Source',c.source],['Licence',c.license_url]]){let l=el('a',label+' ',t);if(/^https:\/\//.test(url))l.href=url;l.target='_blank';l.rel='noopener'}let b=el('button',decisions[name]===c.path?'Selected':'Approve',t);b.onclick=()=>{if(confirm('I checked the species, original licence and attribution')){decisions[name]=c.path;save();render()}}}let b=el('button','Reject / clear',a);b.onclick=()=>{delete decisions[name];save();render()}}}function save(){try{localStorage.setItem('wd-review',JSON.stringify(decisions))}catch(e){}}q.oninput=render;document.querySelector('#export').onclick=()=>{let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(decisions,null,2)],{type:'application/json'}));a.download='decisions.json';a.click()};render()</script>"""
    (OUT/'review.html').write_text(page.replace('DATA',data,1))
MARINE={'Balaenoptera musculus','Xiphias gladius','Monodon monoceros'}
class Visual:
    def __init__(self):
        import torch
        from transformers import CLIPModel, CLIPProcessor
        self.torch=torch; torch.set_num_threads(4)
        self.model=CLIPModel.from_pretrained('openai/clip-vit-base-patch32').eval()
        self.processor=CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
    def score(self,im,name):
        detail={'Swordfish':'whole fish with long flat sword-like bill underwater','Narwhal':'living Arctic whale with spiral tusk or clearly visible body','Blue Whale':'large living blue whale with visible body'}.get(name,'clearly visible living animal')
        labels=[f'a wildlife photograph of a living {name}, {detail}', 'a photograph of antlers or bones without an animal','a photograph of animal footprints or droppings','a dead stranded animal or carcass','a photograph of a tiny distant animal or only a fin above water','a drawing or sculpture or museum specimen','a photograph of a person or unrelated object','a photograph with a large visible text watermark or copyright signature']
        with self.torch.inference_mode():
            inputs=self.processor(text=labels,images=im,return_tensors='pt',padding=True)
            probs=self.model(**inputs).logits_per_image.softmax(dim=1)[0].tolist()
        return probs[0],labels[max(range(len(probs)),key=probs.__getitem__)],probs

def diverse_pool(pool,limit=100):
    groups=defaultdict(list)
    for c in sorted(pool,key=lambda c:-c['score']): groups[c['provider']].append(c)
    out=[]
    while groups and len(out)<limit:
        for k in list(groups):
            out.append(groups[k].pop(0))
            if not groups[k]: del groups[k]
            if len(out)>=limit: break
    return out

def select_diverse(items,limit=3):
    chosen=[]; authors=Counter(); observations=set(); providers=Counter()
    pending=sorted(items,key=lambda c:-c['score'])
    while pending and len(chosen)<limit:
        pending.sort(key=lambda c:(providers[c['provider']],-c['score']))
        c=pending.pop(0); a=c['author'].strip().casefold(); o=(c['provider'],c.get('observation') or c['source'])
        if authors[a]>=2 or o in observations: continue
        chosen.append(c);authors[a]+=1;observations.add(o);providers[c['provider']]+=1
    return sorted(chosen,key=lambda c:-c['score'])

def run():
    ap=argparse.ArgumentParser();ap.add_argument('--all',action='store_true');ap.add_argument('--mode',choices=['missing','upgrade','expansion','final-two','next','retry'],default='next');ap.add_argument('--threshold',type=float,default=.45);ap.add_argument('--pool',type=int,default=30);ap.add_argument('--limit',type=int,default=50);ap.add_argument('--offset',type=int,default=0);ap.add_argument('--decisions',type=Path);ap.add_argument('--repack',action='store_true');ap.add_argument('--state',type=Path,default=ROOT/'import-progress.json');args=ap.parse_args()
    db=OUT/'database.json'; records=json.loads(db.read_text()) if db.exists() else {}; rows=catalog(); errors=[]; hashes=[int(c['dhash'],16) for cs in records.values() for c in cs if 'dhash' in c]
    approved_file=ROOT/'tools/approved_photos.json'
    approved=json.loads(approved_file.read_text()) if approved_file.exists() else {}
    if args.decisions:
        decisions=json.loads(args.decisions.read_text()); import shutil
        dest=ROOT/'approved'; dest.mkdir(exist_ok=True); credits=dict(approved)
        for n,path in decisions.items():
            if n in approved: continue
            c=next(c for c in records[n] if c['path']==path)
            if c['provider']=='Wikimedia':
                pages=get(action='query',titles=c['title'],prop='imageinfo',iiprop='extmetadata')
                meta=pages[0]['imageinfo'][0]['extmetadata']; live=licence(clean(meta.get('LicenseUrl',{}).get('value','')))
                if not live or live[0]!=c['license']: raise ValueError('Licence changed: '+n)
            target='assets/animals/'+slug(n)+'.webp'; f=dest/target;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OUT/path,f);credits[n]={**c,'path':target,'status':'reviewer approved'}
        atomic(dest/'IMAGE_CREDITS.json',credits);atomic(dest/'approved_photos.json',credits)
        with zipfile.ZipFile(OUT/'game-ready.zip','w',zipfile.ZIP_DEFLATED) as z:
            for f in dest.rglob('*'):
                if f.is_file(): z.write(f,f.relative_to(dest))
        return
    if len(rows)!=500: raise ValueError('Expected full 500-animal catalog')
    all_rows=rows
    state=json.loads(args.state.read_text()) if args.state.exists() else {}
    if args.repack:
        selected=rows[args.offset:args.offset+args.limit]
        if not any(records.get(r['name']) for r in selected): raise ValueError('Source artifact has no candidates for requested catalog range; use next mode')
        publish(records, selected, approved, errors, all_rows); return
    if args.mode in ('next','retry'):
        eligible=[r for r in rows[100:] if r['name'] not in approved and ((r['name'] not in state) if args.mode=='next' else (r['name'] in state and state[r['name']].get('candidates',0)==0))]
        rows=eligible[:args.limit]
        if not rows:
            print('No eligible species remaining'); publish({}, [], approved, errors, all_rows, state); return
        records={}; hashes=[]
    visual=Visual()
    if args.mode=='expansion' and not args.all: rows=rows[100:]
    if args.mode not in ('next','retry'): rows=[r for r in rows if args.all or args.mode in ('upgrade','expansion') or (args.mode=='missing' and r['name'] not in approved) or (args.mode=='final-two' and r['name'] in TARGET)][args.offset:args.offset+args.limit]
    rows=[r for r in rows if (r['name'] not in approved or args.mode=='upgrade') and (args.mode=='upgrade' or len(records.get(r['name'],[]))<3)]
    for row in rows:
        n,t=row['name'],row['taxon']; existing=records.get(n,[])
        if args.mode!='upgrade' and len(existing)>=3 and all((OUT/c['path']).exists() and 'visual_probability' in c for c in existing):continue
        pool=[]; found=[c for c in existing if (OUT/c['path']).exists() and 'visual_probability' in c]; urls={c['url'] for c in found}
        for provider in (inat,commons,gbif):
            try:pool.extend(provider(t))
            except Exception as e:errors.append(f'{n} {provider.__name__}: {e}')
        for c in diverse_pool(pool,args.pool):
            if c['url'] in urls or BLOCK.search(c['title']):continue
            urls.add(c['url'])
            try:
                r=s.get(c['url'],timeout=25);r.raise_for_status();im=ImageOps.exif_transpose(Image.open(io.BytesIO(r.content))).convert('RGB')
                if max(im.size)<800 or min(im.size)<400:continue
                h=phash(im)
                if any((h^x).bit_count()<=4 for x in hashes):continue
                gray=im.convert('L');gray.thumbnail((256,256)); contrast=ImageStat.Stat(gray).stddev[0];sharp=ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).mean[0]
                if contrast<8:continue
                probability,label,probs=visual.score(im,n)
                if probability<args.threshold or probability<max(probs[1:]):continue
                c['visual_probability']=round(probability,4);c['visual_label']=label
                c['score']=round(min(100,c['score']*.75+min(12,max(im.size)/100)+min(8,contrast/6)+min(5,sharp/5)),1);c['score']=round(c['score']*.4+probability*60,1);c['dhash']=f'{h:016x}';c['path']='candidates/'+slug(n)+'-'+hashlib.sha256(c['url'].encode()).hexdigest()[:12]+'.webp';c['status']='candidate; manual review required';f=OUT/c['path'];f.parent.mkdir(exist_ok=True);save_small(im,f);hashes.append(h);found.append(c)
            except Exception as e:errors.append(f'{n} download: {e}')
        records[n]=select_diverse(found);atomic(db,records);
        keep={c['path'] for c in records[n]}
        for c in found:
            if c['path'] not in keep: (OUT/c['path']).unlink(missing_ok=True)
        print(n,len(records[n]),'selected from',len(found),flush=True)
    counts=publish(records, rows, approved, errors, all_rows, state)
    if args.mode in ('next','retry'):
        for r in rows: state[r['name']]={'candidates':counts.get(r['name'],0)}
        atomic(args.state,state)
        atomic(ROOT/'review-export/progress.json',state)

def save_small(im, path):
    im=im.copy(); im.thumbnail((800,800))
    for q in (82,72,60,48,35):
        im.save(path,'WEBP',quality=q)
        if path.stat().st_size<=90000: return
    while path.stat().st_size>90000:
        im.thumbnail((max(1,int(im.width*.8)),max(1,int(im.height*.8))))
        im.save(path,'WEBP',quality=35)

def publish(records, rows, approved, errors, all_rows=None, state=None):
    import shutil
    export=ROOT/'review-export'
    if export.exists(): shutil.rmtree(export)
    export.mkdir()
    clean_records={}; seen=set()
    for row in rows:
        n=row['name']; valid=[]
        for c in sorted(records.get(n,[]),key=lambda c:-c.get('score',0)):
            path=c.get('path',''); f=OUT/path
            if not path.startswith('candidates/') or not f.resolve().is_relative_to(OUT.resolve()) or not f.is_file(): continue
            if not licence(c.get('license_url')) or not c.get('author') or not c.get('source') or c.get('search_taxon','').casefold()!=row['taxon'].casefold(): continue
            try:
                with Image.open(f) as im:
                    im=ImageOps.exif_transpose(im).convert('RGB'); h=phash(im)
                    if any((h^x).bit_count()<=4 for x in seen): continue
                    save_small(im,f)
                seen.add(h); valid.append(c)
                if len(valid)==3: break
            except Exception as e: errors.append(f'{n}: {e}')
        if valid: clean_records[n]=valid
    atomic(OUT/'database.json',clean_records)
    keep={c['path'] for cs in clean_records.values() for c in cs}
    for f in (OUT/'candidates').glob('*'):
        if f.is_file() and f.relative_to(OUT).as_posix() not in keep: f.unlink()
    coverage=[dict(name=r['name'],taxon=r['taxon'],approved=r['name'] in approved,candidates=len(clean_records.get(r['name'],[]))) for r in (all_rows if all_rows is not None else rows)]
    selected_names={r['name'] for r in rows}
    for r in coverage:
        r['in_batch']=r['name'] in selected_names
        r['previous_candidates']=(state or {}).get(r['name'],{}).get('candidates')
    atomic(export/'coverage.json',coverage)
    (export/'ERRORS.txt').write_text('\n'.join(errors))
    (export/'MISSING.txt').write_text('\n'.join(r['name'] for r in coverage if r['in_batch'] and not r['approved'] and not r['candidates']))
    # Separate self-contained batches; only shortlisted images enter artifacts.
    names=list(clean_records)
    for start in range(0,len(names),100):
        batch={n:clean_records[n] for n in names[start:start+100]}
        folder=export/f'batch-{start//100+1:02d}'; folder.mkdir()
        for cs in batch.values():
            for c in cs:
                f=folder/c['path']; f.parent.mkdir(exist_ok=True); shutil.copyfile(OUT/c['path'],f)
        dashboard(batch); shutil.copyfile(OUT/'review.html',folder/'review.html')
        atomic(folder/'database.json',batch)
        atomic(folder/'IMAGE_CREDITS.json',{n:cs[0] for n,cs in batch.items()})
        atomic(folder/'ALTERNATIVES.json',{n:cs[1:] for n,cs in batch.items()})
        tiles=[(n,c) for n,cs in batch.items() for c in cs]
        for k in range(0,len(tiles),30):
            chunk=tiles[k:k+30]; sheet=Image.new('RGB',(1000,190*((len(chunk)+4)//5)),'white'); draw=ImageDraw.Draw(sheet)
            for j,(n,c) in enumerate(chunk):
                x=j%5*200;y=j//5*190
                with Image.open(folder/c['path']) as im:
                    im.thumbnail((190,145));sheet.paste(im,(x,y))
                draw.text((x,y+145),n[:30],fill='black');draw.text((x,y+160),Path(c['path']).stem[-12:],fill='black')
            sheet.save(folder/f'contact-{k//30+1}.jpg',quality=75)
        zpath=export/(folder.name+'.zip')
        with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
            for f in folder.rglob('*'):
                if f.is_file(): z.write(f,f.relative_to(folder))
        if zpath.stat().st_size>150_000_000: raise RuntimeError('Archive exceeds 150 MB')
        shutil.rmtree(folder)
    print(f'Batch: {len(clean_records)}/{len(rows)} species with candidates',flush=True)
    return {n:len(cs) for n,cs in clean_records.items()}
if __name__=='__main__':run()
