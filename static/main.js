import { showHomeScreen, initScreens } from './screens.js';
import { initAdventureScreen } from './adventure.js';

// 常にホーム画面を表示する
function showGameScreen() {
    console.log('登録画面をスキップし、直接ホーム画面を表示します。');
    showHomeScreen();
    initAdventureScreen();
}

// DOMが完全にロードされたらゲーム画面を表示
document.addEventListener('DOMContentLoaded', () => {
    initScreens();
    showGameScreen();
});