import { showHomeScreen, initScreens, showAdventureScreen } from './screens.js';
import { initAdventureScreen } from './adventure.js';
import { loadAndDisplayCharacterData, initHomeScreen } from './home.js';

// 常にホーム画面を表示する
function showGameScreen() {
    console.log('登録画面をスキップし、直接ホーム画面を表示します。');
    showHomeScreen();
    initAdventureScreen();
    loadAndDisplayCharacterData();
    initHomeScreen(); // 追加
}

// DOMが完全にロードされたらゲーム画面を表示
document.addEventListener('DOMContentLoaded', () => {
    initScreens();
    showGameScreen();

    // Adjust height on window resize
    window.addEventListener('resize', () => {
        // Only adjust if the adventure screen is visible
        const adventureScreen = document.getElementById('adventure-screen');
        if (adventureScreen && !adventureScreen.classList.contains('hidden')) {
            showAdventureScreen(); // This will call adjustAdventureScreenHeight
        }
    });
});
