import json, re, pathlib, time, html, urllib.parse, io
import requests
from PIL import Image, ImageOps
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'review'; OUT.mkdir(exist_ok=True)
(OUT/'assets/animals').mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers['User-Agent']='WildDominionPhotoReview/1.0 (https://github.com/Vrsbenecq/Wild-dominion)'
api='https://commons.wikimedia.org/w/api.php'
def clean(v): return html.unescape(re.sub('<[^>]+>',' ',v)).strip()
def get(params):
 r=s.get(api,params={'format':'json',**params},timeout=40);r.raise_for_status();return r.json()
names=[n for group in re.findall(r"\['[^']+','[^']+','([^']+)'\]",(ROOT/'js/animals.js').read_text()) for n in group.split(',')]
assert len(names)==100, f'Expected 100 species, found {len(names)}'
manifest={}; missing=[]
for name in names:
 try:
  data=get({'action':'query','generator':'search','gsrsearch':name+' filetype:bitmap','gsrnamespace':6,'gsrlimit':15,'prop':'imageinfo','iiprop':'url|extmetadata|mime','iiurlwidth':800})
  for page in sorted(data.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',999)):
   info=page['imageinfo'][0];m=info.get('extmetadata',{});val=lambda k:clean(m.get(k,{}).get('value',''))
   lic=val('LicenseShortName');url=val('LicenseUrl');author=val('Artist');source=info.get('descriptionurl','')
   if not ((lic=='CC0' and url.rstrip('/')=='https://creativecommons.org/publicdomain/zero/1.0') or (re.fullmatch(r'CC BY (2\.0|2\.5|3\.0|4\.0)',lic) and url.rstrip('/')=='https://creativecommons.org/licenses/by/'+lic.split()[-1])):continue
   if not author or not source.startswith('https://commons.wikimedia.org/') or val('Restrictions'):continue
   if info.get('mime') not in ('image/jpeg','image/png','image/webp'):continue
   thumb=info.get('thumburl','');
   if not thumb.startswith('https://upload.wikimedia.org/'):continue
   r=s.get(thumb,timeout=45);r.raise_for_status();im=ImageOps.exif_transpose(Image.open(io.BytesIO(r.content))).convert('RGB');im.thumbnail((800,800))
   if min(im.size)<250:continue
   path='assets/animals/'+re.sub('[^a-z0-9]+','-',name.lower()).strip('-')+'.webp';im.save(OUT/path,'WEBP',quality=82)
   manifest[name]={'path':path,'author':author,'license':lic,'license_url':url,'source':source,'title':page['title'],'description':val('ImageDescription')};break
  if name not in manifest:missing.append(name)
 except Exception as e:missing.append(name);print(name,str(e))
 time.sleep(1)
 (OUT/'IMAGE_CREDITS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(OUT/'MISSING.txt').write_text('\n'.join(missing));(OUT/'REVIEW.txt').write_text('CANDIDATES ONLY. Verify each source, author, licence, species and photograph. Remove rejected entries and corresponding images before uploading approved files. No automatic publication.\n')
print(f'{len(manifest)} candidates, {len(missing)} missing')
