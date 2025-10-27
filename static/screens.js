import { loadAndDisplayCharacterData, startHpRecovery, stopHpRecovery } from './home.js';

let registerScreen;
let homeScreen;
let adventureScreen;

export function initScreens() {
    registerScreen = document.getElementById('register-screen');
    homeScreen = document.getElementById('home-screen');
    adventureScreen = document.getElementById('adventure-screen');
}

function adjustAdventureScreenHeight() {
    const skillsPanel = document.querySelector('.skills-panel');
    const adventureScreen = document.getElementById('adventure-screen');

    if (skillsPanel && adventureScreen) {
        const skillsPanelRect = skillsPanel.getBoundingClientRect();
        const adventureScreenRect = adventureScreen.getBoundingClientRect();
        
        const availableHeight = skillsPanelRect.bottom - adventureScreenRect.top;

        if (availableHeight > 0) {
            adventureScreen.style.height = `${availableHeight}px`;
        }
    }
}

export function showRegisterScreen() {
    if (registerScreen) registerScreen.classList.remove('hidden');
    if (homeScreen) homeScreen.classList.add('hidden');
    if (adventureScreen) adventureScreen.classList.add('hidden');
    stopHpRecovery(); // HP回復を停止
}

export function showHomeScreen() {
    if (adventureScreen) adventureScreen.classList.add('hidden');
    loadAndDisplayCharacterData();
    startHpRecovery(); // HP回復を開始
}

export function showAdventureScreen() {
    if (adventureScreen) adventureScreen.classList.remove('hidden');
    stopHpRecovery(); // HP回復を停止
    // Adjust height when the screen is shown
    adjustAdventureScreenHeight();
}
