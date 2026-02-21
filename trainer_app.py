import tkinter as tk

from trainer_handlers import TrainerHandlersMixin
from trainer_ime import TrainerIMEMixin
from trainer_ui import TrainerUIMixin


class TrainerApp(TrainerUIMixin, TrainerHandlersMixin, TrainerIMEMixin):
    def __init__(self, root):
        self.root = root
        self.root.title("Hanguk Trainer (초급)")
        self.root.geometry("780x520")

        self.vocab_path = None
        self.vocab = []
        self.prog = {}
        self.prog_path = None
        self.ko_to_ja = {}
        self.ja_to_ko = {}

        self.mode = tk.StringVar(value="MC_JA_TO_KO")
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
