import { showAdventureScreen } from './screens.js';

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

        // --- ステータスパネルの更新 ---
        document.getElementById('char-username').textContent = data.username;
        document.getElementById('char-level').textContent = data.level;
        document.getElementById('char-current-exp').textContent = data.current_exp;
        document.getElementById('char-required-exp').textContent = data.required_exp;
        document.getElementById('char-money').textContent = data.money;
        document.getElementById('char-hp').textContent = data.hp;
        document.getElementById('char-attack').textContent = data.attack;
        document.getElementById('char-defense').textContent = data.defense;
        document.getElementById('char-intelligence').textContent = data.intelligence;
        document.getElementById('char-agility').textContent = data.agility;
        document.getElementById('char-luck').textContent = data.luck;
        document.getElementById('char-charisma').textContent = data.charisma;

        // --- キャラクター画像の更新 ---
        // 画像は /static/images/ ディレクトリにあると仮定
        const imageUrl = `/static/images/${data.image_url}`;
        document.getElementById('character-image').src = imageUrl;


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

    } catch (error) {
        console.error('キャラクターデータのロード中にエラーが発生しました:', error);
    }
}
