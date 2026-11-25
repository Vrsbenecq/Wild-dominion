'use strict';
const species=groups.flatMap(([habitat,icon,names])=>names.split(',').map(name=>({name,habitat,icon}))).map((a,id)=>({...a,id,base:stats.map((_,j)=>35+((id*37+j*23+id*j*11)%56))}));
const overrides={'African Lion':[92,81,70,75,78,95],'Cheetah':[58,99,45,65,40,90],'African Elephant':[99,40,98,90,82,75],'Orca':[94,80,82,98,88,95],'Peregrine Falcon':[42,99,40,72,78,95],'Giant Pacific Octopus':[50,48,55,98,65,90]};species.forEach(a=>{if(overrides[a.name])a.base=overrides[a.name]});

