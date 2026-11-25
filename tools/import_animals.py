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
def get(api=API, **params):
    r=s.get(api,params={'format':'json','formatversion':2,**params},timeout=40);r.raise_for_status(); time.sleep(.4); d=r.json()
    if 'error' in d: raise RuntimeError(d['error'])
    return d.get('query',{}).get('pages',[])
names=[n for group in re.findall(r"\['[^']+','[^']+','([^']+)'\]",(ROOT/'js/animals.js').read_text()) for n in group.split(',')]
assert len(names)==100 and len(set(names))==100
# Broad game labels use representative taxa, not a claim that the label denotes one species.
taxa='Panthera leo|Acinonyx jubatus|Loxodonta africana|Giraffa|Crocuta crocuta|Ceratotherium simum|Diceros bicornis|Equus quagga|Suricata suricatta|Syncerus caffer|Sagittarius serpentarius|Struthio camelus|Mellivora capensis|Canis lupus|Ursus arctos|Vulpes vulpes|Lynx lynx|Cervus elaphus|Sus scrofa|Meles meles|Alces alces|Procyon lotor|Bubo virginianus|Sciurus vulgaris|Ursus americanus|Panthera tigris tigris|Panthera onca|Gorilla gorilla|Pongo|Pan troglodytes|Bradypus|Okapia johnstoni|Tapirus|Harpia harpyja|Eunectes murinus|Dendrobatidae|Ramphastidae|Neofelis nebulosa|Orcinus orca|Carcharodon carcharias|Balaenoptera musculus|Megaptera novaeangliae|Tursiops truncatus|Enteroctopus dofleini|Mobula birostris|Chelonia mydas|Sphyrnidae|Xiphias gladius|Sphyraena barracuda|Enhydra lutris|Odobenus rosmarus|Ursus maritimus|Vulpes lagopus|Lepus arcticus|Ovibos moschatus|Rangifer tarandus|Bubo scandiacus|Monodon monoceros|Delphinapterus leucas|Phoca vitulina|Aptenodytes forsteri|Hydrurga leptonyx|Sterna paradisaea|Camelus dromedarius|Vulpes zerda|Leiurus quinquestriatus|Crotalus cerastes|Gopherus agassizii|Heloderma suspectum|Addax nasomaculatus|Caracal caracal|Felis margarita|Jaculus|Geococcyx californianus|Moloch horridus|Panthera uncia|Aquila chrysaetos|Capra ibex|Oreamnos americanus|Ovis canadensis|Ochotona|Vultur gryphus|Puma concolor|Ailurus fulgens|Hemitragus jemlahicus|Chinchilla|Falco peregrinus|Crocodylus porosus|Crocodylus niloticus|Hippopotamus amphibius|Alligator mississippiensis|Hydrochoerus hydrochaeris|Castor|Ornithorhynchus anatinus|Phoenicopterus|Ardea herodias|Bubalus bubalis|Varanus komodoensis|Ophiophagus hannah|Dynastinae'.split('|')
assert len(taxa)==len(names)
BLOCK=re.compile(r'\b(illustration|drawing|diagram|cartoon|graphic|map|skull|skeleton|blubber|taxidermy|specimen|montage|collage|logo|stamp|fossil|dissection|painting|distribution map|knitting|pattern|karyotype|chromosome|molar|tooth|fighter aircraft|sternite|cross section|hybrid|tea cosy|street scene)\b',re.I)
props=dict(prop='imageinfo',iiprop='url|extmetadata|mime|size',iiurlwidth=800)
def candidate(page):
    info=page.get('imageinfo',[{}])[0]; m=info.get('extmetadata',{}); val=lambda k:clean(m.get(k,{}).get('value',''))
    lic=val('LicenseShortName'); url=val('LicenseUrl'); author=val('Artist'); source=info.get('descriptionurl',''); desc=val('ImageDescription')
    url=re.sub(r'^http://creativecommons.org/','https://creativecommons.org/',url).rstrip('/')
    valid=(lic in ('CC0','CC0 1.0') and url=='https://creativecommons.org/publicdomain/zero/1.0') or (re.fullmatch(r'CC BY (2\.0|2\.5|3\.0|4\.0)',lic) and url=='https://creativecommons.org/licenses/by/'+lic.split()[-1])
    if not valid or not author or not source.startswith('https://commons.wikimedia.org/') or val('Restrictions'): return
    if info.get('mime') not in ('image/jpeg','image/png','image/webp') or BLOCK.search(page['title']+' '+desc): return
    thumb=info.get('thumburl') or info.get('url','')
    if not thumb.startswith('https://upload.wikimedia.org/'): return
    return thumb,dict(author=author,license=lic,license_url=url,source=source,title=page['title'],description=desc,modifications='Resized and converted to WebP')
