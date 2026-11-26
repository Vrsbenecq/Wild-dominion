'use strict';
const make=(id,r=0)=>({id,r:species[id].rarity});const key=c=>c.id+':'+c.r;const SAVE_KEY='wild-dominion-v1', BACKUP_KEY=SAVE_KEY+'-backup';


function migrate(s){return {...s,cards:s.cards.map(c=>make(c.id)),deck:s.deck.map(k=>key(make(Number(k.split(":")[0]))))};}
