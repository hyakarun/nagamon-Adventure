from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os

import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:/Users/kazuto/OneDrive/ドキュメント/Apps/AdventureGame/users2.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Firebase Admin SDK initialization
# サービスアカウントキーファイル名を指定
cred = credentials.Certificate("C:\\Users\\kazuto\\OneDrive\\ドキュメント\\Apps\\AdventureGame\\serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('character', uselist=False))
    
    # 基本ステータス
    money = db.Column(db.Integer, default=100)
    current_exp = db.Column(db.Integer, default=0)
    required_exp = db.Column(db.Integer, default=10)
    level = db.Column(db.Integer, default=1)
    attack = db.Column(db.Integer, default=10)
    defense = db.Column(db.Integer, default=10)
    hp = db.Column(db.Integer, default=50)
    max_hp = db.Column(db.Integer, default=50)
    intelligence = db.Column(db.Integer, default=10)
    agility = db.Column(db.Integer, default=10)
    luck = db.Column(db.Integer, default=5)
    charisma = db.Column(db.Integer, default=5)
    
    # 装備
    equip_right_hand = db.Column(db.String(100), default="なし")
    equip_left_hand = db.Column(db.String(100), default="なし")
    equip_head = db.Column(db.String(100), default="なし")
    equip_face_upper = db.Column(db.String(100), default="なし")
    equip_face_middle = db.Column(db.String(100), default="なし")
    equip_face_lower = db.Column(db.String(100), default="なし")
    equip_ears = db.Column(db.String(100), default="なし")
    equip_body = db.Column(db.String(100), default="なし")
    equip_arms = db.Column(db.String(100), default="なし")
    equip_hands = db.Column(db.String(100), default="なし")
    equip_waist = db.Column(db.String(100), default="なし")
    equip_legs = db.Column(db.String(100), default="なし")
    equip_shoes = db.Column(db.String(100), default="なし")
    equip_accessory1 = db.Column(db.String(100), default="なし")
    equip_accessory2 = db.Column(db.String(100), default="なし")

    # スキル（簡単のため文字列で保持）
    active_skills = db.Column(db.Text, default="")
    passive_skills = db.Column(db.Text, default="")
    
    # キャラクター画像
    image_url = db.Column(db.String(255), default="Farah.png")

class Enemy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    max_hp = db.Column(db.Integer, nullable=False)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    agility = db.Column(db.Integer, nullable=False)
    exp_yield = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    print(f"DEBUG: Accessing / route. app.debug is {app.debug}")
    if app.debug:
        # デバッグモードならテストユーザーでログイン
        test_uid = 'test_user'
        user = User.query.filter_by(firebase_uid=test_uid).first()
        if not user:
            user = User(firebase_uid=test_uid, username='テストユーザー')
            db.session.add(user)
            db.session.flush() # IDを確定
            
            character = Character(user_id=user.id, image_url="Farah.png") # 明示的に設定
            db.session.add(character)
            db.session.commit()
        
        login_user(user)
        print(f"DEBUG: Test user logged in: {current_user.is_authenticated}")

    return render_template('index.html')

# ... (中略) ...

def get_character_data():
    if current_user.is_authenticated:
        character = current_user.character
    else:
        # ログインしていない場合はダミーキャラクターを作成
        class DummyCharacter:
            def __init__(self):
                self.id = 0
                self.user_id = 0
                self.money = 100
                self.current_exp = 0
                self.required_exp = 10
                self.level = 1
                self.attack = 10
                self.defense = 10
                self.hp = 50
                self.max_hp = 50
                self.intelligence = 10
                self.agility = 10
                self.luck = 5
                self.charisma = 5
                self.equip_right_hand = "なし"
                self.equip_left_hand = "なし"
                self.equip_head = "なし"
                self.equip_face_upper = "なし"
                self.equip_face_middle = "なし"
                self.equip_face_lower = "なし"
                self.equip_ears = "なし"
                self.equip_body = "なし"
                self.equip_arms = "なし"
                self.equip_hands = "なし"
                self.equip_waist = "なし"
                self.equip_legs = "なし"
                self.equip_shoes = "なし"
                self.equip_accessory1 = "なし"
                self.equip_accessory2 = "なし"
                self.active_skills = ""
                self.passive_skills = ""
                self.image_url = "Farah.png"
        character = DummyCharacter()

    # フォールバックとして、もしキャラクターが存在しなければ作成 (ログイン時のみ)
    if current_user.is_authenticated and not character:
        character = Character(user_id=current_user.id, image_url="Farah.png")
        db.session.add(character)
        db.session.commit()

    character_data = {
        'username': current_user.username if current_user.is_authenticated else "ゲスト",
        'money': character.money,
        'current_exp': character.current_exp,
        'required_exp': character.required_exp,
        'level': character.level,
        'attack': character.attack,
        'defense': character.defense,
        'hp': character.hp,
        'max_hp': character.max_hp,
        'intelligence': character.intelligence,
        'agility': character.agility,
        'luck': character.luck,
        'charisma': character.charisma,
        'equip_right_hand': character.equip_right_hand,
        'equip_left_hand': character.equip_left_hand,
        'equip_head': character.equip_head,
        'equip_face_upper': character.equip_face_upper,
        'equip_face_middle': character.equip_face_middle,
        'equip_face_lower': character.equip_face_lower,
        'equip_ears': character.equip_ears,
        'equip_body': character.equip_body,
        'equip_arms': character.equip_arms,
        'equip_hands': character.equip_hands,
        'equip_waist': character.equip_waist,
        'equip_legs': character.equip_legs,
        'equip_shoes': character.equip_shoes,
        'equip_accessory1': character.equip_accessory1,
        'equip_accessory2': character.equip_accessory2,
        'active_skills': character.active_skills,
        'passive_skills': character.passive_skills,
        'image_url': "Farah.png" # ここで強制的に上書き
    }
    print(f"DEBUG: image_url being returned: {character_data['image_url']}")
    return jsonify(character_data)


# --- Battle Logic ---
import random

class BattleEnemy:
    def __init__(self, enemy_template):
        self.name = enemy_template.name
        self.max_hp = enemy_template.max_hp
        self.hp = enemy_template.max_hp
        self.attack = enemy_template.attack
        self.defense = enemy_template.defense
        self.agility = enemy_template.agility
        self.exp_yield = enemy_template.exp_yield
        self.image_url = enemy_template.image_url # image_url を追加
        self.item_drops = [] # TODO: アイテムドロップを実装
        self.is_alive = True

def run_battle(player_char, enemies):
    detailed_log = []
    initial_combatants = [player_char] + enemies

    # 初期状態をログに記録
    current_state = {
        'message': "戦闘開始！",
        'player_hp': player_char.hp,
        'player_max_hp': player_char.max_hp,
        'player_is_alive': player_char.is_alive,
        'enemies_state': [{'name': e.name, 'hp': e.hp, 'max_hp': e.max_hp, 'is_alive': e.is_alive} for e in enemies]
    }
    detailed_log.append(current_state)

    turn = 0
    max_turns = 60
    timed_out = False

    while player_char.is_alive and any(e.is_alive for e in enemies):
        turn += 1
        if turn > max_turns:
            timed_out = True
            break

        turn_message = f"\n--- ターン {turn} ---"
        detailed_log.append({
            'message': turn_message,
            'player_hp': player_char.hp,
            'player_max_hp': player_char.max_hp,
            'player_is_alive': player_char.is_alive,
            'enemies_state': [{'name': e.name, 'hp': e.hp, 'max_hp': e.max_hp, 'is_alive': e.is_alive} for e in enemies]
        })
        
        # --- 新しい攻撃順決定ロジック ---
        action_order = []
        turn_combatants = [c for c in initial_combatants if c.is_alive]
        
        while turn_combatants:
            total_agility = sum(c.agility for c in turn_combatants)
            # 全員の素早さが0の場合のフォールバック
            if total_agility == 0:
                actor = random.choice(turn_combatants)
            else:
                weights = [c.agility / total_agility for c in turn_combatants]
                actor = random.choices(turn_combatants, weights=weights, k=1)[0]
            
            action_order.append(actor)
            turn_combatants.remove(actor)

        for combatant in action_order:
            if not combatant.is_alive:
                continue

            # ターゲットを決定
            if combatant == player_char:
                targets = [e for e in enemies if e.is_alive]
                if not targets:
                    break
                target = random.choice(targets)
                actor_name = "プレイヤー"
            else:
                target = player_char
                actor_name = combatant.name

            # --- 新しいダメージ計算ロジック ---
            base_damage = combatant.attack
            # 防御力が0の場合のゼロ除算を避ける
            target_defense = target.defense if target.defense > 0 else 1
            damage_modifier = combatant.attack / target_defense
            random_modifier = random.uniform(0.9, 1.1)
            
            damage = int(base_damage * damage_modifier * random_modifier)
            if damage < 1:
                damage = 1
            
            target.hp -= damage
            action_message = f"{actor_name} の攻撃！ {target.name if target != player_char else 'プレイヤー'} に {damage} のダメージ！"

            if target.hp <= 0:
                target.hp = 0
                target.is_alive = False
                action_message += f" {target.name if target != player_char else 'プレイヤー'} は倒れた。"
            
            # 各行動後に状態をログに記録
            detailed_log.append({
                'message': action_message,
                'player_hp': player_char.hp,
                'player_max_hp': player_char.max_hp,
                'player_is_alive': player_char.is_alive,
                'enemies_state': [{'name': e.name, 'hp': e.hp, 'max_hp': e.max_hp, 'is_alive': e.is_alive} for e in enemies]
            })

    # 戦闘結果
    result = {'outcome': '', 'exp_gained': 0, 'items_found': []}
    if timed_out:
        result['outcome'] = 'lose'
        detailed_log.append({
            'message': f"\n{max_turns}ターンが経過し、時間切れとなった...。",
            'player_hp': player_char.hp,
            'player_max_hp': player_char.max_hp,
            'player_is_alive': player_char.is_alive,
            'enemies_state': [{'name': e.name, 'hp': e.hp, 'max_hp': e.max_hp, 'is_alive': e.is_alive} for e in enemies]
        })
        # 時間切れでもペナルティ
        penalty = int(player_char.money * 0.1)
        player_char.money -= penalty
        if player_char.money < 0:
            player_char.money = 0

    elif player_char.is_alive:
        result['outcome'] = 'win'
        exp_total = sum(e.exp_yield for e in enemies)
        result['exp_gained'] = exp_total
        detailed_log.append({
            'message': f"\n戦闘に勝利した！ {exp_total} の経験値を獲得。",
            'player_hp': player_char.hp,
            'player_max_hp': player_char.max_hp,
            'player_is_alive': player_char.is_alive,
            'enemies_state': [{'name': e.name, 'hp': e.hp, 'max_hp': e.max_hp, 'is_alive': e.is_alive} for e in enemies]
        })
        player_char.current_exp += exp_total

    else:
        result['outcome'] = 'lose'
        detailed_log.append({
            'message': f"\n戦闘に敗北した...。",
            'player_hp': player_char.hp,
            'player_max_hp': player_char.max_hp,
            'player_is_alive': player_char.is_alive,
            'enemies_state': [{'name': e.name, 'hp': e.hp, 'max_hp': e.max_hp, 'is_alive': e.is_alive} for e in enemies]
        })
        penalty = int(player_char.money * 0.1)
        player_char.money -= penalty
        if player_char.money < 0:
            player_char.money = 0
    
    return detailed_log, result

@app.route('/api/battle/<dungeon_id>')
def start_battle(dungeon_id):
    if current_user.is_authenticated:
        player_char = current_user.character
    else:
        # ログインしていない場合はダミーキャラクターを作成
        class DummyPlayerChar:
            def __init__(self):
                self.hp = 50
                self.max_hp = 50
                self.attack = 10
                self.defense = 10
                self.agility = 10
                self.current_exp = 0 # ダミーなので経験値は更新しない
                self.is_alive = True
                self.image_url = "Farah.png" # image_url を追加
        player_char = DummyPlayerChar()
    # 戦闘ロジックで使うための一時的なステータス
    player_char.is_alive = True
    # player_char.max_hp = player_char.hp # この行は削除または修正

    # ダンジョンIDに基づいて敵を生成
    enemies = []
    if dungeon_id == 'dungeon1':
        # TODO: ダンジョンと敵の関連付けをDBで行う
        slime_template = Enemy.query.filter_by(name="スライム").first()
        goblin_template = Enemy.query.filter_by(name="ゴブリン").first()
        if slime_template:
            enemies.append(BattleEnemy(slime_template))
        if goblin_template:
            enemies.append(BattleEnemy(goblin_template))
            
    elif dungeon_id == 'dungeon2':
        # TODO: ダンジョンと敵の関連付けをDBで行う
        orc_template = Enemy.query.filter_by(name="オーク").first()
        skeleton_template = Enemy.query.filter_by(name="スケルトン").first()
        if orc_template:
            enemies.append(BattleEnemy(orc_template))
        if skeleton_template:
            enemies.append(BattleEnemy(skeleton_template))
    else:
        return jsonify({'error': '無効なダンジョンです'}), 404

    if not enemies:
        return jsonify({'error': 'ダンジョンに敵が見つかりませんでした'}), 404

    # 戦闘実行
    detailed_log, result = run_battle(player_char, enemies)

    # 結果をDBに反映
    if current_user.is_authenticated: # ログインしている場合のみDBに反映
        if result['outcome'] == 'win':
            player_char.current_exp += result['exp_gained']
            # TODO: レベルアップ判定と処理
        
        # 勝敗に関わらずセッションをコミット（敗北時の所持金減少などを反映）
        db.session.commit()

    # フロントエンドに返すデータを作成
    # オブジェクトは直接JSON化できないため、辞書に変換
    player_initial_stats = {
        'name': 'プレイヤー',
        'hp': player_char.hp, 
        'max_hp': player_char.max_hp,
        'image_url': player_char.image_url # image_url を追加
    }
    enemies_initial_stats = [
        {'name': e.name, 'hp': e.max_hp, 'max_hp': e.max_hp, 'image_url': e.image_url} for e in enemies
    ]

    response_data = {
        'detailed_log': detailed_log,
        'result': result,
        'player': player_initial_stats,
        'enemies': enemies_initial_stats
    }

    return jsonify(response_data)


@app.route('/api/character/recover_hp', methods=['POST'])
@login_required
def recover_hp():
    character = current_user.character
    if character and character.hp < character.max_hp:
        character.hp += 1
        db.session.commit()
        return jsonify({'success': True, 'hp': character.hp, 'max_hp': character.max_hp})
    elif character:
        return jsonify({'success': False, 'message': 'HP is already full.', 'hp': character.hp, 'max_hp': character.max_hp})
    else:
        return jsonify({'success': False, 'message': 'Character not found.'}), 404

def setup_database(app):
    with app.app_context():
        db.create_all()

        # 敵の初期データ
        if Enemy.query.first() is None:
            enemies = [
                Enemy(name="スライム", max_hp=20, attack=8, defense=5, agility=5, exp_yield=5, image_url="enemy1.png"),
                Enemy(name="ゴブリン", max_hp=30, attack=12, defense=8, agility=8, exp_yield=10, image_url="enemy2.png"),
                Enemy(name="オーク", max_hp=50, attack=15, defense=12, agility=6, exp_yield=20, image_url="orc.png"),
                Enemy(name="スケルトン", max_hp=35, attack=14, defense=10, agility=10, exp_yield=15, image_url="skeleton.png")
            ]
            db.session.bulk_save_objects(enemies)
            db.session.commit()
            print("Added initial enemy data.")

if __name__ == '__main__':
    setup_database(app)
    app.run(debug=True)