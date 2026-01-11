#
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Union, Tuple
from tools.img_tool import screen_shot, dict2tuple, crop, load_tpl
from tools.config import (
    DATA_ENEMY, DATA_CARD, INTENT_MAP,
    ROI_MAP, Card_AREA, ENEMY_AREA
)
# 新增：引入 match_enemy 的接口
from match_enemy import count_enemies_and_intent as match_enemy_count

# --------------- EasyOCR 初始化 ---------------
import easyocr
from typing import Optional
_READER: Optional[easyocr.Reader] = None

def _get_reader() -> easyocr.Reader:
    global _READER
    if _READER is None:
        _READER = easyocr.Reader(["ch_sim", "en"], gpu=False)
    return _READER

def _try_int(txt: str, default: int = 0) -> int:
    digits = "".join(c for c in txt if c.isdigit())
    return int(digits) if digits else default

# --------------- 固定 ROI 读取 ---------------
def _fix_roi_read(name: str) -> int:
    roi = dict2tuple(ROI_MAP.get(name))
    if roi is None:
        return 0
    patch = crop(screen_shot(), roi)
    texts = _get_reader().readtext(patch, detail=0)
    return _try_int("".join(texts))

# --------------- 灰度 + 空模板保护 ---------------
def _safe_tpl(path: Path) -> np.ndarray:
    return load_tpl(path) if path.exists() else np.array([])

# --------------- 对外唯一接口 ---------------
def battle_state() -> Dict[str, Union[int, List[str]]]:
    result = {}
    for key in ("player_hp", "player_hp_max",
                "player_energy", "player_energy_max",
                "player_block", "gold"):
        result[key] = _fix_roi_read(key)

    # 直接调用 match_enemy 提供的接口
    enemy_total, enemy_intents = match_enemy_count()
    result["enemy_count"] = enemy_total
    result["enemy_intents"] = enemy_intents
    return result

if __name__ == "__main__":
    import time, pprint
    time.sleep(1)
    pprint.pprint(battle_state())