'use strict';
const species=groups.flatMap(([habitat,icon,names])=>names.split(',').map(name=>({name,habitat,icon}))).map((a,id)=>({...a,id,base:stats.map((_,j)=>35+((id*37+j*23+id*j*11)%56))}));
const overrides={'African Lion':[92,81,70,75,78,95],'Cheetah':[58,99,45,65,40,90],'African Elephant':[99,40,98,90,82,75],'Orca':[94,80,82,98,88,95],'Peregrine Falcon':[42,99,40,72,78,95],'Giant Pacific Octopus':[50,48,55,98,65,90]};species.forEach(a=>{if(overrides[a.name])a.base=overrides[a.name]});


// Preserve original IDs and ratings.
for (const a of expansion140) species.push({...a,id:species.length});

// Stable ranking by unboosted total, then strongest stat, then collection ID.
const tierCounts=[160,120,80,50,35,25,15,10,5];
const strengthOrder=[...species].sort((a,b)=>b.base.reduce((x,y)=>x+y,0)-a.base.reduce((x,y)=>x+y,0)||Math.max(...b.base)-Math.max(...a.base)||a.id-b.id);
let rankOffset=0;for(let r=8;r>=0;r--){for(const a of strengthOrder.slice(rankOffset,rankOffset+tierCounts[r]))a.rarity=r;rankOffset+=tierCounts[r];}
const tierPools=rarities.map((_,r)=>species.filter(a=>a.rarity===r));
