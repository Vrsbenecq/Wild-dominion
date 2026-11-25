'use strict';
function valid(s){return !!s && ['coins','wins','losses'].every(k=>Number.isSafeInteger(s[k])&&s[k]>=0) && Array.isArray(s.cards)&&s.cards.every(c=>c&&Number.isInteger(c.id)&&c.id>=0&&c.id<species.length&&Number.isInteger(c.r)&&c.r>=0&&c.r<rarities.length)&&Array.isArray(s.deck)&&s.deck.length<=6&&s.deck.every(k=>typeof k==='string'&&s.cards.some(c=>key(c)===k))&&new Set(s.deck.map(k=>k.split(':')[0])).size===s.deck.length;}
function read(k){try{const raw=JSON.parse(localStorage.getItem(k));const data=raw?.state||raw;return valid(data)?data:null}catch{return null}}

