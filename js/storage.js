'use strict';
let saveStatus='Not yet saved';
function showSave(){const el=document.querySelector('#save-status');if(el){el.textContent=saveStatus;el.dataset.status=saveStatus.startsWith('Saved on')?'ok':'warning';}}
function save(){const raw=JSON.stringify(state);let primary=false,backup=false;try{localStorage.setItem(SAVE_KEY,raw);primary=localStorage.getItem(SAVE_KEY)===raw}catch{}try{localStorage.setItem(BACKUP_KEY,raw);backup=localStorage.getItem(BACKUP_KEY)===raw}catch{}saveStatus=primary&&backup?'Saved on this browser · '+new Date().toLocaleTimeString():primary||backup?'Saved in one slot only — export a backup':'Saving unavailable — export your progress';showSave();return primary||backup;}
function exportSave(){const blob=new Blob([JSON.stringify({game:'Wild Dominion',version:1,state},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='wild-dominion-save.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);}
async function importSave(input){try{const file=input.files[0];if(!file)return;if(file.size>5000000)throw Error('File too large');const raw=JSON.parse(await file.text());const data=raw.state||raw;if(!valid(data))throw Error('Invalid save file');if(!confirm('Replace your current progress with this backup?'))return;state=data;match=null;packResult=[];save();render();}catch(e){alert('Import failed: '+e.message)}finally{input.value=''}}
function manualSave(){save();}

