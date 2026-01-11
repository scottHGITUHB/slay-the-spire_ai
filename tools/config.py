from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parent.parent

# ---------- 基础路径 ----------
DATA_SCENE = ROOT / 'data' / 'scene'
DATA_ENEMY = ROOT / 'data' / 'enemy'
DATA_CARD = ROOT / 'data' / 'card'

MATCH_THRESHOLD = 0.75

# ---------- 全屏场景模板 ----------
SCENE_MAP: Dict[str, Tuple[str, str]] = {
    "start": ("开始场景", "start.png"),
    "chose_mode": ("选择模式", "chose_mode.png"),
    "chose_person": ("选择人物", "chose_person.png"),
    "first_chose": ("第一关选择增益", "first_chose.png"),
    "map": ("地图", "map.png"),
    "battle": ("战斗中", "battle.png"),
    "battle_settlement": ("战斗结算/奖励", "battle_settlement.png"),
    "chose_one_card": ("选择一张卡牌", "chose_card.png"),
    "advance": ("前进", "advance.png"),
    "shop": ("商店", "shop.png"),
    "rest": ("休整处", "rest.png"),
    "Box": ("宝箱", "box.png"),
    "???room": ("???房间", "room.png"),
    "failure": ("战斗失败", "failure.png"),
    "victory": ("胜利", "victory.png"),
    "lose1": ("失败1", "lose.png"),
    "lose2": ("失败2", "lose2.png"),
}

# ---------- 敌人意图模板 ----------
INTENT_MAP: Dict[str, Tuple[str, str]] = {
    "attack1": ("攻击1", "attack1.png"),
    "attack2": ("攻击2", "attack2.png"),
    "attack3": ("攻击3", "attack3.png"),
    "attack4": ("强化攻击", "attack4.png"),
    "attack5": ("至强一击", "attack5.png"),
    "unknown": ("未知意图", "unknown.png"),
    "sleep": ("睡觉", "sleep.png"),
    "defend": ("防御", "defend.png"),
    "debuff": ("减益", "debuff.png"),
    "debuff2": ("强化减益", "debuff2.png"),
    "strength": ("强化", "strength.png")
}

# ---------- 手牌类型模板 ----------
CARD_KIND_MAP: Dict[str, Tuple[str, str]] = {
    "attack": ("攻击牌", "card_kind_attack.png"),
    "defend": ("防御牌", "card_kind_defend.png"),
    "skill": ("技能牌", "card_kind_skill.png"),
    "power": ("能力牌", "card_kind_power.png"),
    "status": ("状态牌", "card_kind_status.png"),
}

# ========== 能量消耗模板（拆分大小） ==========
# 大卡牌能量模板（技能、防御、能力、诅咒等）
BIG_ENERGY_MAP: Dict[str, Tuple[str, str]] = {
    "energy_0": ("0费", "energy_0.png"),
    "energy_1": ("1费", "energy_1.png"),
    "energy_2": ("2费", "energy_2.png"),
    "energy_3": ("3费", "energy_3.png"),
}

# 小卡牌能量模板（攻击牌专用）
SMALL_ENERGY_MAP: Dict[str, Tuple[str, str]] = {
    "energy_0_small": ("0费", "energy_0_small.png"),
    "energy_1_small": ("1费", "energy_1_small.png"),
    "energy_2_small": ("2费", "energy_2_small.png"),
    "energy_3_small": ("3费", "energy_3_small.png"),
}

# 注意：需要准备两套模板文件：
# - 大能量：energy_0.png, energy_1.png, energy_2.png, energy_3.png
# - 小能量：energy_0_small.png, energy_1_small.png, energy_2_small.png, energy_3_small.png

# ========== 战斗画面固定 ROI（1920×1080） ==========
ROI_MAP = {
    "player_hp": {"left": 424, "top": 6, "width": 57, "height": 70},
    "player_hp_max": { "left": 642,"top": 1165,"width": 40,"height": 43},
    "player_energy": {"left": 182, "top": 1314, "width": 63, "height": 62},
    "player_energy_max": {"left": 271, "top": 1307, "width": 59, "height": 71},
    "player_block": {"left": 324, "top": 870, "width": 50, "height": 50},
    "gold": {"left": 620,"top": 10,"width": 90,"height": 63},
    "big_card_energy": {"left": 968, "top": 378, "width": 205, "height": 255},  # 非攻击牌能量区域
    "small_card_energy": {"left": 1096,"top": 1131,"width": 119,"height": 135}, # 攻击牌能量区域
}

# 注意：如果攻击牌的能量数字位置与大卡牌不同，需要单独调整 small_card_energy 的坐标

# ---------- 动态识别区域 ----------
Card_AREA = {"left": 736,"top": 302,"width": 965,"height": 940}
ENEMY_AREA = {"left": 1298, "top": 525, "width": 1265, "height": 708}