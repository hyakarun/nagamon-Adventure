import { player } from './player.js';
import { showScreen } from './screens.js';

let battleLog = [];
let currentEnemies = [];

export function initAdventureScreen() {
    const adventureButton = document.getElementById('adventure-button');
    if (adventureButton) {
        adventureButton.addEventListener('click', async () => {
            const dungeonSelect = document.getElementById('dungeon-select');
            const selectedDungeonId = dungeonSelect.value;
            if (!selectedDungeonId) {
                alert('ダンジョンを選択してください。');
                return;
            }
            startBattle(selectedDungeonId);
        });
    }
}

async function startBattle(dungeonId) {
    console.log("Attempting to show adventure screen.");
    // showScreen('adventure-screen'); // 削除またはコメントアウト
    battleLog = [];
    currentEnemies = [];
    updateBattleLog('戦闘開始！');

    try {
        const response = await fetch(`/api/battle/${dungeonId}`);
        if (!response.ok) {
            const errorData = await response.json();
            updateBattleLog(`戦闘開始に失敗しました: ${errorData.error}`);
            return;
        }

        const data = await response.json();
        console.log("Battle Data:", data);

        // プレイヤーと敵の初期状態を設定
        player.hp = data.player.hp;
        player.max_hp = data.player.max_hp;
        player.image_url = data.player.image_url; // プレイヤー画像URLを更新

        currentEnemies = data.enemies.map(e => ({
            name: e.name,
            hp: e.hp,
            max_hp: e.max_hp,
            image_url: e.image_url, // 敵画像URLを更新
            is_alive: true // 初期状態では全員生存
        }));

        updateBattleStatus();

        // 詳細なログを順次表示
        for (const logEntry of data.detailed_log) {
            await new Promise(resolve => setTimeout(resolve, 500)); // ログ表示を遅延
            updateBattleLog(logEntry.message);
            // HPなどの状態を更新
            player.hp = logEntry.player_hp;
            // 敵のHPも更新
            logEntry.enemies_state.forEach(enemyState => {
                const enemy = currentEnemies.find(e => e.name === enemyState.name);
                if (enemy) {
                    enemy.hp = enemyState.hp;
                    enemy.is_alive = enemyState.is_alive;
                }
            });
            updateBattleStatus();
        }

        // 最終結果を表示
        await new Promise(resolve => setTimeout(resolve, 1000));
        if (data.result.outcome === 'win') {
            updateBattleLog(`戦闘に勝利した！ ${data.result.exp_gained} の経験値を獲得。`);
            if (data.result.leveled_up) {
                updateBattleLog(`レベルアップ！ ${data.player_new_level} になった！`);
                for (const stat in data.result.stat_increases) {
                    updateBattleLog(`${stat} が ${data.result.stat_increases[stat]} 上がった！`);
                }
            }
        } else if (data.result.outcome === 'lose') {
            updateBattleLog('戦闘に敗北した...');
        } else if (data.result.outcome === 'timeout') {
            updateBattleLog('時間切れで戦闘終了...');
        }
        displayBattleResult(data.result);

    } catch (error) {
        console.error('戦闘中にエラーが発生しました:', error);
        updateBattleLog('エラーが発生し、戦闘が中断されました。');
    }
}

function updateBattleLog(message) {
    console.log("Updating battle log with message:", message);
    battleLog.push(message);
    const battleLogArea = document.getElementById('battle-log-area');
    if (battleLogArea) {
        console.log("battleLogArea found.");
        const p = document.createElement('p');
        p.textContent = message;
        battleLogArea.appendChild(p);
        battleLogArea.scrollTop = battleLogArea.scrollHeight; // スクロールを最下部に
    }
}

function updateBattleStatus() {
    const battleStatusArea = document.getElementById('battle-status-area');
    if (!battleStatusArea) return;

    battleStatusArea.innerHTML = ''; // クリア

    // プレイヤーの状態表示
    const playerStatus = document.createElement('div');
    playerStatus.classList.add('combatants-state');
    playerStatus.innerHTML = `
        <div class="player-state-wrapper">
            <div class="combatant-info">
                <img src="/static/images/${player.image_url}" alt="プレイヤー" class="combatant-image">
                <div class="combatant-stats">
                    <div class="hp-bar-name">${player.name}</div>
                    <div class="hp-bar-container">
                        <div class="hp-bar-health" style="width: ${(player.hp / player.max_hp) * 100}%;"></div>
                        <div class="hp-bar-text">${player.hp}/${player.max_hp}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    battleStatusArea.appendChild(playerStatus);

    // 敵の状態表示
    const enemiesStatusWrapper = document.createElement('div');
    enemiesStatusWrapper.classList.add('enemies-state-wrapper');
    currentEnemies.forEach(enemy => {
        const enemyStatus = document.createElement('div');
        enemyStatus.classList.add('combatant-info');
        enemyStatus.innerHTML = `
            <img src="/static/images/${enemy.image_url}" alt="${enemy.name}" class="combatant-image ${enemy.is_alive ? '' : 'defeated'}">
            <div class="combatant-stats">
                <div class="hp-bar-name">${enemy.name}</div>
                <div class="hp-bar-container">
                    <div class="hp-bar-health" style="width: ${(enemy.hp / enemy.max_hp) * 100}%;"></div>
                    <div class="hp-bar-text">${enemy.hp}/${enemy.max_hp}</div>
                </div>
            </div>
        `;
        enemiesStatusWrapper.appendChild(enemyStatus);
    });
    playerStatus.appendChild(enemiesStatusWrapper);
}

function displayBattleResult(result) {
    const battleResultArea = document.getElementById('battle-result-area');
    if (!battleResultArea) return;

    battleResultArea.innerHTML = ''; // クリア

    const resultMessage = document.createElement('p');
    if (result.outcome === 'win') {
        resultMessage.textContent = `勝利！ ${result.exp_gained} 経験値を獲得しました。`;
    } else if (result.outcome === 'lose') {
        resultMessage.textContent = '敗北...。';
    } else if (result.outcome === 'timeout') {
        resultMessage.textContent = '時間切れ...。';
    }
    battleResultArea.appendChild(resultMessage);

    const backButton = document.createElement('button');
    backButton.textContent = 'ホームに戻る';
    backButton.classList.add('action-button');
    backButton.addEventListener('click', () => {
        showScreen('main-container');
        // ホーム画面に戻った際にキャラクターデータを再読み込みして最新の状態を反映
        // loadAndDisplayCharacterData(); // main.jsで認証後に呼び出されるため不要
    });
    battleResultArea.appendChild(backButton);
}