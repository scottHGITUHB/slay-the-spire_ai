"""
场景识别入口：全屏模板匹配
"""
from pathlib import Path
import sys
import cv2

sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools.config import SCENE_MAP, DATA_SCENE, MATCH_THRESHOLD
from tools.img_tool import screen_shot, load_tpl, match_once

def match_current_scene():
    full_screen = screen_shot()
    for key, (cn_name, file_name) in SCENE_MAP.items():
        tpl_path = DATA_SCENE / file_name
        if not tpl_path.exists():
            print(f"[WARN] 模板缺失：{tpl_path}")
            continue
        tpl = load_tpl(tpl_path)
        if match_once(full_screen, tpl, MATCH_THRESHOLD):
            print(f"[DEBUG] 命中模板：{key} 相似度="
                  f"{cv2.minMaxLoc(cv2.matchTemplate(full_screen, tpl, cv2.TM_CCOEFF_NORMED))[1]:.3f}")
            return cn_name
    return None

if __name__ == "__main__":
    scene = match_current_scene()
    print("当前场景：", scene if scene else "未识别到任何场景")