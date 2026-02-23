import os
import sys
import tkinter as tk
from tkinter import ttk

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from hangul_utils import (
    L_DOUBLE,
    L_JAMO,
    T_COMBINE,
    T_INDEX,
    T_SPLIT,
    V_COMBINE,
    V_JAMO,
    V_SPLIT,
    compose_hangul,
)


class HangulClipboardPad:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Hangul Clipboard Pad")
        self.root.geometry("780x520")

        self.ime_buffer = ""
        self.ime_l = None
        self.ime_v = None
        self.ime_t = None

        self.status_var = tk.StringVar(value="入力して「コピー」を押すとクリップボードへ入ります。")

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="ハングル入力（コピー専用）", font=("Segoe UI", 14)).pack(side="left")

        editor = ttk.Frame(self.root, padding=10)
        editor.pack(fill="x")

        self.text_entry = ttk.Entry(editor, width=72, font=("Segoe UI", 16))
        self.text_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ttk.Button(editor, text="コピー", command=self.copy_text).pack(side="left")
        ttk.Button(editor, text="クリア", command=self.ime_clear).pack(side="left", padx=(8, 0))

        pad = ttk.Frame(self.root, padding=10)
        pad.pack(fill="both", expand=True)

        ttk.Label(pad, text="子音").pack(anchor="w")
        consonant_frame = ttk.Frame(pad)
        consonant_frame.pack(fill="x", pady=(2, 8))
        for i, jamo in enumerate(L_JAMO):
            b = ttk.Button(consonant_frame, text=jamo, width=3, command=lambda c=jamo: self.ime_input_consonant(c))
            b.grid(row=i // 10, column=i % 10, padx=2, pady=2)

        ttk.Label(pad, text="母音").pack(anchor="w")
        vowel_frame = ttk.Frame(pad)
        vowel_frame.pack(fill="x", pady=(2, 8))
        for i, jamo in enumerate(V_JAMO):
            b = ttk.Button(vowel_frame, text=jamo, width=3, command=lambda v=jamo: self.ime_input_vowel(v))
            b.grid(row=i // 10, column=i % 10, padx=2, pady=2)

        controls = ttk.Frame(pad)
        controls.pack(fill="x", pady=(6, 0))
        ttk.Button(controls, text="Space", command=self.ime_input_space).pack(side="left", padx=4)
        ttk.Button(controls, text="<-", command=self.ime_backspace).pack(side="left", padx=4)
        ttk.Button(controls, text="確定", command=self.ime_commit).pack(side="left", padx=4)

        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill="x")
        ttk.Label(bottom, textvariable=self.status_var).pack(side="left")

    def _ime_sync_if_needed(self):
        entry_text = self.text_entry.get()
        if entry_text != self._ime_display_text():
            self.ime_buffer = entry_text
            self.ime_l = None
            self.ime_v = None
            self.ime_t = None

    def _ime_display_text(self):
        s = self.ime_buffer
        if self.ime_l and self.ime_v:
            s += compose_hangul(self.ime_l, self.ime_v, self.ime_t)
        elif self.ime_l:
            s += self.ime_l
        return s

    def _ime_update_entry(self):
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, self._ime_display_text())

    def ime_input_consonant(self, c: str):
        self._ime_sync_if_needed()
        if self.ime_l is None:
            self.ime_l = c
        elif self.ime_v is None:
            combo = L_DOUBLE.get((self.ime_l, c))
            if combo:
                self.ime_l = combo
            else:
                self.ime_buffer += self.ime_l
                self.ime_l = c
        else:
            if self.ime_t is None:
                if c in T_INDEX:
                    self.ime_t = c
                else:
                    self.ime_buffer += compose_hangul(self.ime_l, self.ime_v, None)
                    self.ime_l = c
                    self.ime_v = None
                    self.ime_t = None
            else:
                combo = T_COMBINE.get((self.ime_t, c))
                if combo:
                    self.ime_t = combo
                else:
                    self.ime_buffer += compose_hangul(self.ime_l or "", self.ime_v or "", self.ime_t or "")
                    self.ime_l = c
                    self.ime_v = None
                    self.ime_t = None
        self._ime_update_entry()

    def ime_input_vowel(self, v: str):
        self._ime_sync_if_needed()
        if self.ime_l is None and self.ime_v is None:
            self.ime_l = "ㅇ"
            self.ime_v = v
        elif self.ime_l is not None and self.ime_v is None:
            self.ime_v = v
        elif self.ime_l is not None and self.ime_v is not None and self.ime_t is None:
            combo = V_COMBINE.get((self.ime_v, v))
            if combo:
                self.ime_v = combo
            else:
                self.ime_buffer += compose_hangul(self.ime_l, self.ime_v, None)
                self.ime_l = "ㅇ"
                self.ime_v = v
        elif self.ime_t is not None:
            split = T_SPLIT.get(self.ime_t)
            if split:
                first, second = split
                if self.ime_l is not None and self.ime_v is not None:
                    self.ime_buffer += compose_hangul(self.ime_l, self.ime_v, first)
                self.ime_l = second
            else:
                self.ime_buffer += compose_hangul(self.ime_l or "", self.ime_v or "", self.ime_t or "")
                self.ime_l = self.ime_t
            self.ime_v = v
            self.ime_t = None
        else:
            self.ime_l = "ㅇ"
            self.ime_v = v
        self._ime_update_entry()

    def ime_input_space(self):
        self._ime_sync_if_needed()
        self.ime_commit()
        self.ime_buffer += " "
        self._ime_update_entry()

    def ime_backspace(self):
        self._ime_sync_if_needed()
        if self.ime_t:
            split = T_SPLIT.get(self.ime_t)
            if split:
                self.ime_t = split[0]
            else:
                self.ime_t = None
        elif self.ime_v:
            base = V_SPLIT.get(self.ime_v)
            if base:
                self.ime_v = base
            else:
                self.ime_v = None
        elif self.ime_l:
            self.ime_l = None
        else:
            self.ime_buffer = self.ime_buffer[:-1]
        self._ime_update_entry()

    def ime_commit(self):
        if self.ime_l and self.ime_v:
            self.ime_buffer += compose_hangul(self.ime_l, self.ime_v, self.ime_t)
        elif self.ime_l:
            self.ime_buffer += self.ime_l
        self.ime_l = None
        self.ime_v = None
        self.ime_t = None
        self._ime_update_entry()

    def ime_clear(self):
        self.ime_buffer = ""
        self.ime_l = None
        self.ime_v = None
        self.ime_t = None
        self._ime_update_entry()
        self.status_var.set("クリアしました。")

    def copy_text(self):
        self._ime_sync_if_needed()
        self.ime_commit()
        text = self.text_entry.get().strip()
        if not text:
            self.status_var.set("コピーする文字がありません。")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set(f"コピーしました: {text}")


def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass
    HangulClipboardPad(root)
    root.mainloop()


if __name__ == "__main__":
    main()
