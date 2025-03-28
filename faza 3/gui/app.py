import tkinter as tk

from screens import Screens

class MyApp(Screens):
    NAME_CREATE_TX = "Create Tx"
    NAME_BLOCKCHAIN = "Blockchain"

    def __init__(self, root):
        self.transactions = [
            {"hash": "abc123", "from": "addr1", "to": "addr2", "index": 0, "amount": 50},
            {"hash": "def456", "from": "addr3", "to": "addr4", "index": 1, "amount": 75},
        ]

        self.addresses = {}
        self.tx_pool = {}
        self.utxo_pool = {'utx1': 'sdefrgt423re323', 'utx2': 'sdfdewf', 'utx3': 'wdefrgfwde'}
        self.blockchain = None
        self.handle_blocks = None
        self.last_block_procced = None

        self.root = root
        self.root.title("Beautiful Desktop App")
        self.root.geometry("800x500")
        self.root.minsize(800, 500)
        self.root.maxsize(1000, 1000)
        self.root.configure(bg="#f0f4f8")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.sidebar = tk.Frame(self.root, bg="#37474f", width=400)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content_area = tk.Frame(self.root, bg="#fafafa")
        self.content_area.grid(row=0, column=1, sticky="nsew")

        self.screens = {}

        self.create_sidebar()

        self.create_blockchain_screen(self.NAME_BLOCKCHAIN, "#c8e6c9")
        self.create_address_screen("Addresses", "#e0f7fa")
        self.create_tx_pool_screen("Txs Pool", "#ffe0b2")
        self.create_utxo_pool_screen("UTXO Pool", "#e1bee7")
        self.create_tx_screen(self.NAME_CREATE_TX, "#c8e6c9")

        self.show_screen("main")

    def create_sidebar(self):
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

        buttons = [self.NAME_BLOCKCHAIN, "Addresses", "Txs Pool", "UTXO Pool", self.NAME_CREATE_TX]
        for label in buttons:
            btn = tk.Button(self.sidebar, text=label, command=lambda l=label: self.show_screen(l), **btn_style)
            btn.pack(fill="x", padx=20, pady=5)