TARGETS = ['African Lion', 'Honey Badger', 'Red Fox', 'Eurasian Lynx', 'Moose', 'Raccoon', 'Red Squirrel', 'Jaguar', 'Western Gorilla', 'Toucan', 'Blue Whale', 'Humpback Whale', 'Hammerhead Shark', 'Great Barracuda', 'Walrus', 'Polar Bear', 'Arctic Fox', 'Arctic Hare', 'Narwhal', 'Arctic Tern', 'Dromedary Camel', 'Deathstalker Scorpion', 'Sidewinder', 'Desert Tortoise', 'Alpine Ibex', 'Puma', 'Chinchilla', 'Saltwater Crocodile', 'Beaver', 'Great Blue Heron', 'Water Buffalo', 'King Cobra', 'Bengal Tiger', 'Sloth', 'Reindeer', 'Orangutan', 'Red Deer', 'Hippopotamus', 'Cheetah', 'Wild Boar', 'European Badger', 'American Black Bear', 'Orca', 'Swordfish', 'Andean Condor', 'Rhinoceros Beetle', 'Beluga Whale', 'Golden Eagle', 'Flamingo', 'Giraffe', 'Thorny Devil', 'Leopard Seal']
WIKI='https://en.wikipedia.org/w/api.php'
ALIASES={'African Lion':'Lion','Western Gorilla':'Western gorilla','Honey Badger':'Honey badger','Puma':'Cougar','Sidewinder':'Crotalus cerastes','Deathstalker Scorpion':'Deathstalker','Hammerhead Shark':'Hammerhead shark','Toucan':'Toucan','Sloth':'Three-toed sloth','Sea Turtle':'Green sea turtle','Beaver':'Eurasian beaver','Rhinoceros Beetle':'Dynastinae','Water Buffalo':'Water buffalo','Flamingo':'Flamingo'}
def wiki_titles(name,taxon):
    for title in dict.fromkeys([ALIASES.get(name,name),taxon]):
        pages=get(WIKI,action='query',titles=title,redirects=1,prop='pageimages|images',piprop='name',pilicense='free',imlimit=50)
        for page in pages:
            if page.get('pageimage'): yield 'File:'+page['pageimage']
            for item in page.get('images',[]):
                t=item['title']; norm=t.replace('_',' ').lower()
                if t.lower().endswith(('.jpg','.jpeg','.png')) and not BLOCK.search(norm) and any(x.lower() in norm for x in [name,taxon,ALIASES.get(name,name)]): yield t

def queries(name,taxon,errors):
    try:
        titles=list(dict.fromkeys(wiki_titles(name,taxon)))[:12]
        for i in range(0,len(titles),5):
            yield dict(titles='|'.join(titles[i:i+5])), 'wikipedia'
    except Exception as e: errors.append(f'{name}: Wikipedia: {e}')
    for q in [dict(generator='search',gsrsearch='intitle:"'+taxon+'" filetype:bitmap',gsrnamespace=6,gsrlimit=30),dict(generator='categorymembers',gcmtitle='Category:'+taxon,gcmtype='file',gcmlimit=30),dict(generator='search',gsrsearch='intitle:"'+name+'" filetype:bitmap',gsrnamespace=6,gsrlimit=30)]: yield q,'commons'

def run():
    manifest={}; missing=[]; errors=[]; alternatives={}
    assert set(TARGETS)<=set(names)
    for name,taxon in zip(names,taxa):
        if name not in TARGETS: continue
        slug=re.sub('[^a-z0-9]+','-',name.lower()).strip('-'); found=[]; seen=set()
        for query,method in queries(name,taxon,errors):
            if len(found)>=3: break
            try: pages=get(action='query',**query,**props)
            except Exception as e: errors.append(f'{name}: search: {e}'); continue
            if method=='wikipedia':
                order={t.replace('_',' ').casefold():i for i,t in enumerate(query['titles'].split('|'))}
                pages.sort(key=lambda p:order.get(p['title'].replace('_',' ').casefold(),999))
            for page in pages:
                if len(found)>=3: break
                if page['title'] in seen: continue
                seen.add(page['title']); c=candidate(page)
                if not c: continue
                thumb,meta=c
                if method!='wikipedia':
                    evidence=(meta['title']+' '+meta['description']).replace('_',' ').casefold()
                    if not any(x.casefold() in evidence for x in (name,taxon,ALIASES.get(name,name))): continue
                try:
                    r=s.get(thumb,timeout=45);r.raise_for_status(); im=ImageOps.exif_transpose(Image.open(io.BytesIO(r.content))).convert('RGB');im.thumbnail((800,800))
                    if min(im.size)<250: continue
                    path=f'assets/animals/{slug}.webp' if not found else f'alternatives/{slug}-{len(found)+1}.webp'
                    (OUT/path).parent.mkdir(parents=True,exist_ok=True);im.save(OUT/path,'WEBP',quality=82)
                    found.append(dict(meta,path=path,search_taxon=taxon,discovery=method,review_status='pending'))
                except Exception as e: errors.append(f'{name}: {page["title"]}: {e}');continue
        if found: manifest[name]=found[0]; alternatives[name]=found[1:]
        else: missing.append(name)
        print(f'{name}: {len(found)} candidates',flush=True)
        for filename,data in [('IMAGE_CREDITS.json',manifest),('ALTERNATIVES.json',alternatives)]: (OUT/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2))
        (OUT/'MISSING.txt').write_text('\n'.join(missing));(OUT/'ERRORS.txt').write_text('\n'.join(errors))
    (OUT/'REVIEW.txt').write_text('Targeted candidates only. Keep prior ZIPs; do not overwrite approved artwork. Verify species, photo, source and attribution manually. No automatic publication.\n')
    (OUT/'TARGETS.txt').write_text('\n'.join(TARGETS))
    print(f'{len(manifest)} of {len(TARGETS)} targeted species with candidates; {len(missing)} missing')
if __name__=='__main__': run()
