import { loadAndDisplayCharacterData, startHpRecovery, stopHpRecovery } from './home.js';

let registerScreen;
let homeScreen;
let adventureScreen;

export function initScreens() {
    registerScreen = document.getElementById('register-screen');
    homeScreen = document.getElementById('home-screen');
    adventureScreen = document.getElementById('adventure-screen');
}

export function showRegisterScreen() {
    if (registerScreen) registerScreen.classList.remove('hidden');
    if (homeScreen) homeScreen.classList.add('hidden');
    if (adventureScreen) adventureScreen.classList.add('hidden');
    stopHpRecovery(); // HP回復を停止
}

export function showHomeScreen() {
    if (homeScreen) homeScreen.classList.remove('hidden');
    if (registerScreen) registerScreen.classList.add('hidden');
    if (adventureScreen) adventureScreen.classList.add('hidden');
    loadAndDisplayCharacterData();
    startHpRecovery(); // HP回復を開始
}

export function showAdventureScreen() {
    if (adventureScreen) adventureScreen.classList.remove('hidden');
    if (registerScreen) registerScreen.classList.add('hidden');
    if (homeScreen) homeScreen.classList.add('hidden');
    stopHpRecovery(); // HP回復を停止
    // showScene('start'); // Will be called from adventure.js
}