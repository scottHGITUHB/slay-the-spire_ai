# img_tool.py
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

def load_tpl(path: Path, color: bool = False) -> np.ndarray:
    """
    加载模板
    color=False -> 灰度 (cv2.IMREAD_GRAYSCALE)
    color=True  -> 彩色 (cv2.IMREAD_COLOR)
    """
    flag = cv2.IMREAD_COLOR if color else cv2.IMREAD_GRAYSCALE
    return cv2.imread(str(path), flag)

def screen_shot(color: bool = False) -> np.ndarray:
    """
    全屏截图
    color=False -> 返回单通道灰度
    color=True  -> 返回三通道 BGR（OpenCV 默认顺序）
    """
    from PIL import ImageGrab
    img_rgb = ImageGrab.grab()          # RGB 顺序
    img_np = np.array(img_rgb, dtype=np.uint8)
    if color:
        return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

def dict2tuple(roi: Optional[Dict[str, int]]) -> Optional[Tuple[int, int, int, int]]:
    if roi is None:
        return None
    return (roi["left"], roi["top"], roi["width"], roi["height"])

def crop(img: np.ndarray, roi: Optional[Tuple[int, int, int, int]]) -> np.ndarray:
    if roi is None:
        return img
    x, y, w, h = roi
    return img[y:y+h, x:x+w]

def match_once(hay: np.ndarray, needle: np.ndarray, threshold: float = 0.8) -> bool:
    """单模板匹配，返回是否命中（hay/needle 同通道即可）"""
    res = cv2.matchTemplate(hay, needle, cv2.TM_CCOEFF_NORMED)
    return cv2.minMaxLoc(res)[1] >= threshold