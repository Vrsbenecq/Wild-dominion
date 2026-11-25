'use strict';
function unique(){return [...new Map(state.cards.map(c=>[key(c),c])).values()]}
function collection(){document.querySelector('#collection').innerHTML=unique().filter(c=>species[c.id].name.toLowerCase().includes(filter.toLowerCase())&&(habitat==='All'||species[c.id].habitat===habitat)&&(rarity==='All'||rarities[c.r]===rarity)).sort((a,b)=>b.r-a.r||a.id-b.id).map(c=>card(c,`toggle('${key(c)}')`,state.deck.includes(key(c))?'Remove from deck':'Add to deck',!state.deck.includes(key(c))&&(state.deck.length>=6||state.deck.some(k=>k.split(':')[0]===String(c.id))))).join('')||'<p>No matching cards.</p>'}

