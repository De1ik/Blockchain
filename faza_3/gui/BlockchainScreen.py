import random
import tkinter as tk
from tkinter import ttk, messagebox

from BaseScreen import BaseScreen
from faza_3.Block import Block
from faza_3.RSA import RSAHelper
from faza_3.Blockchain import Blockchain
from faza_3.HandleBlocks import HandleBlocks

class BlockchainScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        # delete all components before new draw
        for widget in self.frame.winfo_children():
            widget.destroy()

        title = tk.Label(self.frame, text="Blockchain", bg=self.frame["bg"],
                         font=("Helvetica", 24, "bold"), fg="#333333")
        title.pack(pady=20)

        # create scroll container
        self.main_container = tk.Frame(self.frame, bg=self.frame["bg"])
        self.main_container.pack(expand=True, fill="both")
        self.canvas = tk.Canvas(self.main_container, bg=self.frame["bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.frame["bg"])
        self.scrollable_frame.bind("<Configure>",
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))   # Linux

        def bind_mousewheel(widget, func):
            widget.bind("<MouseWheel>", func)
            widget.bind("<Button-4>", func)
            widget.bind("<Button-5>", func)
            for child in widget.winfo_children():
                bind_mousewheel(child, func)

        bind_mousewheel(self.scrollable_frame, _on_mousewheel)

        # down container
        self.controls_frame = tk.Frame(self.frame, bg=self.frame["bg"])
        self.controls_frame.pack(fill="x", side="bottom", pady=20)

        # field to select the hash of the prev block
        self.all_blocks = [block_hash.hex() for block_hash in self.app.blockchain.blockchain_dict.keys()] if self.app.blockchain else None
        self.selected_prev_block = tk.StringVar()
        self.dropdown_prev_hash_block = ttk.Combobox(self.controls_frame, textvariable=self.selected_prev_block,
                                                     values=self.all_blocks, state="readonly", width=40)
        self.dropdown_prev_hash_block.pack(pady=10)
        if self.all_blocks:
            self.dropdown_prev_hash_block.set("Choose the block to add after")
            self.dropdown_prev_hash_block["state"] = "readonly"
        else:
            self.dropdown_prev_hash_block["state"] = "disabled"
            self.dropdown_prev_hash_block.set("No blocks exist, create genesis block")
        self.dropdown_prev_hash_block.bind("<<ComboboxSelected>>", self.on_selected_prev_block)

        # container for buttons
        self.main_wrapper = tk.Frame(self.controls_frame, bg=self.frame["bg"])
        self.main_wrapper.pack(expand=True, pady=20)
        self.create_block_btn = tk.Button(
            self.main_wrapper,
            text="Create Block",
            font=("Helvetica", 12, "bold"),
            bg="#4caf50", fg="white", activebackground="#45a049",
            relief="flat",
            command=self.create_new_block
        )
        self.create_block_hash_btn = tk.Button(
            self.main_wrapper,
            text="Create Block On Prev",
            font=("Helvetica", 12, "bold"),
            bg="#4caf50", fg="white", activebackground="#45a049",
            relief="flat",
            command=self.create_block_by_hash
        )
        self.create_block_hash_btn["state"] = "disabled"
        self.create_block_btn.pack(side="left", padx=10, pady=10)
        self.create_block_hash_btn.pack(side="left", padx=10, pady=10)

    def on_selected_prev_block(self, event):
        prev_block = self.selected_prev_block.get()
        if prev_block and prev_block != "Choose the block to add after":
            self.create_block_hash_btn["state"] = "normal"
        else:
            self.create_block_hash_btn["state"] = "disabled"

    def updated_list_of_blocks(self):
        self.all_blocks = [block_hash.hex() for block_hash in self.app.blockchain.blockchain_dict.keys()] if self.app.blockchain else None
        self.dropdown_prev_hash_block.configure(values=self.all_blocks)
        if self.all_blocks:
            self.dropdown_prev_hash_block.set("Select the prev block on which will be added new block")
            self.dropdown_prev_hash_block["state"] = "readonly"
        else:
            self.dropdown_prev_hash_block["state"] = "disabled"
            self.dropdown_prev_hash_block.set("No blocks exist, create genesis block")

    def create_block_by_hash(self):
        prev_block = bytes.fromhex(self.selected_prev_block.get())
        random_addr = random.choice(list(self.app.addresses.values()))
        block = Block(prev_block, random_addr.public_key)
        block.finalize()
        is_block_added = self.app.handle_blocks.block_process(block)
        if not is_block_added:
            messagebox.showerror("Block cannot be created", "No blocks were created")
            return True
        blocknode = self.app.blockchain.blockchain_dict[block.get_hash()]
        self.add_block_info(blocknode)
        self.updated_list_of_blocks()

    def create_new_block(self):
        if not self.app.addresses:
            messagebox.showwarning("Block cannot be created", "No addresses were created")
            return
        random_addr = random.choice(list(self.app.addresses.values()))
        if not self.app.blockchain:
            block = Block(None, random_addr.public_key)
            block.finalize()
            self.app.blockchain = Blockchain(block)
            self.app.handle_blocks = HandleBlocks(self.app.blockchain)
        else:
            block = self.app.handle_blocks.block_create(random_addr.public_key)
        if not block:
            messagebox.showerror("Block cannot be created", "No blocks were created")
            return True
        blocknode = self.app.blockchain.blockchain_dict[block.get_hash()]
        self.add_block_info(blocknode)
        self.updated_list_of_blocks()

    def add_block_info(self, blocknode):
        block_frame = tk.Frame(self.scrollable_frame, bg="white", bd=2, relief="groove")
        block_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(block_frame, text="Block Hash:", bg="white",
                 font=("Helvetica", 10, "bold"), fg="#555555").grid(row=0, column=0, sticky="w", padx=10, pady=2)
        tk.Label(block_frame, text=blocknode.block.get_hash().hex(), bg="white",
                 font=("Helvetica", 10), fg="#333333").grid(row=0, column=1, sticky="w", padx=10, pady=2)

        prev_hash = blocknode.block.get_prev_block_hash()
        prev_hash_short = prev_hash.hex()[:9] if prev_hash else "None"
        tk.Label(block_frame, text="Previous Hash:", bg="white",
                 font=("Helvetica", 10, "bold"), fg="#555555").grid(row=1, column=0, sticky="w", padx=10, pady=2)
        tk.Label(block_frame, text=f"{prev_hash_short}...", bg="white",
                 font=("Helvetica", 10), fg="#333333").grid(row=1, column=1, sticky="w", padx=10, pady=2)

        # transactions
        tk.Label(block_frame, text="Transactions:", bg="white",
                 font=("Helvetica", 10, "underline"), fg="#555555").grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 0))
        coinbase_tx = blocknode.block.get_coinbase()
        output = coinbase_tx.get_outputs()[0]
        address = RSAHelper().get_short_address(output.get_address())
        value = output.get_value()
        tx_hash = coinbase_tx.get_hash().hex()[:24] + "..."
        coinbase_text = f"• COINBASE: {tx_hash} | Address -> {address} | Amount -> {value}"
        tk.Label(block_frame, text=coinbase_text, bg="white",
                 font=("Helvetica", 9), fg="#333333").grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=2)
        row_idx = 4
        for tx in blocknode.block.get_transactions():
            tx_hash_str = tx.get_hash().hex()[:6] + "...)"
            tk.Label(block_frame, text=tx_hash_str, bg="white",
                     font=("Helvetica", 9), fg="#333333").grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=20, pady=2)
            row_idx += 1

        # UTXO pool
        tk.Label(block_frame, text="Final UTXO Pool:", bg="white",
                 font=("Helvetica", 10, "underline"), fg="#555555").grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 0))
        row_idx += 1
        utxo_pool = blocknode.get_utxo_pool_copy()
        for utxo in utxo_pool.get_all_utxo():
            tx_output = utxo_pool.get_tx_output(utxo)
            addr = RSAHelper().get_short_address(tx_output.get_address())
            utxo_info = f"• Tx Hash: {utxo.get_tx_hash().hex()[:24]}... | Index: {utxo.get_index()} | Address: {addr} | Amount: {tx_output.get_value()}"
            tk.Label(block_frame, text=utxo_info, bg="white",
                     font=("Helvetica", 9), fg="#333333").grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=20, pady=2)
            row_idx += 1

