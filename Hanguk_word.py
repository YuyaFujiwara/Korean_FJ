import tkinter as tk
from tkinter import ttk

from trainer_app import TrainerApp


def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass
    app = TrainerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
