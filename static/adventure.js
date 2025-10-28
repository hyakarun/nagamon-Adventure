import { showHomeScreen, showAdventureScreen } from './screens.js';
import { loadAndDisplayCharacterData } from './home.js';

// --- Module-level variables ---
let currentDungeonId = null;

// --- DOM Elements ---


const statusArea = document.getElementById('battle-status-area');
const logArea = document.getElementById('battle-log-area');
const resultArea = document.getElementById('battle-result-area');

// --- Helper Functions ---



/**
 * Renders a health bar for a combatant.
 * @param {object} combatant - Player or enemy object with hp and max_hp.
 * @param {boolean} isPlayer - True if the combatant is the player.
 * @returns {string} - HTML string for the health bar.
 */
function createHpBarHtml(combatant, isPlayer = false) {
    const hpPercentage = (combatant.hp / combatant.max_hp) * 100;
    const name = isPlayer ? "プレイヤー" : combatant.name;
    return `
        <div class="hp-bar-name">${name}</div>
        <div class="hp-bar-container">
            <div class="hp-bar-damage"></div>
            <div class="hp-bar-health" style="width: ${hpPercentage}%;"></div>
            <div class="hp-bar-text">${combatant.hp} / ${combatant.max_hp}</div>
        </div>
    `;
}

/**
 * Renders the entire battle result to the screen.
 * @param {object} data - The JSON response from the battle API.
 */
function renderBattleResults(data) {
    // Clear previous results
    statusArea.innerHTML = '';
    logArea.innerHTML = '';
    resultArea.innerHTML = '';

    // 1. Render battle log with images and HP bars per turn
    const logList = document.createElement('div');
    logList.classList.add('battle-log-list');

    data.detailed_log.forEach(logEntry => {
        const logEntryDiv = document.createElement('div');
        logEntryDiv.classList.add('log-entry');

        // メッセージ表示
        const messageP = document.createElement('p');
        messageP.textContent = logEntry.message;
        logEntryDiv.appendChild(messageP);

        // 戦闘状態表示 (画像とHPバー)
        const combatantsStateDiv = document.createElement('div');
        combatantsStateDiv.classList.add('combatants-state');

        // プレイヤーの状態
        const playerWrapperDiv = document.createElement('div');
        playerWrapperDiv.classList.add('player-state-wrapper');
        // 仲間は1人なので、1回だけ表示
        for (let i = 0; i < 1; i++) {
            const playerStateDiv = document.createElement('div');
            playerStateDiv.classList.add('combatant-info');
            playerStateDiv.innerHTML = `
                <img src="/static/images/${data.player.image_url}" alt="プレイヤー" class="combatant-image">
                <div class="combatant-stats">
                    ${createHpBarHtml({ hp: logEntry.player_hp, max_hp: logEntry.player_max_hp, name: "プレイヤー" }, true)}
                </div>
            `;
            playerWrapperDiv.appendChild(playerStateDiv);
        }
        combatantsStateDiv.appendChild(playerWrapperDiv);

        // 敵の状態
        const enemiesWrapperDiv = document.createElement('div');
        enemiesWrapperDiv.classList.add('enemies-state-wrapper');
        logEntry.enemies_state.forEach(enemy => {
            const enemyInfoDiv = document.createElement('div');
            enemyInfoDiv.classList.add('combatant-info');
            const enemyMasterData = data.enemies.find(e => e.name === enemy.name);
            const enemyImageFilename = enemyMasterData ? enemyMasterData.image_url : 'default_enemy.png';
            enemyInfoDiv.innerHTML = `
                <img src="/static/images/${enemyImageFilename}" alt="${enemy.name}" class="combatant-image ${!enemy.is_alive ? 'defeated' : ''}">
                <div class="combatant-stats">
                    ${createHpBarHtml(enemy)}
                </div>
            `;
            if (!enemy.is_alive) {
                // 倒されたテキストは表示しない
            }
            enemiesWrapperDiv.appendChild(enemyInfoDiv);
        });
        combatantsStateDiv.appendChild(enemiesWrapperDiv);

        logEntryDiv.appendChild(combatantsStateDiv);

        logList.appendChild(logEntryDiv);
    });
    logArea.appendChild(logList);

    // 2. Render final result message and buttons
    let resultHTML = `<h3>結果</h3>`;
    if (data.result.outcome === 'win') {
        resultHTML += `<p>勝利！ ${data.result.exp_gained} の経験値を獲得した。</p>`;
        
        if (data.result.leveled_up) {
            resultHTML += `<p>レベルアップ！ レベルが ${data.player_new_level} になった！</p>`;
            if (data.result.stat_increases) {
                for (const stat in data.result.stat_increases) {
                    resultHTML += `<p>${stat} が ${data.result.stat_increases[stat]} 上がった！</p>`;
                }
            }
        }
        // TODO: Display items found
    } else {
        resultHTML += `<p>敗北...。</p>`;
    }
    
    resultHTML += `
        <button id="back-to-home-btn" class="action-button">ホームへ戻る</button>
        <button id="go-deeper-btn" class="action-button">奥へ進む</button>
    `;
    resultArea.innerHTML = resultHTML;

    // 戦闘結果表示後、ホーム画面のキャラクターデータを更新
    loadAndDisplayCharacterData();

    // 3. Add event listeners to new buttons
    document.getElementById('back-to-home-btn').addEventListener('click', () => {
        showHomeScreen();
    });
    document.getElementById('go-deeper-btn').addEventListener('click', () => {
        if (currentDungeonId) {
            startBattle(currentDungeonId);
        } else {
            console.error("現在のダンジョンIDが不明です。ホーム画面に戻ります。");
            showHomeScreen();
        }
    });
}

/**
 * Starts the battle by fetching data from the server.
 * @param {string} dungeonId - The ID of the dungeon to fight in.
 */
async function startBattle(dungeonId) {
    if (!dungeonId) {
        alert('ダンジョンを選択してください。');
        return;
    }
    currentDungeonId = dungeonId; // Save the current dungeon ID

    console.log(`${dungeonId} の冒険を開始します...`);
    showAdventureScreen();

    // Clear screen and show loading message
    statusArea.innerHTML = '';
    resultArea.innerHTML = '';
    logArea.innerHTML = '<p>戦闘中...</p>';

    try {
        const response = await fetch(`/api/battle/${dungeonId}`);
        if (!response.ok) {
            throw new Error(`サーバーエラー: ${response.statusText}`);
        }
        const data = await response.json();
        renderBattleResults(data);

    } catch (error) {
        console.error('戦闘データの取得に失敗しました:', error);
        logArea.innerHTML = `<p>エラーが発生しました: ${error.message}</p>`;
    }
}

export function initAdventureScreen() {
    const startAdventureButton = document.getElementById('adventure-button');
    if (startAdventureButton) {
        startAdventureButton.addEventListener('click', () => {
            const dungeonSelect = document.getElementById('dungeon-select');
            const selectedDungeon = dungeonSelect.value;
            startBattle(selectedDungeon);
        });
    }
}
