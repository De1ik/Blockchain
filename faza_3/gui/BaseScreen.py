import tkinter as tk

class BaseScreen:
    def __init__(self, parent, name, bg_color):
        self.name = name
        self.frame = tk.Frame(parent, bg=bg_color)
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    def forget(self):
        self.frame.pack_forget()
    def update(self):
        pass

