let mainContainer;
let adventureScreen;
let loginScreen;
let registerScreen;

export function initScreens() {
    mainContainer = document.getElementById('main-container');
    adventureScreen = document.getElementById('adventure-screen');
    loginScreen = document.getElementById('login-screen');
    registerScreen = document.getElementById('register-screen');
}

function hideAllScreens() {
    if (mainContainer) mainContainer.classList.add('hidden');
    if (adventureScreen) adventureScreen.classList.add('hidden');
    if (loginScreen) loginScreen.classList.add('hidden');
    if (registerScreen) registerScreen.classList.add('hidden');
}

export function showHomeScreen() {
    hideAllScreens();
    if (mainContainer) mainContainer.classList.remove('hidden');
}

export function showAdventureScreen() {
    hideAllScreens();
    if (adventureScreen) adventureScreen.classList.remove('hidden');
}

export function showLoginScreen() {
    hideAllScreens();
    if (loginScreen) loginScreen.classList.remove('hidden');
}

export function showRegisterScreen() {
    hideAllScreens();
    if (registerScreen) registerScreen.classList.remove('hidden');
}