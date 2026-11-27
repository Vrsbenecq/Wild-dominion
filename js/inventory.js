'use strict';
function inventoryMeta(){const m=state.inventoryMeta;if(!m||typeof m!=='object'||Array.isArray(m))state.inventoryMeta={};return state.inventoryMeta;}
function acquiredAt(c){return Number(inventoryMeta()[c.id]?.at)||0;}
function isNewCard(c){return inventoryMeta()[c.id]?.unseen===true;}
function markViewed(id){const m=inventoryMeta()[id];if(!m?.unseen)return;m.unseen=false;save();for(const b of document.querySelectorAll('[data-new-card="'+id+'"]'))b.remove();}
function acquireCards(cards){const known=new Set(state.cards.map(c=>c.id));const meta=inventoryMeta();let stamp=Math.max(Date.now(),...Object.values(meta).map(m=>Number(m?.at)||0))+1;for(const c of cards){const fresh=!known.has(c.id);meta[c.id]={at:stamp++,unseen:fresh||meta[c.id]?.unseen===true};c.newSpecies=fresh;if(fresh)wdEvent("species");known.add(c.id);state.cards.push({id:c.id,r:c.r});} }
