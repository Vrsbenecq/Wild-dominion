'use strict';
let state=read(SAVE_KEY)||read(BACKUP_KEY)||{coins:500,cards:[0,1,2,13,25,38].map(id=>make(id)),deck:[0,1,2,13,25,38].map(id=>key(make(id))),wins:0,losses:0};
state=migrate(state);
let page='Home',match=null,filter='',habitat='All',rarity='All',packResult=[];const app=document.querySelector('#app');

