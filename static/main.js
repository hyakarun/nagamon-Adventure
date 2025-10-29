import { initAdventureScreen } from './adventure.js';
import { initScreens, showHomeScreen, showLoginScreen } from './screens.js';
import { auth } from './firebase-init.js';
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-auth.js";
import { loadAndDisplayCharacterData, initHomeScreen } from './home.js';

// --- Initialization ---
document.addEventListener('DOMContentLoaded', async () => {
    // initScreens(); // 画面の初期化を無効化
    initHomeScreen();
    initAdventureScreen();

    // 認証ロジックを一時的に無効化し、常にホーム画面を表示
    // onAuthStateChanged(auth, async (user) => {
    //     if (user) {
    //         console.log("User is signed in:", user.uid);
    //         await loadAndDisplayCharacterData();
    //         showHomeScreen();
    //     } else {
    //         console.log("User is signed out.");
    //         showLoginScreen();
    //     }
    // });
});