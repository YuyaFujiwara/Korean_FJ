import tkinter as tk
from typing import Any

from hangul_utils import (
    L_DOUBLE,
    T_COMBINE,
    T_INDEX,
    T_SPLIT,
    V_COMBINE,
    V_SPLIT,
    compose_hangul,
)

class TrainerIMEMixin:
    input_entry: Any

    def _ime_sync_if_needed(self):
        entry_text = self.input_entry.get()
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
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, self._ime_display_text())

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
        if hasattr(self, "input_entry"):
            self._ime_update_entry()