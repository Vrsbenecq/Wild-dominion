'use strict';
function toggle(k){if(state.deck.includes(k))state.deck=state.deck.filter(x=>x!==k);else if(state.deck.length<6&&!state.deck.some(x=>x.split(':')[0]===k.split(':')[0])&&state.cards.some(c=>key(c)===k))state.deck.push(k);save();render()}

