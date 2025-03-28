import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random

from ..RSA import RSAHelper
from ..Block import Block
from ..Blockchain import Blockchain
from ..HandleBlocks import HandleBlocks

class Screens:
    def create_tx_pool_screen(self, name, color):
        frame = tk.Frame(self.content_area, bg=color)
        title = tk.Label(frame, text=name, bg=color, font=("Arial", 24))
        title.pack(pady=20)

        canvas = tk.Canvas(frame, bg=color, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for tx in self.transactions:
            tx_frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief="raised")
            tx_frame.pack(fill="x", padx=20, pady=10)

            tk.Label(tx_frame, text=f"Hash: {tx['hash']}", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)
            tk.Label(tx_frame, text=f"From: {tx['from']}", bg="white", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)
            tk.Label(tx_frame, text=f"To: {tx['to']}", bg="white", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)
            tk.Label(tx_frame, text=f"Index: {tx['index']}", bg="white", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)
            tk.Label(tx_frame, text=f"Amount: {tx['amount']}", bg="white", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)

        self.screens[name] = frame

    def create_utxo_pool_screen(self, name, color, block=None):
        frame = tk.Frame(self.content_area, bg=color)
        # ... (rest of the UTXO pool screen code)
        self.screens[name] = frame
        frame.bind("<Map>", lambda e: update_utxo())

    def create_address_screen(self, name, color):
        frame = tk.Frame(self.content_area, bg=color)
        # ... (rest of the address screen code)
        self.screens[name] = frame
        frame.bind("<Map>", lambda e: update_screen())

    def create_tx_screen(self, name, color):
        frame = tk.Frame(self.content_area, bg=color)
        # ... (rest of the tx screen code)
        self.screens[name] = frame

    def create_blockchain_screen(self, name, color):
        frame = tk.Frame(self.content_area, bg=color)
        # ... (rest of the blockchain screen code)
        self.screens[name] = frame
        frame.bind("<Map>", lambda e: update_screen())

    def show_screen(self, name, update=True):
        for screen in self.screens.values():
            screen.pack_forget()

        screen = self.screens.get(name)
        if screen:
            screen.pack(expand=True, fill="both")

        if name == self.NAME_CREATE_TX:
            self.update_send_to_screen()