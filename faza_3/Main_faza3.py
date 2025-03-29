import tkinter as tk
from tkinter import ttk, messagebox
import random
from RSA import RSAHelper
from Block import Block
from Blockchain import Blockchain
from HandleBlocks import HandleBlocks
from Transaction import Transaction


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


class GraphicalBlockchainScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app

        # create container for canvas
        self.container = tk.Frame(self.frame, bg=bg_color)
        self.container.pack(fill="both", expand=True)

        # scrollbar
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        # canvas for the block of the blockchain
        self.canvas = tk.Canvas(self.container, bg="#fafafa",
                                yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        # match scrollbar with canvas block
        self.scrollbar.config(command=self.canvas.yview)

        # automatically draw after screen started
        self.frame.bind("<Map>", lambda e: self.draw_blockchain())

        # mouse processing
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # для Windows/macOS
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # для Linux
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))  # для Linux

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def draw_blockchain(self):
        # delete all existing canvas block
        self.canvas.delete("all")

        if not self.app.blockchain:
            self.canvas.create_text(400, 300, text="No blockchain data", font=("Arial", 24))
            return

        # find the first block
        genesis = None
        for node in self.app.blockchain.blockchain_dict.values():
            if node.parent is None:
                genesis = node
                break
        if not genesis:
            self.canvas.create_text(400, 300, text="No genesis block", font=("Arial", 24))
            return

        # use the depth search for finding every block
        levels = {}

        def traverse(node, depth):
            if depth not in levels:
                levels[depth] = []
            levels[depth].append(node)
            for child in node.children:
                traverse(child, depth + 1)

        traverse(genesis, 0)

        # drawing config
        canvas_width = self.canvas.winfo_width() or 800
        vertical_spacing = 100
        node_width = 80
        node_height = 40
        y_offset = 50
        positions = {}

        # draw blocks for every height
        for depth, nodes in levels.items():
            n = len(nodes)
            for i, node in enumerate(nodes):
                x = (i + 1) * canvas_width / (n + 1)
                y = y_offset + depth * vertical_spacing
                positions[node] = (x, y)

                self.canvas.create_rectangle(
                    x - node_width / 2, y - node_height / 2,
                    x + node_width / 2, y + node_height / 2,
                    fill="lightblue", outline="black"
                )

                text = f"{node.block.get_hash().hex()[:9]}...\nH:{node.height}"
                self.canvas.create_text(x, y, text=text, font=("Arial", 10))

        # connect blocks
        for depth, nodes in levels.items():
            for node in nodes:
                if node.parent:
                    x1, y1 = positions[node.parent]
                    x2, y2 = positions[node]
                    self.canvas.create_line(x1, y1 + node_height / 2,
                                            x2, y2 - node_height / 2,
                                            arrow=tk.LAST)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


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


class AddressScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self.frame, text="Wallet Addresses", bg=self.frame["bg"],
                         font=("Helvetica", 24, "bold"), fg="#333333")
        title.pack(pady=20)

        # create main container
        self.main_container = tk.Frame(self.frame, bg=self.frame["bg"])
        self.main_container.pack(expand=True, fill="both")
        self.canvas = tk.Canvas(self.main_container, bg=self.frame["bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.frame["bg"])
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))  # Linux

        # down container
        controls_frame = tk.Frame(self.frame, bg=self.frame["bg"])
        controls_frame.pack(fill="x", side="bottom", pady=20)
        buttons_container = tk.Frame(controls_frame, bg=self.frame["bg"])
        buttons_container.pack(expand=True)
        btn_add = tk.Button(buttons_container,
                            text="➕ Create New Address",
                            font=("Helvetica", 12, "bold"),
                            bg="#4caf50", fg="white", activebackground="#45a049",
                            relief="flat", command=self.add_new_address)
        btn_add.pack(side="left", padx=10, pady=10)
        btn_update = tk.Button(buttons_container,
                               text="Update for new txs",
                               font=("Helvetica", 12, "bold"),
                               bg="#4caf50", fg="white", activebackground="#45a049",
                               relief="flat", command=self.update_addresses)
        btn_update.pack(side="left", padx=10, pady=10)

        # data filling
        self.update_addresses()

    def update_addresses(self, address=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        list_addresses = [address] if address else list(self.app.addresses.keys())
        for addr in list_addresses:
            # main block
            addr_frame = tk.Frame(self.scrollable_frame, bg="white", bd=2, relief="groove")
            addr_frame.pack(fill="x", padx=20, pady=10)

            # title
            addr_label = tk.Label(addr_frame, text=addr, bg="white",
                                  font=("Helvetica", 12, "bold"), fg="#222222")
            addr_label.grid(row=0, column=0, sticky="w", padx=10, pady=5, columnspan=2)

            # lines
            separator = tk.Frame(addr_frame, bg="#e0e0e0", height=1)
            separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

            total_amount = 0
            row_index = 2
            # utxo data
            if self.app.blockchain:
                for utxo in self.app.blockchain.get_utxo_pool_at_max_height().get_all_utxo():
                    tx_output = self.app.blockchain.utxo_pool.get_tx_output(utxo)
                    short_addr = RSAHelper().get_short_address(tx_output.get_address())
                    value = tx_output.get_value()
                    if addr == short_addr:
                        total_amount += value
                        utxo_hash = utxo.get_tx_hash().hex()[:24] + "..."
                        info_text = f"Index: {utxo.get_index()} | Amount: {value}"
                        utxo_label = tk.Label(addr_frame,
                                              text=f"{utxo_hash}    {info_text}",
                                              bg="white",
                                              font=("Helvetica", 10),
                                              fg="#555555")
                        utxo_label.grid(row=row_index, column=0, sticky="w", padx=20, pady=2)
                        row_index += 1
            # final amount for addr
            total_label = tk.Label(addr_frame,
                                   text=f"Total Amount: {total_amount}",
                                   bg="white",
                                   font=("Helvetica", 12, "bold"),
                                   fg="#333333")
            total_label.grid(row=row_index, column=0, sticky="w", padx=10, pady=5)

    def add_new_address(self):
        rsa_comp = RSAHelper()
        address = RSAHelper().get_short_address(rsa_comp.public_key)
        self.app.addresses[address] = rsa_comp
        self.update_addresses()


class TxPoolScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.frame.bind("<Map>", lambda event: self.create_widgets())

    def create_widgets(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        title = tk.Label(self.frame, text="Transaction Pool", bg=self.frame["bg"],
                         font=("Helvetica", 24, "bold"), fg="#333333")
        title.pack(pady=20)

        canvas = tk.Canvas(self.frame, bg=self.frame["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.frame["bg"])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/macOS
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux

        if self.app.blockchain:
            tx_list = self.app.blockchain.get_transaction_pool().get_transactions()
            for tx in tx_list:
                tx_frame = tk.Frame(scrollable_frame, bg="white", bd=2, relief="groove")
                tx_frame.pack(fill="x", padx=20, pady=10)

                # hash tx
                header_frame = tk.Frame(tx_frame, bg="white")
                header_frame.pack(fill="x", padx=10, pady=(10, 5))
                hash_label = tk.Label(header_frame, text=f"Transaction Hash: {tx.get_hash().hex()}",
                                      bg="white", font=("Helvetica", 10, "bold"), fg="#222222")
                hash_label.pack(side="left")

                # lines
                separator = tk.Frame(tx_frame, bg="#e0e0e0", height=1)
                separator.pack(fill="x", padx=10, pady=5)

                # inputs
                inputs_frame = tk.Frame(tx_frame, bg="white")
                inputs_frame.pack(fill="x", padx=10, pady=5)
                inputs_title = tk.Label(inputs_frame, text="Inputs:", bg="white",
                                        font=("Helvetica", 10, "bold"), fg="#555555")
                inputs_title.grid(row=0, column=0, sticky="w")
                for idx, inp in enumerate(tx.get_inputs()):
                    input_text = f"{idx+1}. From: {inp.prevTxHash.hex()} | Index: {inp.outputIndex}"
                    inp_label = tk.Label(inputs_frame, text=input_text, bg="white",
                                         font=("Helvetica", 10), fg="#666666")
                    inp_label.grid(row=idx+1, column=0, sticky="w", pady=2)

                # outputs
                outputs_frame = tk.Frame(tx_frame, bg="white")
                outputs_frame.pack(fill="x", padx=10, pady=5)
                outputs_title = tk.Label(outputs_frame, text="Outputs:", bg="white",
                                         font=("Helvetica", 10, "bold"), fg="#555555")
                outputs_title.grid(row=0, column=0, sticky="w")
                for idx, out in enumerate(tx.get_outputs()):
                    output_text = (f"{idx+1}. To: {RSAHelper.get_short_address(out.address)} | "
                                   f"Amount: {out.value}")
                    out_label = tk.Label(outputs_frame, text=output_text, bg="white",
                                         font=("Helvetica", 10), fg="#666666")
                    out_label.grid(row=idx+1, column=0, sticky="w", pady=2)
        else:
            canvas.create_text(400, 300, text="No transaction data available",
                               font=("Helvetica", 24), fill="#888888")


class UTXOPoolScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self.frame, text="UTXO Pool - Latest Block", bg=self.frame["bg"],
                         font=("Helvetica", 24, "bold"), fg="#333333")
        title.pack(pady=20)

        self.main_container = tk.Frame(self.frame, bg=self.frame["bg"])
        self.main_container.pack(expand=True, fill="both")
        self.canvas = tk.Canvas(self.main_container, bg=self.frame["bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.frame["bg"])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))   # Linux

        self.frame.bind("<Map>", lambda e: self.update_utxo())

    def update_utxo(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if self.app.blockchain:
            utxo_pool = self.app.blockchain.get_utxo_pool_at_max_height()
            for utxo in utxo_pool.get_all_utxo():
                tx_output = utxo_pool.get_tx_output(utxo)
                addr = RSAHelper().get_short_address(tx_output.get_address())
                value = tx_output.get_value()

                utxo_frame = tk.Frame(self.scrollable_frame, bg="white", bd=2, relief="groove")
                utxo_frame.pack(fill="x", padx=20, pady=10)

                tk.Label(utxo_frame, text="Tx Hash:", bg="white",
                         font=("Helvetica", 10, "bold"), fg="#555555").grid(row=0, column=0, sticky="w", padx=10, pady=2)
                tk.Label(utxo_frame, text=utxo.get_tx_hash().hex(), bg="white",
                         font=("Helvetica", 10), fg="#333333").grid(row=0, column=1, sticky="w", padx=10, pady=2)

                tk.Label(utxo_frame, text="Index:", bg="white",
                         font=("Helvetica", 10, "bold"), fg="#555555").grid(row=1, column=0, sticky="w", padx=10, pady=2)
                tk.Label(utxo_frame, text=utxo.get_index(), bg="white",
                         font=("Helvetica", 10), fg="#333333").grid(row=1, column=1, sticky="w", padx=10, pady=2)

                tk.Label(utxo_frame, text="Tx Address:", bg="white",
                         font=("Helvetica", 10, "bold"), fg="#555555").grid(row=2, column=0, sticky="w", padx=10, pady=2)
                tk.Label(utxo_frame, text=addr, bg="white",
                         font=("Helvetica", 10), fg="#333333").grid(row=2, column=1, sticky="w", padx=10, pady=2)

                tk.Label(utxo_frame, text="Amount:", bg="white",
                         font=("Helvetica", 10, "bold"), fg="#555555").grid(row=3, column=0, sticky="w", padx=10, pady=2)
                tk.Label(utxo_frame, text=value, bg="white",
                         font=("Helvetica", 10), fg="#333333").grid(row=3, column=1, sticky="w", padx=10, pady=2)


class TxScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        # Списки для динамических рядов входов и выходов
        self.input_rows = []    # каждый элемент — словарь с Combobox и прочими данными
        self.output_rows = []   # каждый элемент — словарь с Combobox для адреса и Entry для суммы
        self.frame.bind("<Map>", lambda event: self.create_widgets())

    def create_widgets(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.input_rows = []
        self.output_rows = []

        title = tk.Label(self.frame, text="Create Transaction", bg=self.frame["bg"], font=("Arial", 24))
        title.pack(pady=20)

        # sender
        sender_addresses = list(self.app.addresses.keys())
        self.selected_sender = tk.StringVar()
        self.dropdown_sender = ttk.Combobox(self.frame, textvariable=self.selected_sender,
                                            values=sender_addresses, state="readonly", width=40)
        self.dropdown_sender.pack(pady=5)
        if sender_addresses:
            self.dropdown_sender.set("Select sender address")
            self.dropdown_sender["state"] = "readonly"
        else:
            self.dropdown_sender["state"] = "disabled"
            self.dropdown_sender.set("No addresses exist")
        self.dropdown_sender.bind("<<ComboboxSelected>>", self.on_sender_selected)

        # inputs UTXO
        inputs_frame = tk.LabelFrame(self.frame, text="Inputs (UTXO)", bg=self.frame["bg"], font=("Arial", 12))
        inputs_frame.pack(pady=10, fill="x", padx=20)
        # add new input
        add_input_btn = tk.Button(inputs_frame, text="Add input", font=("Arial", 10),
                                  command=lambda: self.add_input_row(inputs_frame))
        add_input_btn.pack(pady=5)

        # default input
        self.add_input_row(inputs_frame)

        # outputs
        outputs_frame = tk.LabelFrame(self.frame, text="Output (Address abd Amount)", bg=self.frame["bg"], font=("Arial", 12))
        outputs_frame.pack(pady=10, fill="x", padx=20)
        add_output_btn = tk.Button(outputs_frame, text="Add output", font=("Arial", 10),
                                   command=lambda: self.add_output_row(outputs_frame))
        add_output_btn.pack(pady=5)

        # default output
        self.add_output_row(outputs_frame)

        # confirmation
        self.confirm_btn = tk.Button(self.frame, text="Send", font=("Arial", 12, "bold"),
                                     bg="#4caf50", fg="white", activebackground="#45a049",
                                     relief="flat", command=self.confirm_selection)
        self.confirm_btn.pack(pady=20)

        self.confirm_btn["state"] = "disabled"

        # observe the changes in the state of required fields
        self.selected_sender.trace("w", lambda *args: self.update_confirm_button_state())

    def on_sender_selected(self, event):
        sender = self.selected_sender.get()
        self.get_utxo_per_addr(sender)
        for row in self.input_rows:
            cb = row["combobox"]
            if sender and sender != "Select sender address":
                cb.configure(state="readonly", values=[utxo.hex() for utxo in self.utxo_dict.keys()])
                cb.set("Select UTXO")
            else:
                cb.configure(state="disabled")
        self.update_confirm_button_state()

    def add_input_row(self, parent_frame):
        row_frame = tk.Frame(parent_frame, bg=self.frame["bg"])
        row_frame.pack(fill="x", pady=2)

        selected_utxo = tk.StringVar()
        selected_utxo.trace("w", lambda *args: self.update_confirm_button_state())

        sender = self.selected_sender.get()
        state = "readonly" if sender and sender != "Select sender address" and sender != "No addresses exist" else "disabled"
        cb = ttk.Combobox(row_frame, textvariable=selected_utxo, state=state, width=40)
        cb.pack(side="left", padx=5)
        btn_remove = tk.Button(row_frame, text="Delete", command=lambda: self.remove_input_row(row_frame))
        btn_remove.pack(side="left", padx=5)

        self.input_rows.append({"frame": row_frame, "combobox": cb, "var": selected_utxo})

        if state == "readonly":
            self.get_utxo_per_addr(sender)  # обновляет self.utxo_dict
            if hasattr(self, "utxo_dict"):
                cb.configure(values=[utxo.hex() for utxo in self.utxo_dict.keys()])
                cb.set("Select UTXO")
        self.update_confirm_button_state()

    def remove_input_row(self, row_frame):
        for row in self.input_rows:
            if row["frame"] == row_frame:
                self.input_rows.remove(row)
                break
        row_frame.destroy()
        self.update_confirm_button_state()

    def add_output_row(self, parent_frame):
        row_frame = tk.Frame(parent_frame, bg=self.frame["bg"])
        row_frame.pack(fill="x", pady=2)

        selected_recipient = tk.StringVar()
        selected_recipient.trace("w", lambda *args: self.update_confirm_button_state())
        recipients = list(self.app.addresses.keys())
        cb = ttk.Combobox(row_frame, textvariable=selected_recipient, values=recipients,
                          state="readonly", width=30)
        cb.pack(side="left", padx=5)
        if recipients:
            cb.set("Select the receiver address")
        else:
            cb.set("No addresses")
            cb["state"] = "disabled"

        amount_entry = tk.Entry(row_frame, width=10)
        amount_entry.bind("<KeyRelease>", lambda event: self.update_confirm_button_state())
        amount_entry.pack(side="left", padx=5)
        btn_remove = tk.Button(row_frame, text="Delete", command=lambda: self.remove_output_row(row_frame))
        btn_remove.pack(side="left", padx=5)

        self.output_rows.append(
            {"frame": row_frame, "combobox": cb, "recipient_var": selected_recipient, "amount_entry": amount_entry})
        self.update_confirm_button_state()

    def remove_output_row(self, row_frame):
        for row in self.output_rows:
            if row["frame"] == row_frame:
                self.output_rows.remove(row)
                break
        row_frame.destroy()
        self.update_confirm_button_state()

    def get_utxo_per_addr(self, address):
        self.utxo_dict = dict()
        if not self.app.blockchain:
            return

        utxo_pool_component = self.app.blockchain.get_utxo_pool_at_max_height()
        for utxo in utxo_pool_component.get_all_utxo():
            tx_output = utxo_pool_component.get_tx_output(utxo)
            addr = RSAHelper().get_short_address(tx_output.get_address())
            if addr == address:
                self.utxo_dict[utxo.get_tx_hash()] = utxo

    def update_confirm_button_state(self, *args):
        if not hasattr(self, "confirm_btn") or not self.confirm_btn.winfo_exists():
            return

        valid = bool(self.selected_sender.get() and self.input_rows and self.output_rows)
        for row in self.input_rows:
            if not row["var"].get() or row["var"].get() == "Выберите UTXO":
                valid = False
                break
        for row in self.output_rows:
            if not row["recipient_var"].get() or row["recipient_var"].get() == "Выберите адрес получателя":
                valid = False
                break
            try:
                amount = float(row["amount_entry"].get())
                if amount <= 0:
                    valid = False
                    break
            except ValueError:
                valid = False
                break

        self.confirm_btn["state"] = "normal" if valid else "disabled"

    def is_valid_float(self, new_value):
        if new_value == "":
            return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False

    def confirm_selection(self):
        if not self.app.blockchain:
            messagebox.showwarning("Tx cannot be created", "No blockchain data available")
            return

        sender_address = self.selected_sender.get()
        if sender_address not in self.app.addresses:
            messagebox.showwarning("Tx cannot be created", "Invalid sender address")
            return

        sender_object = self.app.addresses[sender_address]
        tx = Transaction()

        # add all inputs
        for row in self.input_rows:
            utxo_hex = row["var"].get()
            try:
                utxo_hash = bytes.fromhex(utxo_hex)
            except Exception as e:
                continue
            utxo = self.utxo_dict.get(utxo_hash)
            if utxo is None:
                messagebox.showerror("Error", "Tx was not created due to some issues")

            self.app.blockchain.get_utxo_pool_at_max_height().get_tx_output(utxo)
            index = utxo.get_index()
            tx.add_input(utxo_hash, index)

        # add all outputs
        for row in self.output_rows:
            recipient = row["recipient_var"].get()
            if recipient not in self.app.addresses:
                continue
            try:
                amount = float(row["amount_entry"].get())
            except ValueError:
                continue
            recipient_object = self.app.addresses[recipient]
            tx.add_output(amount, address=recipient_object.public_key)

        for i in range(len(tx.get_inputs())):
            data_to_sign = tx.get_data_to_sign(i)
            signature = sender_object.sign(data_to_sign)
            tx.add_signature(signature, i)
        tx.finalize()

        is_added = self.app.blockchain.transaction_add(tx)
        if is_added:
            messagebox.showinfo("Success", "Tx was created")
            self.create_widgets()
        else:
            messagebox.showerror("Error", "Tx was not created due to some issues")


class MyApp:
    NAME_BLOCKCHAIN_DIAGRAM = "Graphical BC"
    NAME_CREATE_TX = "Create Tx"
    NAME_BLOCKCHAIN = "Blockchain"
    NAME_ADDRESS_SCREEN = "Address"
    NAME_TXS_POOL = "Txs Pool"
    NAME_UTXO_POOL = "UTXO Pool"

    def __init__(self, root):
        # set up config
        self.root = root
        self.root.title("Artem Blockchain")
        self.root.attributes("-fullscreen", True)
        self.is_fullscreen = True
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<Configure>", self.on_configure)
        self.root.configure(bg="#f0f4f8")
        self.root.geometry("900x600")
        self.root.minsize(700, 550)
        # self.root.maxsize(1000, 600)

        # layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # left menu
        sidebar_buttons = [self.NAME_BLOCKCHAIN_DIAGRAM, self.NAME_BLOCKCHAIN, self.NAME_ADDRESS_SCREEN, self.NAME_TXS_POOL, self.NAME_UTXO_POOL, self.NAME_CREATE_TX]
        self.sidebar = Sidebar(self.root, sidebar_buttons, self.show_screen)

        # content area
        self.content_area = tk.Frame(self.root, bg="#fafafa")
        self.content_area.grid(row=0, column=1, sticky="nsew")

        # blockchain required attributes
        self.addresses = {}
        self.tx_pool = {}
        self.blockchain = None
        self.handle_blocks = None
        self.last_block_procced = None
        self.screens = {}


        # screen init
        self.screens[self.NAME_BLOCKCHAIN_DIAGRAM] = GraphicalBlockchainScreen(self.content_area, self, self.NAME_BLOCKCHAIN_DIAGRAM, "#ffffff")
        self.screens[self.NAME_BLOCKCHAIN] = BlockchainScreen(self.content_area, self, self.NAME_BLOCKCHAIN, "#c8e6c9")
        self.screens[self.NAME_ADDRESS_SCREEN] = AddressScreen(self.content_area, self, self.NAME_ADDRESS_SCREEN, "#e0f7fa")
        self.screens[self.NAME_TXS_POOL] = TxPoolScreen(self.content_area, self, self.NAME_TXS_POOL, "#ffe0b2")
        self.screens[self.NAME_UTXO_POOL] = UTXOPoolScreen(self.content_area, self, self.NAME_UTXO_POOL, "#e1bee7")
        self.screens[self.NAME_CREATE_TX] = TxScreen(self.content_area, self, self.NAME_CREATE_TX, "#c8e6c9")
        self.show_screen(self.NAME_BLOCKCHAIN)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        self.root.geometry("900x600")

    def on_configure(self, event=None):
        if not self.is_fullscreen:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            win_width = self.root.winfo_width()
            win_height = self.root.winfo_height()

            if abs(win_width - screen_width) < 10 and abs(win_height - screen_height) < 10:
                self.root.attributes("-fullscreen", True)
                self.is_fullscreen = True

    def show_screen(self, name):
        for screen in self.screens.values():
            screen.forget()
        screen = self.screens.get(name)
        if screen:
            screen.pack(expand=True, fill="both")






if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()