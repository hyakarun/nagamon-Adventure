from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os
import csv

import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'users3.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.exp_table = {} # 経験値テーブルを保持する辞書
app.chara_pram_table = {} # キャラクターパラメータテーブルを保持する辞書 # 追加

db = SQLAlchemy(app)

# Firebase Admin SDK initialization
# サービスアカウントキーファイル名を指定
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "serviceAccountKey.json"))
# --- ここから追加 ---
print(f"--- Credentials object created: {cred} ---")

# --- ここから追加 ---
print("Attempting to initialize Firebase Admin SDK...")
# --- ここまで追加 ---
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
# --- ここから追加 ---
print("Firebase Admin SDK initialized successfully.")
# --- ここまで追加 ---

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
    # 現在MPはDBに保存
    _mp = db.Column("mp", db.Integer)

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
        # chara_pram_tableから現在のレベルに対応するHPを取得
        stats = app.chara_pram_table.get(self.level)
        if stats and 'hp' in stats:
            return stats['hp']
        # フォールバック
        return self.vitality * 5 + self.level * 5
    
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = max(0, min(value, self.max_hp))

    @property
    def max_mp(self):
        # 仮の計算式: 最大MP = 賢さ * 3 + レベル * 3
        return self.intelligence * 3 + self.level * 3

    @property
    def mp(self):
        return self._mp

    @mp.setter
    def mp(self, value):
        self._mp = max(0, min(value, self.max_mp))

    def add_exp(self, exp_to_add):
        self.current_exp += exp_to_add
        leveled_up = False
        stat_increases = {}
        
        if not app.exp_table or not app.chara_pram_table: # chara_pram_table もチェック
            return False, {}

        while self.level < max(app.exp_table.keys()) and self.current_exp >= app.exp_table.get(self.level + 1, {}).get('total_exp', float('inf')):
            leveled_up = True
            old_level = self.level
            self.level += 1
            
            # chara_pram_table から新しいステータスを取得
            new_stats = app.chara_pram_table.get(self.level)
            if new_stats:
                # 各ステータスの差分を計算し、stat_increases に格納
                if 'hp' in new_stats:
                    stat_increases['hp'] = new_stats['hp'] - self.max_hp # max_hp はプロパティなので直接変更できない
                    # HPはmax_hpが上がった分だけ増やす
                    self.hp += stat_increases['hp']
                if 'str' in new_stats:
                    stat_increases['strength'] = new_stats['str'] - self.strength
                    self.strength = new_stats['str']
                if 'vit' in new_stats:
                    stat_increases['vitality'] = new_stats['vit'] - self.vitality
                    self.vitality = new_stats['vit']
                if 'int' in new_stats:
                    stat_increases['intelligence'] = new_stats['int'] - self.intelligence
                    self.intelligence = new_stats['int']
                if 'agi' in new_stats:
                    stat_increases['agility'] = new_stats['agi'] - self.agility
                    self.agility = new_stats['agi']
                if 'luk' in new_stats:
                    stat_increases['luck'] = new_stats['luk'] - self.luck
                    self.luck = new_stats['luk']
                if 'vis' in new_stats: # charisma
                    stat_increases['charisma'] = new_stats['vis'] - self.charisma
                    self.charisma = new_stats['vis']
            
            # 次のレベルに必要な経験値を更新
            self.required_exp = app.exp_table.get(self.level, {}).get('next_exp', self.required_exp) # 変更

        return leveled_up, stat_increases
    
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
    image_url = db.Column(db.String(255), nullable=False) # image_url を追加

class Dungeon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    max_enemies = db.Column(db.Integer, default=3) # 追加

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
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    id_token = data.get('idToken')
    username = data.get('username') # 新規登録時に送られてくる

    try:
        decoded_token = auth.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']

        user = User.query.filter_by(firebase_uid=firebase_uid).first()

        if not user:
            # ユーザーが存在しない場合は新規作成
            if not username:
                # Googleログインなどでusernameがない場合は、Firebaseの表示名を使う
                username = decoded_token.get('name', '名無しの冒険者')

            user = User(firebase_uid=firebase_uid, username=username)
            db.session.add(user)
            db.session.flush()  # user.id を確定させる

            # 新しいキャラクターを作成
            # chara_pram_tableからLv1のステータスを取得
            lv1_stats = app.chara_pram_table.get(1, {})
            if not lv1_stats:
                # 万が一テーブルが読み込めていない場合のフォールバック
                lv1_stats = {'str': 10, 'vit': 10, 'int': 10, 'agi': 10, 'luk': 10, 'vis': 10}

            character = Character(
                user_id=user.id,
                image_url="baby.png", # 画像を固定
                strength=lv1_stats.get('str', 10),
                vitality=lv1_stats.get('vit', 10),
                intelligence=lv1_stats.get('int', 10),
                agility=lv1_stats.get('agi', 10),
                luck=lv1_stats.get('luk', 10),
                charisma=lv1_stats.get('vis', 10)
            )
            # 明示的にレベルと体力を設定 (max_hpアクセス前に属性を確実に設定するため)
            character.level = lv1_stats.get('lv', 1)
            character.vitality = lv1_stats.get('vit', 10)

            # HPとMPの初期値を設定
            character.hp = character.max_hp
            character.mp = character.max_mp

            db.session.add(character)
            db.session.commit()
            print(f"New user and character created for {username} (UID: {firebase_uid})")

        login_user(user)
        print(f"--- User logged in (in /login) ---")
        print(f"current_user.is_authenticated: {current_user.is_authenticated}")
        print(f"------------------------------------")
        return jsonify({'success': True, 'username': user.username})

    except auth.InvalidIdTokenError as e: # Exceptionをキャプチャ
        print(f"Firebase Invalid ID Token Error: {e}") # Exceptionをそのまま表示
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Invalid ID token'}), 401
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/users')
def get_users():
    users = User.query.all()
    user_list = [{'id': user.id, 'username': user.username} for user in users]
    return jsonify(user_list)


