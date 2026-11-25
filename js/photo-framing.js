'use strict';
const wildlifeFrames = {
  "addax": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "african-buffalo": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "african-elephant": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "american-alligator": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "american-black-bear": {
    "fit": "cover",
    "position": "50% 15%"
  },
  "andean-condor": {
    "fit": "cover",
    "position": "50% 15%"
  },
  "arctic-fox": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "arctic-tern": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "beluga-whale": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "black-rhinoceros": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "brown-bear": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "capybara": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "caracal": {
    "fit": "cover",
    "position": "50% 12%"
  },
  "cheetah": {
    "fit": "cover",
    "position": "50% 15%"
  },
  "chimpanzee": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "clouded-leopard": {
    "fit": "cover",
    "position": "50% 20%"
  },
  "deathstalker-scorpion": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "dromedary-camel": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "emperor-penguin": {
    "fit": "cover",
    "position": "50% 65%"
  },
  "eurasian-lynx": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "fennec-fox": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "giant-pacific-octopus": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "gila-monster": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "golden-eagle": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "gray-wolf": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "great-horned-owl": {
    "fit": "cover",
    "position": "50% 20%"
  },
  "great-white-shark": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "greater-roadrunner": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "harpy-eagle": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "himalayan-tahr": {
    "fit": "cover",
    "position": "50% 35%"
  },
  "jaguar": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "jerboa": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "king-cobra": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "komodo-dragon": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "leopard-seal": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "manta-ray": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "meerkat": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "mountain-goat": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "okapi": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "orangutan": {
    "fit": "cover",
    "position": "50% 8%"
  },
  "orca": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "peregrine-falcon": {
    "fit": "cover",
    "position": "50% 15%"
  },
  "plains-zebra": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "poison-dart-frog": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "polar-bear": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "puma": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "raccoon": {
    "fit": "cover",
    "position": "50% 15%"
  },
  "red-panda": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "sand-cat": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "sea-otter": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "sea-turtle": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "secretary-bird": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "snowy-owl": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "spotted-hyena": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "tapir": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "thorny-devil": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "white-rhinoceros": {
    "fit": "cover",
    "position": "50% 15%"
  },
  "wild-boar": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "nile-crocodile": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "harbor-seal": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "platypus": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "green-anaconda": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "bottlenose-dolphin": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "rhinoceros-beetle": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "african-lion": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "giraffe": {
    "fit": "cover",
    "position": "50% 10%"
  },
  "ostrich": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "honey-badger": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "red-fox": {
    "fit": "cover",
    "position": "50% 20%"
  },
  "red-deer": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "european-badger": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "red-squirrel": {
    "fit": "cover",
    "position": "50% 20%"
  },
  "bengal-tiger": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "western-gorilla": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "sloth": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "humpback-whale": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "hammerhead-shark": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "great-barracuda": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "walrus": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "arctic-hare": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "musk-ox": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "reindeer": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "sidewinder": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "desert-tortoise": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "snow-leopard": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "alpine-ibex": {
    "fit": "cover",
    "position": "50% 35%"
  },
  "bighorn-sheep": {
    "fit": "cover",
    "position": "50% 25%"
  },
  "pika": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "saltwater-crocodile": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "hippopotamus": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "beaver": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "flamingo": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "great-blue-heron": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "water-buffalo": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "moose": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "toucan": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "blue-whale": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "chinchilla": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "swordfish": {
    "fit": "cover",
    "position": "50% 50%"
  },
  "narwhal": {
    "fit": "cover",
    "position": "50% 50%"
  }
};
function frameWildlifePhoto(img){
 const slug=img.getAttribute('src')?.split('/').pop()?.replace(/\.webp$/,'');
 const f=wildlifeFrames[slug]; if(!f)return;
 img.style.objectFit=f.fit; img.style.objectPosition=f.position;
 const art=img.closest('.art'); if(!art)return;
 art.classList.remove('photo-contained');
 art.style.removeProperty('--photo-backdrop');
 img.tabIndex=0; img.setAttribute('role','button'); img.setAttribute('aria-label','View full photograph of '+slug.replaceAll('-',' '));
}
function scanWildlifePhotos(root){if(root.nodeType!==1&&root.nodeType!==9)return;if(root.matches?.('img.animal-photo'))frameWildlifePhoto(root);root.querySelectorAll?.('img.animal-photo').forEach(frameWildlifePhoto);}
function openWildlifePhoto(img){const dialog=document.getElementById('wildlife-photo-dialog');const name=img.closest('.card')?.querySelector('h3')?.textContent||img.getAttribute('aria-label').replace('View full photograph of ','');dialog.querySelector('h2').textContent=name;const full=dialog.querySelector('img');full.src=img.src;full.alt=name;if(!dialog.open)dialog.showModal();}
document.addEventListener('DOMContentLoaded',()=>{scanWildlifePhotos(document);new MutationObserver(records=>{for(const r of records)for(const n of r.addedNodes)scanWildlifePhotos(n);}).observe(document.getElementById('app'),{childList:true,subtree:true});const dialog=document.getElementById('wildlife-photo-dialog');dialog.querySelector('button').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});});
document.addEventListener('click',e=>{if(e.target.matches?.('img.animal-photo[role="button"]'))openWildlifePhoto(e.target);});
document.addEventListener('keydown',e=>{if(e.target.matches?.('img.animal-photo[role="button"]')&&['Enter',' '].includes(e.key)){e.preventDefault();openWildlifePhoto(e.target);}});
