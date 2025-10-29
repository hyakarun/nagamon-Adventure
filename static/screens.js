export function initScreens() {
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
        screen.classList.add('hidden');
    });
}

export function showScreen(screenId) {
    console.log(`Attempting to show screen: ${screenId}`);
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
        console.log(`Hiding screen: ${screen.id}`);
        screen.classList.add('hidden');
    });
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        console.log(`Target screen ${screenId} found. Current classList: ${targetScreen.classList}`);
        targetScreen.classList.remove('hidden');
        console.log(`Target screen ${screenId} classList after removing hidden: ${targetScreen.classList}`);
    } else {
        console.error(`Target screen ${screenId} not found.`);
    }
}

export function showLoginScreen() {
    showScreen('login-screen');
}

export function showRegisterScreen() {
    showScreen('register-screen');
}

export function showHomeScreen() {
    showScreen('main-container');
}