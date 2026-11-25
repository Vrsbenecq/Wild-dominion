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
names=[n for group in re.findall(r"\['[^']+','[^']+','([^']+)'\]",(ROOT/'js/animals.js').read_text()) for n in group.split(',')]
assert len(names)==100 and len(set(names))==100
# Broad game labels use representative taxa, not a claim that the label denotes one species.
taxa='Panthera leo|Acinonyx jubatus|Loxodonta africana|Giraffa|Crocuta crocuta|Ceratotherium simum|Diceros bicornis|Equus quagga|Suricata suricatta|Syncerus caffer|Sagittarius serpentarius|Struthio camelus|Mellivora capensis|Canis lupus|Ursus arctos|Vulpes vulpes|Lynx lynx|Cervus elaphus|Sus scrofa|Meles meles|Alces alces|Procyon lotor|Bubo virginianus|Sciurus vulgaris|Ursus americanus|Panthera tigris tigris|Panthera onca|Gorilla gorilla|Pongo|Pan troglodytes|Bradypus|Okapia johnstoni|Tapirus|Harpia harpyja|Eunectes murinus|Dendrobatidae|Ramphastidae|Neofelis nebulosa|Orcinus orca|Carcharodon carcharias|Balaenoptera musculus|Megaptera novaeangliae|Tursiops truncatus|Enteroctopus dofleini|Mobula birostris|Chelonia mydas|Sphyrnidae|Xiphias gladius|Sphyraena barracuda|Enhydra lutris|Odobenus rosmarus|Ursus maritimus|Vulpes lagopus|Lepus arcticus|Ovibos moschatus|Rangifer tarandus|Bubo scandiacus|Monodon monoceros|Delphinapterus leucas|Phoca vitulina|Aptenodytes forsteri|Hydrurga leptonyx|Sterna paradisaea|Camelus dromedarius|Vulpes zerda|Leiurus quinquestriatus|Crotalus cerastes|Gopherus agassizii|Heloderma suspectum|Addax nasomaculatus|Caracal caracal|Felis margarita|Jaculus|Geococcyx californianus|Moloch horridus|Panthera uncia|Aquila chrysaetos|Capra ibex|Oreamnos americanus|Ovis canadensis|Ochotona|Vultur gryphus|Puma concolor|Ailurus fulgens|Hemitragus jemlahicus|Chinchilla|Falco peregrinus|Crocodylus porosus|Crocodylus niloticus|Hippopotamus amphibius|Alligator mississippiensis|Hydrochoerus hydrochaeris|Castor|Ornithorhynchus anatinus|Phoenicopterus|Ardea herodias|Bubalus bubalis|Varanus komodoensis|Ophiophagus hannah|Dynastinae'.split('|')
assert len(taxa)==len(names)
TARGET = {'Bighorn Sheep', 'Bengal Tiger', 'Flamingo', 'Swordfish', 'European Badger', 'Sloth', 'Humpback Whale', 'Sidewinder', 'Red Squirrel', 'Reindeer', 'Great Blue Heron', 'Pika', 'Great Barracuda', 'Snow Leopard', 'Western Gorilla', 'Alpine Ibex', 'African Lion', 'Arctic Hare', 'Red Deer', 'Walrus', 'Giraffe', 'Moose', 'Beaver', 'Saltwater Crocodile', 'Narwhal', 'Hippopotamus', 'Blue Whale', 'Red Fox', 'Desert Tortoise', 'Ostrich', 'Toucan', 'Hammerhead Shark', 'Honey Badger', 'Water Buffalo', 'Musk Ox', 'Chinchilla'}

