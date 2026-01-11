"""
敌人意图识别 —— 彩色模板匹配版（完整跑 N 次，取最佳）
针对 debuff.png 增加旋转模板匹配
"""
import cv2
from collections import Counter
import numpy as np
from pathlib import Path
from typing import List, Tuple
from tools.img_tool import screen_shot
from tools.config import DATA_ENEMY, INTENT_MAP, ENEMY_AREA

BEST_OF_N = 3
ROT_TPL_NAMES = {"debuff", "debuff2"}

# ================= 旋转模板缓存 =================
# 只给 debuff.png 预生成多角度模板
_ROT_TPLS: dict[str, List[Tuple[np.ndarray, float]]] = {}   # angle -> (tpl, angle)

def _load_rot_templates(tpl_path: Path, step: int = 15) -> List[Tuple[np.ndarray, float]]:
    """返回 [(旋转模板, 角度), ...] 列表，0°–360°"""
    if tpl_path.stem in _ROT_TPLS:
        return _ROT_TPLS[tpl_path.stem]
    base = cv2.imread(str(tpl_path), cv2.IMREAD_COLOR)
    h, w = base.shape[:2]
    center = (w // 2, h // 2)
    rot_tuples = []
    for angle in range(0, 360, step):
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        # 计算新画布大小，防止裁切
        cos, sin = np.abs(M[0, 0]), np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        rot = cv2.warpAffine(base, M, (new_w, new_h), borderValue=(0, 0, 0))
        rot_tuples.append((rot, angle))
    _ROT_TPLS[tpl_path.stem] = rot_tuples
    return rot_tuples

# ================= 单次匹配（含旋转逻辑） =================
def match_color_once(img: np.ndarray, tpl: np.ndarray, threshold: float = 0.8,
                     tpl_name: str = "") -> Tuple[bool, Tuple[int, int]]:
    """
    对 debuff.png / debuff2.png 启用多角度匹配，其余模板原样匹配
    """
    if tpl_name in ROT_TPL_NAMES:              # <-- 只改这里
        rot_tuples = _load_rot_templates(DATA_ENEMY / f"{tpl_name}.png")
        best_val, best_loc = 0, None
        for rot_tpl, _angle in rot_tuples:
            res = cv2.matchTemplate(img, rot_tpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val, best_loc = max_val, max_loc
        if best_val >= threshold:
            return True, best_loc
    else:
        # 原版匹配
        res = cv2.matchTemplate(img, tpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:
            return True, max_loc
    return False, None

# ================= 单次完整识别 =================
def _single_count() -> Tuple[int, List[str]]:
    enemy_bgr = shot_enemy_color()
    total = 0
    intents = []

    for key, (intent_cn, file_name) in INTENT_MAP.items():
        tpl_path = DATA_ENEMY / file_name
        if not tpl_path.exists():
            continue
        tpl = load_tpl_color(tpl_path)
        tpl_name = tpl_path.stem                 # 用于区分 debuff

        while True:
            hit, top_left = match_color_once(enemy_bgr, tpl, threshold=0.80, tpl_name=tpl_name)
            if not hit:
                break
            total += 1
            intents.append(intent_cn)
            # 涂黑：用原模板尺寸即可（旋转模板已内部处理）
            h_t, w_t = tpl.shape[:2]
            x, y = top_left
            enemy_bgr[y:y+h_t, x:x+w_t] = 0

    return total, intents

# ================= N 次取最佳（带打印） =================
def count_enemies_and_intent(n: int = BEST_OF_N) -> Tuple[int, List[str]]:
    rounds = []
    for i in range(1, n + 1):
        t, its = _single_count()
        print(f"[Round {i}/{n}] 敌人数量：{t}，意图列表：{its}")
        rounds.append(its)

    long_list = [it for r in rounds for it in r]

    # 第一轮为空 → 直接按长列表第一次出现顺序保留一份
    if not rounds[0]:
        final_list = []
        seen = set()
        for it in long_list:
            if it not in seen:
                final_list.append(it)
                seen.add(it)
    else:
        # 原逻辑：不超过第一轮出现次数
        first_cnt = Counter(rounds[0])
        seen_cnt = Counter()
        final_list = []
        for it in long_list:
            if seen_cnt[it] < first_cnt[it]:
                final_list.append(it)
                seen_cnt[it] += 1

    # 兜底
    if not final_list:
        return 1, ['未知意图，敌人可能选择防守']

    return len(final_list), final_list
# ================= 工具函数 =================
def load_tpl_color(tpl_path: Path) -> np.ndarray:
    return cv2.imread(str(tpl_path), cv2.IMREAD_COLOR)

def shot_enemy_color() -> np.ndarray:
    full_bgr = screen_shot(color=True)
    roi = ENEMY_AREA
    x0, y0, w, h = roi["left"], roi["top"], roi["width"], roi["height"]
    return full_bgr[y0:y0+h, x0:x0+w]

# ---------- 自测 ----------
if __name__ == "__main__":
    import time, pprint
    time.sleep(1)
    n, its = count_enemies_and_intent()
    print(f"敌人数量：{n}")
    pprint.pprint(its)