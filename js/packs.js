'use strict';
function roll(){let n=Math.random()*100;for(let i=0;i<odds.length;i++){n-=odds[i];if(n<0)return i}return 8}function buy(){if(state.coins<250)return;state.coins-=250;packResult=Array.from({length:3},()=>make(Math.floor(Math.random()*species.length),roll()));state.cards.push(...packResult);save();render()}

