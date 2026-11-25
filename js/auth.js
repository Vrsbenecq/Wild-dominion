import {auth} from './firebase.js?v=1.1.0';
import {GoogleAuthProvider,signInWithPopup,signOut,onAuthStateChanged,setPersistence,browserLocalPersistence} from 'https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js';
import {connect,disconnect,flush} from './cloud.js?v=1.1.0';
const login=document.getElementById('google-login'),logout=document.getElementById('google-logout'),retry=document.getElementById('cloud-retry'),status=document.getElementById('cloud-status'),name=document.getElementById('account-name'),photo=document.getElementById('account-photo');
login.onclick=async()=>{try{await signInWithPopup(auth,new GoogleAuthProvider())}catch(e){status.textContent='Login failed: '+e.code+' — try Safari if opened from home screen.'}};
logout.onclick=async()=>{if(!confirm('Sign out? Your local progress stays on this device.'))return;await flush();try{await signOut(auth)}catch(e){status.textContent=e.message}};
retry.onclick=()=>{if(auth.currentUser)connect(auth.currentUser)};
try{await setPersistence(auth,browserLocalPersistence)}catch(e){status.textContent='Login persistence unavailable'}
onAuthStateChanged(auth,u=>{login.hidden=!!u;logout.hidden=retry.hidden=!u;name.textContent=u?(u.displayName||'Google player'):'Guest player';photo.hidden=!u?.photoURL;if(u?.photoURL)photo.src=u.photoURL;else photo.removeAttribute('src');if(u)connect(u);else disconnect()});