import hashlib, argparse
from PIL import ImageDraw
BLOCK=re.compile(r'\b(illustration|drawing|diagram|cartoon|map|skull|skeleton|taxidermy|specimen|montage|collage|logo|stamp|fossil|painting|knitting|crochet|toy|sculpture)\b',re.I)
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
    for grade in ('research','needs_id'):
        obs=api(endpoint+'observations',taxon_id=t['id'],quality_grade=grade,photos='true',photo_license='cc0,cc-by',per_page=50,order_by='votes').get('results',[])
        for o in obs:
            ot=o.get('taxon') or {}; ids=ot.get('ancestor_ids',[])
            if ot.get('id')!=t['id'] and t['id'] not in ids: continue
            for p in o.get('photos',[]):
                code=p.get('license_code'); lic={'cc0':'CC0','cc-by':'CC BY 4.0'}.get(code)
                # iNaturalist CC BY is normally 4.0; verify exact version on photo page before publishing.
                url=p.get('url','').replace('/square.','/large.')
                c=make(url,p.get('attribution'),lic,f'https://www.inaturalist.org/photos/{p.get("id")}',ot.get('name',''),taxon,'iNaturalist',85 if grade=='research' else 65)
                if c: yield c

def commons(taxon):
    for q in [dict(generator='categorymembers',gcmtitle='Category:'+taxon,gcmtype='file',gcmlimit=50),dict(generator='search',gsrsearch='"'+taxon+'" filetype:bitmap',gsrnamespace=6,gsrlimit=50)]:
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
            if p.get('type')!='StillImage': continue
            c=make(p.get('identifier',''),p.get('creator') or p.get('rightsHolder'),p.get('license'),p.get('references') or f'https://www.gbif.org/occurrence/{o["key"]}',o.get('scientificName',''),taxon,'GBIF',60)
            if c: yield c

def run():
    parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');args=parser.parse_args()
    manifest={}; alternatives={}; missing=[]; seen=set(); tiles=[]
    for name,taxon in zip(names,taxa):
        if not args.all and name not in TARGET: continue
        slug=re.sub('[^a-z0-9]+','-',name.lower()).strip('-'); pool=[]
        for provider in (inat,commons,gbif):
            try: pool.extend(provider(taxon))
            except Exception as e: errors.append(f'{name} {provider.__name__}: {e}')
        found=[]; urls=set()
        for c in sorted(pool,key=lambda x:-x['score']):
            if len(found)>=5: break
            if c['url'] in urls: continue
            urls.add(c['url'])
            try:
                r=s.get(c['url'],timeout=25);r.raise_for_status(); im=ImageOps.exif_transpose(Image.open(io.BytesIO(r.content))).convert('RGB')
                if max(im.size)<800 or min(im.size)<400: continue
                digest=hashlib.sha256(im.resize((64,64)).tobytes()).hexdigest()
                if digest in seen: continue
                seen.add(digest); c['score']+=min(15,max(im.size)//200); im.thumbnail((1000,1000)); path=f'candidates/{slug}-{len(found)+1}.webp'; (OUT/path).parent.mkdir(exist_ok=True);im.save(OUT/path,'WEBP',quality=85); c['path']=path;found.append(c);tiles.append((name,path))
            except Exception as e: errors.append(f'{name} download: {e}')
        if found: manifest[name]=found[0];alternatives[name]=found[1:]
        else: missing.append(name)
        print(name,len(found),flush=True)
        for fn,obj in [('IMAGE_CREDITS.json',manifest),('ALTERNATIVES.json',alternatives)]: (OUT/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
        (OUT/'MISSING.txt').write_text('\n'.join(missing));(OUT/'ERRORS.txt').write_text('\n'.join(errors))
    for start in range(0,len(tiles),60):
        batch=tiles[start:start+60]; sheet=Image.new('RGB',(1000,160*((len(batch)+4)//5)),'white'); draw=ImageDraw.Draw(sheet)
        for j,(name,path) in enumerate(batch):
            x=j%5*200;y=j//5*160;im=Image.open(OUT/path);im.thumbnail((190,125));sheet.paste(im,(x,y));draw.text((x,y+126),name,fill='black');draw.text((x,y+140),Path(path).stem[-2:],fill='black')
        sheet.save(OUT/f'contact-{start//60+1}.jpg')
    (OUT/'REVIEW.txt').write_text('Candidates only. Verify species, original photo licence and attribution before publication. No existing game assets modified.')
if __name__=='__main__': run()