# ... (中略) ...

@app.route('/api/character')
@login_required
def get_character_data():
    print(f"--- User status (in /api/character) ---")
    print(f"current_user.is_authenticated: {current_user.is_authenticated}")
    print(f"-----------------------------------------")
    print(f"DEBUG: current_user: {current_user}")
    print(f"DEBUG: current_user.character: {current_user.character}")
    character = current_user.character
    
    # ログインしているのにキャラクターが存在しない場合 (通常は起こらないはず)
    if not character:
        character = Character(user_id=current_user.id)
        db.session.add(character)
        db.session.commit()

    print(f"DEBUG: Character data before jsonify: {current_user.username}, Level: {character.level}, HP: {character.hp}/{character.max_hp}, MP: {character.mp}/{character.max_mp}, Image: {character.image_url}") # 追加

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
        'mp': character.mp, # 追加
        'max_mp': character.max_mp, # 追加
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

            # --- 仕様書に基づく新しいダメージ計算ロジック ---
            base_damage = combatant.attack

            # 防御力による補正
            # 攻撃が0の場合のゼロ除算を避ける
            if combatant.attack > 0:
                defense_modifier = (combatant.attack - target.defense) / combatant.attack
            else:
                defense_modifier = 0
            
            # 補正率を±50%に制限
            defense_modifier = max(-0.5, min(0.5, defense_modifier))
            
            modified_damage = base_damage * (1 + defense_modifier)

            # 乱数補正 (±10%)
            random_modifier = random.uniform(0.9, 1.1)
            damage = int(modified_damage * random_modifier)

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
        leveled_up, stat_increases = player_char.add_exp(exp_total)
        result['leveled_up'] = leveled_up
        result['stat_increases'] = stat_increases

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
    dungeon_id = int(dungeon_id_str.replace('dungeon', '')) # 変更
    dungeon = Dungeon.query.get(dungeon_id) # 変更
    
    if not dungeon:
        return jsonify({'error': '無効なダンジョンです'}), 404

    print(f"DEBUG: Dungeon found: {dungeon.name}, max_enemies: {dungeon.max_enemies}") # 追加

    # ダンジョンに出現する敵を取得
    dungeon_enemies = DungeonEnemy.query.filter_by(dungeon_id=dungeon.id).all()
    if not dungeon_enemies:
        return jsonify({'error': 'ダンジョンに敵が見つかりませんでした'}), 404

    # 画像が存在する敵のみを抽選対象にする
    available_enemies = []
    images_path = os.path.join(os.path.dirname(__file__), 'static', 'images')
    for de in dungeon_enemies:
        enemy_template = db.session.get(Enemy, de.enemy_id)
        if enemy_template:
            image_path = os.path.join(images_path, enemy_template.image_url)
            if os.path.exists(image_path):
                available_enemies.append(de)

    if not available_enemies:
        return jsonify({'error': '表示可能な敵が見つかりませんでした'}), 404

    # 出現する敵の中からランダムに選択 (例として3体)
    # spawn_rate を考慮した抽選を行う
    enemy_candidates = [de.enemy_id for de in available_enemies]
    spawn_rates = [de.spawn_rate for de in available_enemies]
    
    num_enemies = dungeon.max_enemies
    # 候補が num_enemies より少ない場合は、いるだけ出現させる
    if len(enemy_candidates) < num_enemies:
        num_enemies = len(enemy_candidates)

    print(f"DEBUG: Selecting {num_enemies} enemies from {len(enemy_candidates)} candidates.") # 追加
    print(f"DEBUG: Enemy candidates: {enemy_candidates}, Spawn rates: {spawn_rates}") # 追加

    # random.choices の weights がすべて0の場合にエラーになる可能性があるのでチェック
    if sum(spawn_rates) == 0:
        # すべての spawn_rate が0の場合は均等に抽選
        selected_enemy_ids = random.choices(enemy_candidates, k=num_enemies)
    else:
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
            # レベルアップ処理は run_battle の中で行われる
            pass
        
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
        'enemies': enemies_initial_stats,
        'player_new_level': player_char.level,
        'player_new_current_exp': player_char.current_exp,
        'player_new_required_exp': app.exp_table.get(player_char.level + 1, {}).get('total_exp', player_char.required_exp),
        'player_new_strength': player_char.strength,
        'player_new_vitality': player_char.vitality,
        'player_new_intelligence': player_char.intelligence,
        'player_new_agility': player_char.agility,
        'player_new_luck': player_char.luck,
        'player_new_charisma': player_char.charisma,
        'player_new_attack': player_char.attack,
        'player_new_defense': player_char.defense,
        'player_new_max_hp': player_char.max_hp,
        'player_new_hp': player_char.hp,
        'player_new_mp': player_char.mp, # 追加
        'player_new_max_mp': player_char.max_mp, # 追加
    }

    return jsonify(response_data)

