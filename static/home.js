import { player } from './player.js';

// APIからキャラクターデータを取得し、ホーム画面を更新する
export async function loadAndDisplayCharacterData() {
    try {
        const response = await fetch('/api/character');

        if (!response.ok) {
            // ログインしていない場合などは、ログインページにリダイレクトされる想定
            // ここではエラーとして処理
            if (response.status === 401) {
                console.error('認証が必要です。ログインしてください。');
                // ログイン画面表示の処理を呼び出すなど
            } else {
                console.error('キャラクターデータの取得に失敗しました。', response.statusText);
            }
            return;
        }

        const data = await response.json();

        // --- player.jsのplayerオブジェクトを更新 ---
        player.name = data.username;
        player.hp = data.hp;
        player.mp = data.mp;
        player.money = data.money;
        player.attack = data.attack;
        player.defense = data.defense;
        player.agility = data.agility;

        // --- ステータスパネルの更新 ---
        document.getElementById('char-username').textContent = data.username;
        document.getElementById('char-level').textContent = data.level;
        document.getElementById('char-current-exp').textContent = data.current_exp;
        document.getElementById('char-required-exp').textContent = data.required_exp;
        document.getElementById('char-money').textContent = data.money;
        document.getElementById('char-hp').textContent = data.hp;
        document.getElementById('char-max-hp').textContent = data.max_hp;
        document.getElementById('char-attack').textContent = data.attack;
        document.getElementById('char-defense').textContent = data.defense;
        document.getElementById('char-strength').textContent = data.strength;
        document.getElementById('char-vitality').textContent = data.vitality;
        document.getElementById('char-intelligence').textContent = data.intelligence;
        document.getElementById('char-agility').textContent = data.agility;
        document.getElementById('char-luck').textContent = data.luck;
        document.getElementById('char-charisma').textContent = data.charisma;

        // --- キャラクター画像の更新 ---
        // 画像は /static/images/ ディレクトリにあると仮定
        const imageUrl = `/static/images/${data.image_url}`;
        document.getElementById('character-image-1').src = imageUrl;


        // --- 装備パネルの更新 ---
        document.getElementById('equip-right-hand').textContent = data.equip_right_hand;
        document.getElementById('equip-left-hand').textContent = data.equip_left_hand;
        document.getElementById('equip-head').textContent = data.equip_head;
        document.getElementById('equip-face-upper').textContent = data.equip_face_upper;
        document.getElementById('equip-face-middle').textContent = data.equip_face_middle;
        document.getElementById('equip-face-lower').textContent = data.equip_face_lower;
        document.getElementById('equip-ears').textContent = data.equip_ears;
        document.getElementById('equip-body').textContent = data.equip_body;
        document.getElementById('equip-arms').textContent = data.equip_arms;
        document.getElementById('equip-hands').textContent = data.equip_hands;
        document.getElementById('equip-waist').textContent = data.equip_waist;
        document.getElementById('equip-legs').textContent = data.equip_legs;
        document.getElementById('equip-shoes').textContent = data.equip_shoes;
        document.getElementById('equip-accessory1').textContent = data.equip_accessory1;
        document.getElementById('equip-accessory2').textContent = data.equip_accessory2;

        // --- スキルパネルの更新 ---
        document.getElementById('active-skills').textContent = data.active_skills || "なし";
        document.getElementById('passive-skills').textContent = data.passive_skills || "なし";

        loadAndDisplayDungeons();

    } catch (error) {
        console.error('キャラクターデータのロード中にエラーが発生しました:', error);
    }
}

export async function loadAndDisplayDungeons() {
    try {
        const response = await fetch('/api/dungeons');
        if (!response.ok) {
            console.error('ダンジョンデータの取得に失敗しました。', response.statusText);
            return;
        }

        const dungeons = await response.json();
        const dungeonSelect = document.getElementById('dungeon-select');
        dungeonSelect.innerHTML = ''; // プルダウンをクリア

        dungeons.forEach(dungeon => {
            const option = document.createElement('option');
            option.value = dungeon.id;
            option.textContent = dungeon.name;
            dungeonSelect.appendChild(option);
        });

    } catch (error) {
        console.error('ダンジョンデータのロード中にエラーが発生しました:', error);
    }
}

let hpRecoveryTimer = null;

export function startHpRecovery() {
    // すでにタイマーが動いていれば何もしない
    if (hpRecoveryTimer) {
        return;
    }

    hpRecoveryTimer = setInterval(async () => {
        try {
            const response = await fetch('/api/character/recover_hp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                // サーバーエラーなどでタイマーを停止
                console.error('HP回復リクエストに失敗しました。', response.statusText);
                clearInterval(hpRecoveryTimer);
                hpRecoveryTimer = null;
                return;
            }

            const data = await response.json();

            if (data.success) {
                console.log('HPが1回復しました。', data.hp);
                // 画面のHP表示を更新
                const charHpElement = document.getElementById('char-hp');
                if (charHpElement) {
                    charHpElement.textContent = data.hp;
                }

                // HPが満タンになったらタイマーを停止
                if (data.hp >= data.max_hp) {
                    console.log('HPが満タンになりました。回復を停止します。');
                    clearInterval(hpRecoveryTimer);
                    hpRecoveryTimer = null;
                }
            } else {
                // HPが満タンなどの理由で回復しなかった場合もタイマーを停止
                if (data.message === 'HP is already full.') {
                    console.log('HPはすでに満タンです。');
                    clearInterval(hpRecoveryTimer);
                    hpRecoveryTimer = null;
                }
            }
        } catch (error) {
            console.error('HP回復処理中にエラーが発生しました:', error);
            clearInterval(hpRecoveryTimer);
            hpRecoveryTimer = null;
        }
    }, 10000); // 10秒ごと
}

export function stopHpRecovery() {
    if (hpRecoveryTimer) {
        clearInterval(hpRecoveryTimer);
        hpRecoveryTimer = null;
        console.log('HP回復を停止しました。');
    }
}

export function initHomeScreen() {
    loadAndDisplayCharacterData();
    const innButton = document.getElementById('inn-button');
    if (innButton) {
        innButton.addEventListener('click', async () => {
            // 現在のキャラクターデータを取得して費用を計算
            const response = await fetch('/api/character');
            const charData = await response.json();
            const cost = charData.level * 1000;

            if (confirm(`${cost} ゴールド消費してHPとMPを全回復しますか？`)) {
                try {
                    const healResponse = await fetch('/api/inn/heal', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });

                    if (!healResponse.ok) {
                        const errorData = await healResponse.json();
                        alert(`回復に失敗しました: ${errorData.message}`);
                        return;
                    }

                    const result = await healResponse.json();
                    if (result.success) {
                        alert(`HPとMPが全回復しました！ ${cost} ゴールド消費しました。`);
                        loadAndDisplayCharacterData(); // キャラクター情報を更新
                    } else {
                        alert(`回復できませんでした: ${result.message}`);
                    }
                } catch (error) {
                    console.error('宿屋での回復処理中にエラーが発生しました:', error);
                    alert('回復処理中にエラーが発生しました。');
                }
            }
        });
    }
}