import { loadAndDisplayCharacterData } from './home.js';

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
}

export function showHomeScreen() {
    if (homeScreen) homeScreen.classList.remove('hidden');
    if (registerScreen) registerScreen.classList.add('hidden');
    if (adventureScreen) adventureScreen.classList.add('hidden');
    loadAndDisplayCharacterData();
}

export function showAdventureScreen() {
    if (adventureScreen) adventureScreen.classList.remove('hidden');
    if (registerScreen) registerScreen.classList.add('hidden');
    if (homeScreen) homeScreen.classList.add('hidden');
    // showScene('start'); // Will be called from adventure.js
}