@app.route('/api/dungeons')
def get_dungeons():
    dungeons = Dungeon.query.all()
    dungeon_list = [{'id': f'dungeon{d.id}', 'name': d.name} for d in dungeons]
    return jsonify(dungeon_list)


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
        print("Database tables created.") # 追加

        # CSVから敵データを読み込み
        try:
            print("Loading enemy data...") # 追加
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
                reader = csv.DictReader(csvfile) # 変更

                # col_map の作成は不要になります

                dungeons = {} # dungeon_name をキーにして Dungeon オブジェクトをキャッシュ
                for row in reader:
                    if not row:
                        continue
                    
                    # CSVの列からデータを取得
                    csv_dungeon_name = row['dungeon_name'] # 変更
                    csv_enemy_id = int(row['enemy_id']) # 変更
                    csv_spawn_rate = int(row['spawn_rate']) # 変更
                    csv_max_enemies = int(row['max_enemies']) # 変更

                    # Dungeon オブジェクトを取得または作成
                    dungeon = Dungeon.query.filter_by(name=csv_dungeon_name).first()
                    if not dungeon:
                        dungeon = Dungeon(name=csv_dungeon_name, max_enemies=csv_max_enemies)
                        db.session.add(dungeon)
                        db.session.flush() # id を確定させる
                    
                    # DungeonEnemy を作成
                    dungeon_enemy = DungeonEnemy(
                        dungeon_id=dungeon.id, # Dungeon オブジェクトの id を使用
                        enemy_id=csv_enemy_id,
                        spawn_rate=csv_spawn_rate
                    )
                    db.session.add(dungeon_enemy)
            
            db.session.commit()
            print("Loaded dungeon data from CSV.")

        except FileNotFoundError:
            print("Dungeon CSV file not found. Skipping data loading.")
        except Exception as e:
            print(f"Error loading dungeon data: {e}")
            db.session.rollback()

        # CSVから経験値テーブルを読み込み
        try:
            exp_csv_path = os.path.join(os.path.dirname(__file__), 'masterdata', 'exp_table.csv')
            with open(exp_csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # レベルをキーにした辞書の辞書を作成
                app.exp_table = {int(row['lv']): {
                    'total_exp': int(row['total_exp']),
                    'next_exp': int(row['next_exp']),
                    '上昇量': int(row['上昇量'])
                } for row in reader}
            
            print("Loaded experience table from CSV.")

        except FileNotFoundError:
            print("Experience table CSV file not found. Skipping data loading.")
        except Exception as e:
            print(f"Error loading experience table data: {e}")

        # CSVからキャラクターパラメータテーブルを読み込み
        try:
            chara_pram_csv_path = os.path.join(os.path.dirname(__file__), 'masterdata', 'chara_pram.csv')
            with open(chara_pram_csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # レベルをキーにした辞書の辞書を作成
                app.chara_pram_table = {int(row['lv']): {
                    'hp': int(row['hp']),
                    'str': int(row['str']),
                    'vit': int(row['vit']),
                    'int': int(row['int']),
                    'agi': int(row['agi']),
                    'luk': int(row['luk']),
                    'vis': int(row['vis']) # charisma
                } for row in reader}
            
            print("Loaded character parameter table from CSV.")

        except FileNotFoundError:
            print("Character parameter table CSV file not found. Skipping data loading.")
        except Exception as e:
            print(f"Error loading character parameter table data: {e}")

    # --- ここから追加 ---
    print("--- Initial Master Data ---")
    print("EXP Table Loaded:", bool(app.exp_table))
    print("Chara Pram Table Loaded:", bool(app.chara_pram_table))
    if app.chara_pram_table:
        print("Lv1 Chara Pram:", app.chara_pram_table.get(1))
    print("--------------------------")

if __name__ == '__main__':
    setup_database(app)
    app.run(debug=True)
