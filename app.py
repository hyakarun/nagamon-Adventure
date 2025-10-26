from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os
import csv

import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:/Users/kazuto/OneDrive/ドキュメント/Apps/AdventureGame/users3.db"
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
    return db.session.get(User, int(user_id))

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('character', uselist=False))
    
    # 基本ステータス
    money = db.Column(db.Integer, default=100)
    current_exp = db.Column(db.Integer, default=0)
    required_exp = db.Column(db.Integer, default=10)
    level = db.Column(db.Integer, default=1)
    
    # 新しい基本ステータス
    strength = db.Column(db.Integer, default=10)
    vitality = db.Column(db.Integer, default=10)
    intelligence = db.Column(db.Integer, default=10)
    agility = db.Column(db.Integer, default=10)
    luck = db.Column(db.Integer, default=5)
    charisma = db.Column(db.Integer, default=5)

    # 現在HPはDBに保存
    _hp = db.Column("hp", db.Integer)

    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)
        if self._hp is None:
            self._hp = self.max_hp

    # 派生ステータス (DBには保存されない)
    @property
    def attack(self):
        # 仮の計算式: 攻撃力 = 力
        return self.strength

    @property
    def defense(self):
        # 仮の計算式: 防御力 = 体力
        return self.vitality

    @property
    def max_hp(self):
        # 仮の計算式: 最大HP = 体力 * 5 + レベル * 5
        return self.vitality * 5 + self.level * 5
    
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = max(0, min(value, self.max_hp))
    
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

class Dungeon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class DungeonEnemy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dungeon_id = db.Column(db.Integer, db.ForeignKey('dungeon.id'), nullable=False)
    enemy_id = db.Column(db.Integer, db.ForeignKey('enemy.id'), nullable=False)
    spawn_rate = db.Column(db.Integer, nullable=False)

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
            
            character = Character(
                user_id=user.id, 
                image_url="Farah.png",
                strength=10,
                vitality=10,
                intelligence=10,
                agility=10,
                luck=5,
                charisma=5,
                level=1
            ) # ステータスの初期値を設定
            db.session.add(character)
            db.session.commit()
        
        login_user(user)
        print(f"DEBUG: Test user logged in: {current_user.is_authenticated}")

    return render_template('index.html')

# ... (中略) ...

@app.route('/api/character')
@login_required
def get_character_data():
    character = current_user.character
    
    # ログインしているのにキャラクターが存在しない場合 (通常は起こらないはず)
    if not character:
        character = Character(user_id=current_user.id)
        db.session.add(character)
        db.session.commit()

    character_data = {
        'username': current_user.username,
        'money': character.money,
        'current_exp': character.current_exp,
        'required_exp': character.required_exp,
        'level': character.level,
        'attack': character.attack,
        'defense': character.defense,
        'hp': character.hp,
        'max_hp': character.max_hp,
        'strength': character.strength,
        'vitality': character.vitality,
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
        'image_url': character.image_url # DBから取得した値を使用
    }
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

            # --- 新しいダメージ計算ロジック (再修正) ---
            # ダメージ = 2 * 攻撃力 - 防御力
            base_damage = max(1, 2 * combatant.attack - target.defense)
            
            # 乱数補正 (±10%)
            random_modifier = random.uniform(0.9, 1.1)
            damage = int(base_damage * random_modifier)

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

