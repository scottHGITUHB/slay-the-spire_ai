#!/usr/bin/env python3
# roi_tool_tk.py  ✅ 修复回车保存、卡死、弹窗问题
import json, os, tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import numpy as np
import mss
from PIL import Image, ImageTk
from typing import Dict, Optional

CONFIG_FILE = "roi_config.json"


class ROITool:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("ROI 框选工具（纯 tkinter 版）")
        self.rois: Dict[str, dict] = self.load_rois()

        ttk.Button(root, text="开始识图", command=self.run_selector).pack(pady=6)
        self.listbox = tk.Listbox(root, height=6)
        self.listbox.pack(fill="both", padx=6, pady=6)
        ttk.Button(root, text="删除选中", command=self.delete_selected).pack(pady=4)
        self.refresh_listbox()

    # ---------------- 数据 ----------------
    def load_rois(self) -> Dict[str, dict]:
        if os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_rois(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.rois, f, ensure_ascii=False, indent=2)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for name, roi in self.rois.items():
            self.listbox.insert(tk.END, f"{name}  {roi}")

    def delete_selected(self):
        if not self.listbox.curselection():
            messagebox.showwarning("提示", "请先选中要删除的条目")
            return
        key = list(self.rois.keys())[self.listbox.curselection()[0]]
        del self.rois[key]
        self.save_rois()
        self.refresh_listbox()

    # ---------------- 框选 ----------------
    def run_selector(self):
        full_img = self.grab_fullscreen()
        roi = self.tk_select_roi(full_img)
        if roi is None:                       # 用户按了 ESC
            messagebox.showinfo("提示", "已取消框选")
            return
        # 命名
        name = simpledialog.askstring("命名", "请输入该区域的名称：")
        if not name or name.strip() == "":
            messagebox.showwarning("提示", "名称不能为空")
            return
        name = name.strip()
        # 保存
        self.rois[name] = roi
        self.save_rois()
        self.refresh_listbox()
        messagebox.showinfo("成功", f"已保存区域：{name}")

    @staticmethod
    def grab_fullscreen() -> Image.Image:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            arr = np.array(sct.grab(monitor))
            return Image.fromarray(arr[:, :, :3])

    def tk_select_roi(self, img: Image.Image) -> Optional[dict]:
        """返回 mss 风格 ROI 字典，失败返回 None"""
        _top = tk.Toplevel(self.root)
        _top.title("拖动鼠标框选区域 - Enter 保存 / ESC 取消")
        _top.configure(cursor="crosshair")
        _top.attributes("-topmost", True)
        _top.focus_set()
        _top.state("zoomed")          # Windows 全屏；Linux/Mac 可改 "-fullscreen"

        tk_img = ImageTk.PhotoImage(img)
        canvas = tk.Canvas(_top, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, anchor="nw", image=tk_img)

        rect_id = None
        rect = {"x1": 0, "y1": 0, "x2": 0, "y2": 0, "drawing": False}

        def start(evt):
            rect["drawing"] = True
            rect["x1"], rect["y1"] = evt.x, evt.y
            rect["x2"], rect["y2"] = evt.x, evt.y

        def move(evt):
            if not rect["drawing"]:
                return
            rect["x2"], rect["y2"] = evt.x, evt.y
            nonlocal rect_id
            if rect_id:
                canvas.delete(rect_id)
            rect_id = canvas.create_rectangle(rect["x1"], rect["y1"], rect["x2"], rect["y2"],
                                              outline="#00ff00", width=2)

        def end(evt):
            rect["drawing"] = False

        canvas.bind("<Button-1>", start)
        canvas.bind("<B1-Motion>", move)
        canvas.bind("<ButtonRelease-1>", end)

        result = None

        def confirm(_evt=None):
            nonlocal result
            if rect["x1"] == rect["x2"] or rect["y1"] == rect["y2"]:
                messagebox.showwarning("警告", "框选区域宽高为 0", parent=_top)
                return
            left, top_coord = min(rect["x1"], rect["x2"]), min(rect["y1"], rect["y2"])
            w, h = abs(rect["x2"] - rect["x1"]), abs(rect["y2"] - rect["y1"])
            result = {"left": left, "top": top_coord, "width": w, "height": h}
            _top.destroy()

        def cancel(_evt=None):
            nonlocal result
            result = None
            _top.destroy()

        _top.bind("<Return>", confirm)
        _top.bind("<Escape>", cancel)

        self.root.wait_window(_top)
        return result


# ---------- 入口 ----------
def main():
    root = tk.Tk()
    ROITool(root)
    root.mainloop()


if __name__ == "__main__":
    main()