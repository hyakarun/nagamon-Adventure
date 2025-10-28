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
    document.body.classList.add('game-view');
    if (mainContainer) mainContainer.classList.remove('hidden');
}

export function showAdventureScreen() {
    hideAllScreens();
    if (adventureScreen) adventureScreen.classList.remove('hidden');
}

export function showLoginScreen() {
    hideAllScreens();
    document.body.classList.remove('game-view');
    if (loginScreen) loginScreen.classList.remove('hidden');
}

export function showRegisterScreen() {
    hideAllScreens();
    document.body.classList.remove('game-view');
    if (registerScreen) registerScreen.classList.remove('hidden');
}
