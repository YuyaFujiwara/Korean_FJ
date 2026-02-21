import os
import random
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any

from hangul_utils import hangul_to_rr, norm_answer
from tts_player import speak_korean
from vocab_progress import (
    load_progress,
    load_vocab,
    progress_path_for,
    save_progress,
    weighted_choice,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOCAB_DIR = os.path.join(PROJECT_ROOT, "data", "vocab")
GRAMMAR_PATH = os.path.join(PROJECT_ROOT, "data", "grammar", "grammar-85.tsv")


class TrainerHandlersMixin:
    file_label: Any
    last_feedback: Any
    stats_label: Any
    choice_info_var: Any
    flash_answer_var: Any
    mode: Any
    mode_combo: Any
    mode_map: dict[str, str]
    prompt_label: Any
    confirm_button: Any
    input_entry: Any
    check_button: Any
    choice_buttons: list[Any]
    _render_mode_ui: Any
    ime_clear: Any
    _ime_sync_if_needed: Any
    ime_commit: Any
    tts_speed_var: Any
    tts_speed_label_var: Any

    def _tts_rate_str(self) -> str:
        ratio = float(self.tts_speed_var.get())
        percent = int(round((ratio - 1.0) * 100))
        return f"{percent:+d}%"

    def on_tts_speed_changed(self, value: str):
        try:
            ratio = float(value)
        except Exception:
            ratio = float(self.tts_speed_var.get())
        self.tts_speed_label_var.set(f"音声: {ratio:.2f}x")

    def _speak(self, text: str):
        if not text:
            return
        speak_korean(text, rate=self._tts_rate_str())

    def _load_grammar(self):
        self.grammar = []
        self.grammar_path = GRAMMAR_PATH
        if not os.path.exists(GRAMMAR_PATH):
            return
        try:
            with open(GRAMMAR_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    ko = (row.get("한글") or "").strip()
                    ja = (row.get("日本語") or "").strip()
                    connect = (row.get("接続ルール") or "").strip()
                    ex_ko = (row.get("예문") or "").strip()
                    ex_ja = (row.get("例文") or "").strip()
                    if not ko or not ja:
                        continue
                    self.grammar.append({"ko": ko, "ja": ja, "connect": connect, "ex_ko": ex_ko, "ex_ja": ex_ja})
        except Exception:
            self.grammar = []

    def _load_on_start(self):
        self._load_grammar()

        default_candidates = [
            os.path.join(VOCAB_DIR, "syokyuu_hanguk.tsv"),
            os.path.join(VOCAB_DIR, "syokyuu_hanguk.txt"),
        ]
        default = next((p for p in default_candidates if os.path.exists(p)), None)

        if default:
            self.load_file(default)
            self.next_item()
        elif self.grammar:
            self.last_feedback.set("語彙ファイル未読込。文法モードは利用できます。")
        else:
            self.last_feedback.set("ファイルを選んで開始。TSV: 番号<TAB>韓国語<TAB>日本語")

    def pick_file(self):
        path = filedialog.askopenfilename(
            title="syokyuu_hanguk.tsv を選択",
            initialdir=VOCAB_DIR,
            filetypes=[("TSV files", "*.tsv"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self.load_file(path)
            self.next_item()

    def load_file(self, path):
        try:
            vocab = load_vocab(path)
        except Exception as e:
            messagebox.showerror("読み込み失敗", str(e))
            return
        self.vocab_path = path
        self.vocab = vocab
        self.ko_to_ja = {v["ko"]: v["ja"] for v in vocab}
        self.ja_to_ko = {}
        for v in vocab:
            self.ja_to_ko.setdefault(v["ja"], []).append(v["ko"])
        self.prog_path = progress_path_for(path)
        self.prog = load_progress(self.prog_path, self.vocab)
        self.file_label.config(text=os.path.basename(path))
        self.last_feedback.set(f"読み込みOK: {len(self.vocab)}語 / 進捗: {self.prog_path}")
        self.update_stats()

    def on_mode_changed(self, _evt=None):
        label = self.mode_combo.get()
        self.mode.set(self.mode_map[label])
        self._render_mode_ui()
        if self.vocab or self.grammar:
            self.next_item()

    def next_item(self):
        m = self.mode.get()
        if m == "MC_GRAMMAR_TO_JA":
            if not self.grammar:
                self.last_feedback.set("文法データが見つかりません。data/grammar/grammar-85.tsv を確認してください。")
                return
            self.current = random.choice(self.grammar)
        else:
            if not self.vocab:
                self.last_feedback.set("まず単語ファイルを読み込んで。")
                return
            self.current = weighted_choice(self.vocab, self.prog)

        self.choices = []
        self.selected_index = None
        self.answered = False
        self.revealed = False
        self.seen_marked = False
        self.last_feedback.set("")
        self.choice_info_var.set("")
        self.flash_answer_var.set("")

        if m == "MC_JA_TO_KO":
            self.prompt_label.config(text=f"日本語 → 韓国語\n\n{self.current['ja']}")
            self.choices = self._make_choices(correct=self.current["ko"], field="ko")
            self._set_choice_buttons(self.choices)
            self.confirm_button.config(state="normal")
        elif m == "MC_KO_TO_JA":
            self.prompt_label.config(text=f"韓国語 → 日本語\n\n{self.current['ko']}")
            self.choices = self._make_choices(correct=self.current["ja"], field="ja")
            self._set_choice_buttons(self.choices)
            self.confirm_button.config(state="normal")
        elif m == "MC_GRAMMAR_TO_JA":
            example = self.current.get("ex_ko", "")
            ex_line = f"\n例文: {example}" if example else ""
            self.prompt_label.config(text=f"文法 → 日本語\n\n{self.current['ko']}{ex_line}\n\n（意味を選んでください）")
            self.choices = self._make_choices(correct=self.current["ja"], field="ja", source=self.grammar)
            self._set_choice_buttons(self.choices)
            self.confirm_button.config(state="normal")
        elif m == "TYPE_ROMA_JA_TO_KO":
            self.prompt_label.config(text=f"日本語 → 韓国語（ローマ字 or ハングルパッド）\n\n{self.current['ja']}")
            self.input_entry.delete(0, tk.END)
            self.input_entry.focus_set()
            self.input_entry.config(state="normal")
            self.check_button.config(state="normal")
            self.ime_clear()
        elif m == "FLASH":
            self.prompt_label.config(text=f"{self.current['ko']}")
        else:
            self.prompt_label.config(text="モード不明")

    def _make_choices(self, correct: str, field: str, source=None):
        source_data = source if source is not None else self.vocab
        pool = [v[field] for v in source_data if v[field] != correct]
        wrongs = []
        if pool:
            wrongs = random.sample(pool, k=min(3, len(pool)))
        opts = wrongs + [correct]
        random.shuffle(opts)
        return opts

    def _set_choice_buttons(self, opts):
        for i, b in enumerate(self.choice_buttons):
            if i < len(opts):
                b.config(text=opts[i], state="normal")
            else:
                b.config(text="", state="disabled")
        self._render_selected()

    def _render_selected(self):
        for i, b in enumerate(self.choice_buttons):
            if i >= len(self.choices):
                continue
            prefix = "▶ " if self.selected_index == i else ""
            b.config(text=f"{prefix}{self.choices[i]}")

    def select_choice(self, idx: int):
        if not self.current or not self.choices:
            return
        m = self.mode.get()
        if self.answered:
            if m == "MC_JA_TO_KO" and idx < len(self.choices):
                self._speak(self.choices[idx])
            elif m == "MC_KO_TO_JA":
                self._speak(self.current["ko"])
            return

        self.selected_index = idx
        self._render_selected()

        if m == "MC_JA_TO_KO":
            self._speak(self.choices[idx])
        elif m == "MC_KO_TO_JA":
            self._speak(self.current["ko"])
        elif m == "MC_GRAMMAR_TO_JA":
            self._speak(self.current["ko"])

    def confirm_choice(self):
        if self.selected_index is None or self.answered or not self.current:
            return
        m = self.mode.get()
        selected = self.choices[self.selected_index]

        if m == "MC_JA_TO_KO":
            correct = self.current["ko"]
            is_ok = selected == correct
            self._record_result(is_ok)
            self.last_feedback.set(self._feedback_text(is_ok, correct_display=correct))
            self._render_choice_result(correct)
        elif m == "MC_KO_TO_JA":
            correct = self.current["ja"]
            is_ok = selected == correct
            self._record_result(is_ok)
            self.last_feedback.set(self._feedback_text(is_ok, correct_display=correct))
            self._render_choice_result(correct)
        elif m == "MC_GRAMMAR_TO_JA":
            correct = self.current["ja"]
            is_ok = selected == correct
            self._record_result(is_ok)
            ex_ja = (self.current.get("ex_ja") or "").strip()
            base = self._feedback_text(is_ok, correct_display=correct)
            if ex_ja:
                base += f"\n例文(日): {ex_ja}"
            self.last_feedback.set(base)
            self._render_choice_result(correct)

    def check_typed(self):
        if not self.current or self.answered:
            return
        self._ime_sync_if_needed()
        self.ime_commit()
        user = self.input_entry.get().strip()
        if not user:
            return

        correct_ko = self.current["ko"]
        correct_rr = hangul_to_rr(correct_ko)

        is_ok = (user == correct_ko) or (norm_answer(user) == norm_answer(correct_rr))

        self._record_result(is_ok)
        self.last_feedback.set(self._feedback_text(is_ok, correct_display=f"{correct_ko}   (RR: {correct_rr})"))
        self._lock_answer_ui()

    def _mark_seen(self):
        if self.seen_marked or not self.current:
            return
        self.prog[self.current["ko"]]["seen"] += 1
        self.seen_marked = True
        if self.prog_path:
            save_progress(self.prog_path, self.prog)
        self.update_stats()

    def _record_result(self, is_ok: bool):
        if self.answered:
            return
        if self.mode.get() == "MC_GRAMMAR_TO_JA":
            self.answered = True
            self._lock_answer_ui()
            return
        self._mark_seen()

        if self.revealed and is_ok:
            is_ok = False

        if self.current is not None:
            p = self.prog[self.current["ko"]]
            if is_ok:
                p["correct"] += 1
            else:
                p["wrong"] += 1
            if self.prog_path:
                save_progress(self.prog_path, self.prog)
            self.update_stats()
        self.answered = True
        self._lock_answer_ui()

    def _lock_answer_ui(self):
        self.confirm_button.config(state="disabled")
        if not self.mode.get().startswith("MC_"):
            for b in self.choice_buttons:
                b.config(state="disabled")
        self.input_entry.config(state="disabled")
        self.check_button.config(state="disabled")

    def _feedback_text(self, is_ok: bool, correct_display: str):
        if self.revealed:
            return f"⚠ 答え表示済み  →  {correct_display}"
        if is_ok:
            return f"✅ 正解   →  {correct_display}"
        return f"❌ 不正解 →  正解: {correct_display}"

    def show_answer(self):
        if not self.current:
            return
        ko = self.current["ko"]
        ja = self.current["ja"]
        rr = hangul_to_rr(ko)
        self.revealed = True
        self._mark_seen()
        mode = self.mode.get()
        if mode == "FLASH":
            self.answered = True
            self.flash_answer_var.set(f"日本語: {ja}")
            return
        if mode in ("MC_JA_TO_KO", "TYPE_ROMA_JA_TO_KO"):
            messagebox.showinfo("答え", f"韓国語: {ko}\nローマ字(RR): {rr}")
        elif mode == "MC_KO_TO_JA":
            messagebox.showinfo("答え", f"日本語: {ja}")
        else:
            messagebox.showinfo("答え", f"韓国語: {ko}\n日本語: {ja}\nローマ字(RR): {rr}")

    def show_choices(self):
        if not self.current or not self.choices:
            return
        lines = self._update_choice_info()
        messagebox.showinfo("選択肢", "\n".join(lines))

    def _update_choice_info(self):
        m = self.mode.get()
        if self.current is not None:
            correct = self.current["ko"] if m == "MC_JA_TO_KO" else self.current["ja"]
        else:
            correct = None
        lines = []
        for i, c in enumerate(self.choices, start=1):
            mark = " (正解)" if c == correct else ""
            if m == "MC_JA_TO_KO":
                meaning = self.ko_to_ja.get(c, "?")
                lines.append(f"{i}. {c} → {meaning}{mark}")
            elif m == "MC_KO_TO_JA":
                kors = self.ja_to_ko.get(c, [])
                meaning = " / ".join(kors) if kors else "?"
                lines.append(f"{i}. {c} → {meaning}{mark}")
            else:
                lines.append(f"{i}. {c}{mark}")
        self.choice_info_var.set("\n".join(lines))
        return lines

    def play_audio(self):
        if not self.current:
            return
        if self.mode.get() == "MC_GRAMMAR_TO_JA":
            self._speak(self.current["ko"])
            return
        self._speak(self.current["ko"])

    def play_example_audio(self):
        if not self.current:
            return
        if self.mode.get() != "MC_GRAMMAR_TO_JA":
            self.play_audio()
            return
        ex_ko = (self.current.get("ex_ko") or "").strip()
        self._speak(ex_ko if ex_ko else self.current["ko"])

    def open_osk(self):
        try:
            os.system("start osk")
        except Exception:
            messagebox.showerror("起動失敗", "スクリーンキーボードを起動できませんでした。")

    def _render_choice_result(self, correct: str):
        for i, b in enumerate(self.choice_buttons):
            if i >= len(self.choices):
                continue
            label = self.choices[i]
            if label == correct:
                b.config(text=f"✔ {label}")
            elif self.selected_index == i:
                b.config(text=f"✖ {label}")
        self._update_choice_info()

    def update_stats(self):
        if not self.vocab:
            self.stats_label.config(text="")
            return
        total_seen = sum(v["seen"] for v in self.prog.values())
        total_correct = sum(v["correct"] for v in self.prog.values())
        total_wrong = sum(v["wrong"] for v in self.prog.values())
        acc = (total_correct / max(1, (total_correct + total_wrong))) * 100.0
        self.stats_label.config(
            text=f"Seen:{total_seen}  Correct:{total_correct}  Wrong:{total_wrong}  Acc:{acc:.1f}%"
        )