@app.route('/api/battle/<dungeon_id_str>')
def start_battle(dungeon_id_str):
    if current_user.is_authenticated:
        player_char = current_user.character
    else:
        # ログインしていない場合はダミーキャラクターを作成
        class DummyPlayerChar:
            def __init__(self):
                self.strength = 10
                self.vitality = 10
                self.level = 1
                self.agility = 10
                self.current_exp = 0
                self.is_alive = True
                self.image_url = "Farah.png"
                
                # プロパティを模倣
                self.attack = self.strength
                self.defense = self.vitality
                self.max_hp = self.vitality * 5 + self.level * 5
                self.hp = self.max_hp
        player_char = DummyPlayerChar()
    # 戦闘ロジックで使うための一時的なステータス
    player_char.is_alive = True

    # ダンジョンID(文字列)に基づいてダンジョンを決定
    dungeon_name = None
    if dungeon_id_str == 'dungeon1':
        dungeon_name = '始まるの森'
    # elif dungeon_id_str == 'dungeon2':
    #     dungeon_name = 'ゴブリンの洞窟' # マスターデータに存在しない
    
    if not dungeon_name:
        return jsonify({'error': '無効なダンジョンです'}), 404

    dungeon = Dungeon.query.filter_by(name=dungeon_name).first()
    if not dungeon:
        return jsonify({'error': 'ダンジョンが見つかりませんでした'}), 404

    # ダンジョンに出現する敵を取得
    dungeon_enemies = DungeonEnemy.query.filter_by(dungeon_id=dungeon.id).all()
    if not dungeon_enemies:
        return jsonify({'error': 'ダンジョンに敵が見つかりませんでした'}), 404

    # 出現する敵の中からランダムに選択 (例として3体)
    # spawn_rate を考慮した抽選を行う
    enemy_candidates = [de.enemy_id for de in dungeon_enemies]
    spawn_rates = [de.spawn_rate for de in dungeon_enemies]
    
    num_enemies = 3 # 仮に3体出現
    selected_enemy_ids = random.choices(enemy_candidates, weights=spawn_rates, k=num_enemies)

    enemies = []
    for enemy_id in selected_enemy_ids:
        enemy_template = db.session.get(Enemy, enemy_id)
        if enemy_template:
            enemies.append(BattleEnemy(enemy_template))

    if not enemies:
        return jsonify({'error': '戦闘に出現する敵を準備できませんでした'}), 404

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

        # CSVから敵データを読み込み
        try:
            # 既存の敵データをすべて削除
            Enemy.query.delete()
            
            csv_path = os.path.join(os.path.dirname(__file__), 'masterdata', 'enemies.csv')
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader) # ヘッダー行をスキップ

                # ヘッダーのマッピング
                col_map = {col_name: i for i, col_name in enumerate(header)}

                for row in reader:
                    if not row or not row[col_map['name']]:
                        continue

                    enemy = Enemy(
                        name=row[col_map['name']],
                        max_hp=int(row[col_map['hp']]),
                        attack=int(row[col_map['atk']]),
                        defense=int(row[col_map['def']]),
                        agility=int(row[col_map['agi']]),
                        exp_yield=int(row[col_map['exp']]),
                        image_url=row[col_map['image_url']]
                    )
                    db.session.add(enemy)
            
            db.session.commit()
            print("Loaded enemy data from CSV.")

        except FileNotFoundError:
            print("Enemy CSV file not found. Skipping data loading.")
        except Exception as e:
            print(f"Error loading enemy data: {e}")
            db.session.rollback()

        # CSVからダンジョンデータを読み込み
        try:
            # 既存のダンジョンデータをすべて削除
            DungeonEnemy.query.delete()
            Dungeon.query.delete()

            dungeon_csv_path = os.path.join(os.path.dirname(__file__), 'masterdata', 'dungeons.csv')
            with open(dungeon_csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader) # ヘッダー行をスキップ

                col_map = {col_name: i for i, col_name in enumerate(header)}

                dungeons = {} # dungeon_name をキーにして Dungeon オブジェクトをキャッシュ
                for row in reader:
                    if not row:
                        continue
                    
                    dungeon_name = row[col_map['dungeon_name']]
                    enemy_id = int(row[col_map['enemy_id']])
                    spawn_rate = int(row[col_map['spawn_rate']])

                    # Dungeon オブジェクトを取得または作成
                    if dungeon_name in dungeons:
                        dungeon = dungeons[dungeon_name]
                    else:
                        dungeon = Dungeon.query.filter_by(name=dungeon_name).first()
                        if not dungeon:
                            dungeon = Dungeon(name=dungeon_name)
                            db.session.add(dungeon)
                            db.session.flush() # id を確定させる
                        dungeons[dungeon_name] = dungeon

                    dungeon_enemy = DungeonEnemy(
                        dungeon_id=dungeon.id,
                        enemy_id=enemy_id,
                        spawn_rate=spawn_rate
                    )
                    db.session.add(dungeon_enemy)
            
            db.session.commit()
            print("Loaded dungeon data from CSV.")

        except FileNotFoundError:
            print("Dungeon CSV file not found. Skipping data loading.")
        except Exception as e:
            print(f"Error loading dungeon data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    setup_database(app)
    app.run(debug=True)