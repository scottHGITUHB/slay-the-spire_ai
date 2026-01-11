# (1280, 800)
import pyautogui
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

from tools.img_tool import screen_shot, load_tpl, match_once, crop
from tools.config import Card_AREA, CARD_KIND_MAP, BIG_ENERGY_MAP, SMALL_ENERGY_MAP, MATCH_THRESHOLD, DATA_CARD, ROI_MAP


def click_center_of_screen():
    """点击屏幕中央，用于激活游戏窗口"""
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    pyautogui.click(center_x, center_y)
    print(f"点击屏幕中间: ({center_x}, {center_y})")


def recognize_energy_by_template(card_type: str) -> Optional[int]:
    """
    使用模板匹配识别卡牌能量消耗
    根据卡牌类型自动选择大/小能量模板和ROI区域

    参数:
        card_type: 卡牌类型 ("attack", "defend", "skill", "power", "curse")
    返回: 能量值(int)或None
    """
    # 根据卡牌类型选择不同的ROI和模板
    if card_type == "attack":
        # 攻击牌使用小能量ROI和小能量模板
        roi_key = "small_card_energy"
        energy_map = SMALL_ENERGY_MAP
        print("  [能量识别] 使用小能量模板（攻击牌）")
    else:
        # 其他牌使用大能量ROI和大能量模板
        roi_key = "big_card_energy"
        energy_map = BIG_ENERGY_MAP
        print("  [能量识别] 使用大能量模板（非攻击牌）")

    # 截取能量区域灰度图
    energy_img = screen_shot(color=False)
    roi = (ROI_MAP[roi_key]["left"], ROI_MAP[roi_key]["top"],
           ROI_MAP[roi_key]["width"], ROI_MAP[roi_key]["height"])
    energy_roi_img = crop(energy_img, roi)

    # 尝试匹配对应能量模板
    for key, (energy_desc, file_name) in energy_map.items():
        tpl_path = DATA_CARD / file_name
        if not tpl_path.exists():
            print(f"  [能量识别] 模板不存在: {tpl_path}")
            continue

        tpl = load_tpl(tpl_path)
        if match_once(energy_roi_img, tpl, MATCH_THRESHOLD):
            print(f"  [能量识别] 匹配成功: {energy_desc}")
            # 从key中提取能量值（如 "energy_2" -> 2, "energy_1_small" -> 1）
            try:
                energy_cost = int(key.split('_')[1])
                return energy_cost
            except (IndexError, ValueError):
                print(f"  [能量识别] 无法解析能量值: {key}")
                return None

    print("  [能量识别] 未匹配到任何能量模板")
    return None


def recognize_card_and_energy(current_hotkey: int) -> Tuple[bool, Optional[str], Optional[int], str]:
    """
    在 Card_AREA 区域内识别手牌类型和能量消耗
    返回: (是否识别成功, 卡牌中文名, 能量值, 卡牌类型)
    """
    # 截取手牌区域灰度图
    card_img = screen_shot(color=False)
    roi = (Card_AREA["left"], Card_AREA["top"],
           Card_AREA["width"], Card_AREA["height"])
    card_roi_img = crop(card_img, roi)

    # 尝试匹配每种手牌模板
    for key, (card_cn, file_name) in CARD_KIND_MAP.items():
        tpl_path = DATA_CARD / file_name
        if not tpl_path.exists():
            print(f"[卡牌类型识别] 模板不存在: {tpl_path}")
            continue

        tpl = load_tpl(tpl_path)
        if match_once(card_roi_img, tpl, MATCH_THRESHOLD):
            # 识别成功，记录卡牌类型和名称
            card_type = key
            card_name = card_cn

            print(f"[卡牌类型识别] 识别为: {card_name} (类型: {card_type})")

            # 根据卡牌类型识别能量消耗（智能切换大小能量模板）
            energy_cost = recognize_energy_by_template(card_type)

            return True, card_name, energy_cost, card_type

    # 没有匹配到任何卡牌模板
    print("[卡牌类型识别] 未识别到任何卡牌")
    return False, None, None, ""


def print_summary(results: Dict[int, Tuple[str, Optional[int], str]]):
    """打印识别结果汇总（包含能量值和卡牌类型）"""
    print("\n" + "=" * 50)
    print(f"识别完成！共 {len(results)} 张牌")
    print("识别结果:")
    for hotkey, (card_name, energy, card_type) in results.items():
        energy_str = f"{energy}费" if energy is not None else "能量未知"
        print(f"  热键{hotkey}: {card_name} ({card_type}) - {energy_str}")
    print("=" * 50)


def press_hotkeys_with_recognition():
    """
    循环按下热键，每次按键后识别手牌区域一次
    识别成功则立即再次按下该热键执行游戏操作
    识别失败则退出循环
    """
    time.sleep(1)  # 初始等待

    hotkey_index = 1
    recognition_results: Dict[int, Tuple[str, Optional[int], str]] = {}  # 收集识别结果 (卡牌名, 能量, 类型)

    while True:
        # 第一步：按下热键选中卡牌进行识别
        pyautogui.press(str(hotkey_index))
        print(f"\n{'=' * 40}")
        print(f"按下热键: {hotkey_index}（用于选中卡牌识别）")
        print(f"{'=' * 40}")

        # 等待游戏响应
        time.sleep(0.5)

        # 识别并获取结果（包含能量值和卡牌类型）
        success, card_name, energy_cost, card_type = recognize_card_and_energy(hotkey_index)

        if success:
            # 记录识别结果
            recognition_results[hotkey_index] = (card_name, energy_cost, card_type)

            energy_str = f"{energy_cost}费" if energy_cost is not None else "能量未知"
            print(f"✅ 识别成功: {card_name} ({card_type}), {energy_str}")

            # 第二步：再次按下该热键，执行游戏操作
            print(f"⏳ 再次按下热键: {hotkey_index}（执行游戏操作）")
            pyautogui.press(str(hotkey_index))
            time.sleep(0.3)  # 等待游戏响应

            print(f"✅ 热键 {hotkey_index} 操作完成")
        else:
            print("\n❌ 识别失败，退出循环")
            break

        # 准备下一个热键
        hotkey_index += 1
        if hotkey_index > 9:
            hotkey_index = 1

    # 所有卡牌识别完成后，打印汇总
    print_summary(recognition_results)


def test_script():
    """测试脚本入口"""
    click_center_of_screen()
    time.sleep(0.5)  # 等待点击生效
    press_hotkeys_with_recognition()


if __name__ == "__main__":
    test_script()