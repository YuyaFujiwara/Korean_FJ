import tkinter as tk
from tkinter import ttk
from typing import Any

from hangul_utils import L_JAMO, V_JAMO


class TrainerUIMixin:
    root: Any
    mode: Any
    mode_combo: Any
    mode_map: dict[str, str]
    last_feedback: Any

    pick_file: Any
    on_mode_changed: Any
    next_item: Any
    show_answer: Any
    show_choices: Any
    play_audio: Any
    select_choice: Any
    confirm_choice: Any
    check_typed: Any
    open_osk: Any
    ime_input_consonant: Any
    ime_input_vowel: Any
    ime_input_space: Any
    ime_backspace: Any
    ime_commit: Any
    ime_clear: Any


    def _build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="単語ファイルを選ぶ", command=self.pick_file).pack(side="left")
        self.file_label = ttk.Label(top, text="(syokyuu_hanguk.txt を選択)")
        self.file_label.pack(side="left", padx=10)

        mid = ttk.Frame(self.root, padding=10)
        mid.pack(fill="x")

        ttk.Label(mid, text="モード:").pack(side="left")
        modes = [
            ("4択：日→韓（入力不要）", "MC_JA_TO_KO"),
            ("4択：韓→日（入力不要）", "MC_KO_TO_JA"),
            ("4択：文法→意味（初級85）", "MC_GRAMMAR_TO_JA"),
            ("ローマ字/ハングル入力：日→韓（IME不要）", "TYPE_ROMA_JA_TO_KO"),
            ("フラッシュ：韓⇄日（見るだけ）", "FLASH"),
        ]
        self.mode_combo = ttk.Combobox(mid, state="readonly", values=[m[0] for m in modes], width=32)
        self.mode_map = {m[0]: m[1] for m in modes}
        self.mode_combo.current(0)
        self.mode_combo.bind("<<ComboboxSelected>>", self.on_mode_changed)
        self.mode_combo.pack(side="left", padx=8)

        ttk.Button(mid, text="次へ", command=self.next_item).pack(side="left", padx=8)
        self.show_answer_button = ttk.Button(mid, text="答え表示", command=self.show_answer)
        self.show_answer_button.pack(side="left")
        self.show_choices_button = ttk.Button(mid, text="選択肢表示", command=self.show_choices)
        self.show_choices_button.pack(side="left", padx=8)
        ttk.Button(mid, text="音声再生", command=self.play_audio).pack(side="left", padx=8)

        self.prompt_frame = ttk.Frame(self.root, padding=10)
        self.prompt_frame.pack(fill="both", expand=True)

        self.prompt_label = ttk.Label(self.prompt_frame, text="", font=("Segoe UI", 20), wraplength=740, justify="center")
        self.prompt_label.pack(pady=15)

        self.flash_answer_frame = ttk.Frame(self.prompt_frame)
        self.flash_answer_button = ttk.Button(self.flash_answer_frame, text="答え表示", command=self.show_answer)
        self.flash_answer_button.pack()
        self.flash_answer_var = tk.StringVar(value="")
        self.flash_answer_label = ttk.Label(self.flash_answer_frame, textvariable=self.flash_answer_var, font=("Segoe UI", 14))
        self.flash_answer_label.pack(pady=8)

        self.choice_frame = ttk.Frame(self.prompt_frame)
        self.choice_frame.pack(pady=10)

        self.choice_buttons = []
        for i in range(4):
            b = ttk.Button(self.choice_frame, text=f"選択肢{i+1}", command=lambda idx=i: self.select_choice(idx), width=40)
            b.grid(row=i // 2, column=i % 2, padx=8, pady=8)
            self.choice_buttons.append(b)

        self.confirm_button = ttk.Button(self.choice_frame, text="決定", command=self.confirm_choice, width=20)
        self.confirm_button.grid(row=2, column=0, columnspan=2, pady=6)

        self.choice_info_var = tk.StringVar(value="")
        self.choice_info_label = ttk.Label(self.choice_frame, textvariable=self.choice_info_var, justify="left")
        self.choice_info_label.grid(row=3, column=0, columnspan=2, pady=6)

        self.input_frame = ttk.Frame(self.prompt_frame)
        self.input_entry = ttk.Entry(self.input_frame, width=40, font=("Segoe UI", 14))
        self.input_entry.pack(side="left", padx=8)
        self.check_button = ttk.Button(self.input_frame, text="判定", command=self.check_typed)
        self.check_button.pack(side="left")
        ttk.Button(self.input_frame, text="スクリーンキーボード", command=self.open_osk).pack(side="left", padx=8)
        ttk.Label(self.input_frame, text="（例: masyeoyo / bwassoyo など）").pack(side="left", padx=8)

        self.hangul_frame = ttk.Frame(self.prompt_frame)
        ttk.Label(self.hangul_frame, text="ハングル入力パッド").pack(anchor="w")

        consonant_frame = ttk.Frame(self.hangul_frame)
        consonant_frame.pack(fill="x", pady=4)
        for i, jamo in enumerate(L_JAMO):
            b = ttk.Button(consonant_frame, text=jamo, width=3, command=lambda c=jamo: self.ime_input_consonant(c))
            b.grid(row=i // 10, column=i % 10, padx=2, pady=2)

        vowel_frame = ttk.Frame(self.hangul_frame)
        vowel_frame.pack(fill="x", pady=4)
        for i, jamo in enumerate(V_JAMO):
            b = ttk.Button(vowel_frame, text=jamo, width=3, command=lambda v=jamo: self.ime_input_vowel(v))
            b.grid(row=i // 10, column=i % 10, padx=2, pady=2)

        control_frame = ttk.Frame(self.hangul_frame)
        control_frame.pack(fill="x", pady=4)
        ttk.Button(control_frame, text="Space", command=self.ime_input_space).pack(side="left", padx=4)
        ttk.Button(control_frame, text="<-", command=self.ime_backspace).pack(side="left", padx=4)
        ttk.Button(control_frame, text="確定", command=self.ime_commit).pack(side="left", padx=4)
        ttk.Button(control_frame, text="クリア", command=self.ime_clear).pack(side="left", padx=4)

        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill="x")

        self.feedback_label = ttk.Label(bottom, textvariable=self.last_feedback, font=("Segoe UI", 12))
        self.feedback_label.pack(side="left")

        self.stats_label = ttk.Label(bottom, text="")
        self.stats_label.pack(side="right")

        self._render_mode_ui()

    def _render_mode_ui(self):
        m = self.mode.get()
        if m.startswith("MC_"):
            self.show_answer_button.pack_forget()
            self.show_choices_button.pack_forget()
            self.flash_answer_frame.pack_forget()
            self.choice_frame.pack(pady=10)
            self.input_frame.pack_forget()
            self.hangul_frame.pack_forget()
        elif m.startswith("TYPE_"):
            self.show_answer_button.pack(side="left")
            self.show_choices_button.pack(side="left", padx=8)
            self.flash_answer_frame.pack_forget()
            self.choice_frame.pack_forget()
            self.input_frame.pack(pady=10)
            self.hangul_frame.pack(pady=6)
        elif m == "FLASH":
            self.show_answer_button.pack_forget()
            self.show_choices_button.pack_forget()
            self.flash_answer_frame.pack(pady=6)
            self.choice_frame.pack_forget()
            self.input_frame.pack_forget()
            self.hangul_frame.pack_forget()