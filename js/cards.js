'use strict';
function card(c,action='',label='',disabled=false){const a=species[c.id];return `<article class="card" style="--rarity:${colors[c.r]}"><div class="art">${a.icon}</div><div class="rarity">${rarities[c.r].toUpperCase()} · #${String(a.id+1).padStart(3,'0')}</div><h3>${a.name}</h3><small>${a.habitat}</small><div class="stats">${stats.map((s,j)=>`<span>${s.slice(0,3)} <b>${rating(c,j)}</b></span>`).join('')}</div>${action?`<button ${disabled?'disabled':''} onclick="${action}">${label}</button>`:''}</article>`}

