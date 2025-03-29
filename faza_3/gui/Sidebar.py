import tkinter as tk



class Sidebar:
    def __init__(self, parent, buttons, command):
        self.frame = tk.Frame(parent, bg="#37474f", width=400)
        self.frame.grid(row=0, column=0, sticky="ns")
        self.buttons = {}
        btn_style = {
            "bg": "#455a64",
            "fg": "#ffffff",
            "activebackground": "#546e7a",
            "activeforeground": "#ffffff",
            "font": ("Helvetica", 12, "bold"),
            "bd": 0,
            "relief": "flat",
            "highlightthickness": 0,
            "padx": 10,
            "pady": 10,
            "anchor": "w"
        }
        for label in buttons:
            btn = tk.Button(self.frame, text=label, command=lambda l=label: command(l), **btn_style)
            btn.pack(fill="x", padx=20, pady=5)
            self.buttons[label] = btn
