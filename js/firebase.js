export const config={apiKey:'AIzaSyDoCUv-RdkWcyD42BXWVvhC7eihKsmRr-k',authDomain:'wild-dominion-e648a.firebaseapp.com',projectId:'wild-dominion-e648a',storageBucket:'wild-dominion-e648a.firebasestorage.app',messagingSenderId:'724387466926',appId:'1:724387466926:web:ca39735fad3db00de6e73f'};
import {initializeApp} from 'https://www.gstatic.com/firebasejs/11.10.0/firebase-app.js';
import {getAuth} from 'https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js';
import {getFirestore} from 'https://www.gstatic.com/firebasejs/11.10.0/firebase-firestore.js';
const app=initializeApp(config);export const auth=getAuth(app),db=getFirestore(app);
