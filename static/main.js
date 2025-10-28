import { auth } from './firebase-init.js';
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-auth.js";
import { initScreens, showHomeScreen, showLoginScreen } from './screens.js';
import { loadAndDisplayCharacterData, initHomeScreen } from './home.js';
import { initAdventureScreen } from './adventure.js';

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initScreens();
    initHomeScreen();
    initAdventureScreen();

    onAuthStateChanged(auth, async (user) => {
        if (user) {
            // User is signed in.
            console.log("User is signed in:", user.uid);
            showHomeScreen();
        } else {
            // User is signed out.
            console.log("User is signed out.");
            showLoginScreen();
        }
    });
});
