import tkinter as tk

from trainer_handlers import TrainerHandlersMixin
from trainer_ime import TrainerIMEMixin
from trainer_ui import TrainerUIMixin


class TrainerApp(TrainerUIMixin, TrainerHandlersMixin, TrainerIMEMixin):
    def __init__(self, root):
        self.root = root
        self.root.title("Hanguk Trainer (초급)")
        self.root.geometry("1180x760")
        self.root.minsize(1080, 700)

        self.vocab_path = None
        self.vocab = []
        self.prog = {}
        self.prog_path = None
        self.ko_to_ja = {}
        self.ja_to_ko = {}
        self.grammar = []
        self.grammar_path = None

        self.mode = tk.StringVar(value="MC_JA_TO_KO")
        self.range_option_var = tk.StringVar(value="全範囲")
        self.range_start_var = tk.StringVar(value="")
        self.range_end_var = tk.StringVar(value="")
        self.range_options = ["全範囲"]
        self.active_vocab = []
        self.tts_speed_var = tk.DoubleVar(value=0.75)
        self.tts_speed_label_var = tk.StringVar(value="音声: 0.75x")
        self.current = None
        self.choices = []
        self.selected_index = None
        self.answered = False
        self.revealed = False
        self.seen_marked = False
        self.last_feedback = tk.StringVar(value="")

        self.ime_buffer = ""
        self.ime_l = None
        self.ime_v = None
        self.ime_t = None

        self._build_ui()
        self._load_on_start()
