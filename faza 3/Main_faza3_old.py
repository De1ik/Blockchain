import tkinter as tk
from tkinter import ttk
from RSA import RSAHelper
from tkinter import messagebox
import random

from Block import Block
from Blockchain import Blockchain
from HandleBlocks import HandleBlocks

class MyApp:

    NAME_CREATE_TX = "Create Tx"
    NAME_BLOCKCHAIN = "Blockchain"

    def __init__(self, root):
        self.transactions = [
            {"hash": "abc123", "from": "addr1", "to": "addr2", "index": 0, "amount": 50},
            {"hash": "def456", "from": "addr3", "to": "addr4", "index": 1, "amount": 75},
            # etc.
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

        # Configure grid layout on root
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar (fixed width)
        self.sidebar = tk.Frame(self.root, bg="#37474f", width=400)
        self.sidebar.grid(row=0, column=0, sticky="ns")  # north-south fill

        # Content area (expandable)
        self.content_area = tk.Frame(self.root, bg="#fafafa")
        self.content_area.grid(row=0, column=1, sticky="nsew")  # fill all directions

        self.screens = {}

        self.create_sidebar()

        self.create_blockchain_screen(self.NAME_BLOCKCHAIN, "#c8e6c9")
        self.create_address_screen("Addresses", "#e0f7fa")
        self.create_tx_pool_screen("Txs Pool", "#ffe0b2")
        self.create_utxo_pool_screen("UTXO Pool", "#e1bee7")
        self.create_tx_screen(self.NAME_CREATE_TX, "#c8e6c9")

        self.show_screen("main")

    def create_sidebar(self):
        # Button style options
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

    def create_main_screen(self):
        main_screen = tk.Label(self.content_area, text=self.NAME_BLOCKCHAIN, bg="#fafafa", font=("Arial", 24))
        main_screen.pack(expand=True)
        self.screens[self.NAME_BLOCKCHAIN] = main_screen

    def create_screen(self, name, color):
        frame = tk.Frame(self.content_area, bg=color)
        label = tk.Label(frame, text=name, bg=color, font=("Arial", 24))
        label.pack(expand=True)
        self.screens[name] = frame

    def create_tx_pool_screen(self, name, color):
        frame = tk.Frame(self.content_area, bg=color)

        title = tk.Label(frame, text=name, bg=color, font=("Arial", 24))
        title.pack(pady=20)

        # Scrollable canvas setup
        canvas = tk.Canvas(frame, bg=color, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sample transaction list (replace with your real data)
        self.transactions = [
            {"hash": "abc123", "from": "wallet1", "to": "wallet2", "index": 0, "amount": 100},
            {"hash": "def456", "from": "wallet3", "to": "wallet4", "index": 1, "amount": 50},
            {"hash": "ghi789", "from": "wallet5", "to": "wallet6", "index": 2, "amount": 200},
        ]

        # Transaction cards
        for tx in self.transactions:
            tx_frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief="raised")
            tx_frame.pack(fill="x", padx=20, pady=10)

            tk.Label(tx_frame, text=f"Hash: {tx['hash']}", bg="white", font=("Arial", 10, "bold")).pack(anchor="w",
                                                                                                        padx=10, pady=2)
            tk.Label(tx_frame, text=f"From: {tx['from']}", bg="white", font=("Arial", 10)).pack(anchor="w", padx=10,
                                                                                                pady=2)
            tk.Label(tx_frame, text=f"To: {tx['to']}", bg="white", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)
            tk.Label(tx_frame, text=f"Index: {tx['index']}", bg="white", font=("Arial", 10)).pack(anchor="w", padx=10,
                                                                                                  pady=2)
            tk.Label(tx_frame, text=f"Amount: {tx['amount']}", bg="white", font=("Arial", 10)).pack(anchor="w", padx=10,
                                                                                                    pady=2)

        self.screens[name] = frame

    def is_valid_float(self, new_value):
        if new_value == "":
            return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False


    # utxo screen
    def create_utxo_pool_screen(self, name, color, block=None):
        frame = tk.Frame(self.content_area, bg=color)

        title = tk.Label(frame, text="Utxo Pool For The Latest Block", bg=color, font=("Arial", 24))
        title.pack(pady=20)

        main_container = tk.Frame(frame, bg=color)
        main_container.pack(expand=True, fill="both")

        canvas = tk.Canvas(main_container, bg=color, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=color)

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
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))


        def update_utxo():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()


            if self.blockchain:
                for utxo in self.blockchain.get_utxo_pool_at_max_height().get_all_utxo():
                    utxo_frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief="groove")
                    utxo_frame.pack(padx=20, pady=10, anchor='center')

                    tx_output = self.blockchain.utxo_pool.get_tx_output(utxo)
                    addr = RSAHelper().get_short_address(tx_output.get_address())
                    value = tx_output.get_value()

                    utxo_hash = f"• Tx Hash: {utxo.get_tx_hash()[:6]}"
                    utxo_index = f"• Index {utxo.get_index()}"
                    utxo_addr = f"• Tx Address: {addr}"
                    utxo_value = f"• Amount {value}"
                    tk.Label(utxo_frame, text=utxo_hash, bg="white", font=("Arial", 12)).pack(anchor="w", padx=20)
                    tk.Label(utxo_frame, text=utxo_index, bg="white", font=("Arial", 12)).pack(anchor="w", padx=20)
                    tk.Label(utxo_frame, text=utxo_addr, bg="white", font=("Arial", 12)).pack(anchor="w", padx=20)
                    tk.Label(utxo_frame, text=utxo_value, bg="white", font=("Arial", 12)).pack(anchor="w", padx=20)


        self.screens[name] = frame
        frame.bind("<Map>", lambda e: update_utxo())

    # address screen
    def create_address_screen(self, name, color):
        frame = tk.Frame(self.content_area, bg=color)

        title = tk.Label(frame, text="Wallet Addresses", bg=color, font=("Arial", 24))
        title.pack(pady=20)

        main_container = tk.Frame(frame, bg=color)
        main_container.pack(expand=True, fill="both")

        canvas = tk.Canvas(main_container, bg=color, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=color)

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
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))




            # for utxo in self.blockchain.get_utxo_pool_at_max_height().utxo_pool.get_all_utxo():
            #     tx_output = self.blockchain.utxo_pool.get_tx_output(utxo)
            #     addr = RSAHelper().get_short_address(tx_output.get_address())
            #
            #     utxo_info = f"• Tx Hash: {utxo.get_tx_hash()[:6]} # Index {utxo.get_index()} # Address: {addr} # Amount {tx_output.get_value()}"
            #     tk.Label(addr_frame, text=utxo_info, bg="white", font=("Arial", 9)).pack(anchor="w", padx=20)

        def update_addresses(address = None):
            if not address:
                for widget in scrollable_frame.winfo_children():
                    widget.destroy()
                list_addresses = list(self.addresses.keys())
            else:
                list_addresses = [address]

            for address in list_addresses:
                addr_frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief="groove")
                addr_frame.pack(fill="x", padx=20, pady=10)

                label_address = tk.Label(addr_frame, text=address, bg="white", font=("Arial", 10, "bold"))
                label_address.pack(anchor="w", padx=10, pady=2)

                label_amount = tk.Label(addr_frame, bg="white", font=("Arial", 10, "bold"))
                label_amount.pack(anchor="w", padx=10, pady=2)

                total_amount = 0
                if self.blockchain:
                    for utxo in self.blockchain.get_utxo_pool_at_max_height().get_all_utxo():
                        tx_output = self.blockchain.utxo_pool.get_tx_output(utxo)
                        addr = RSAHelper().get_short_address(tx_output.get_address())
                        value = tx_output.get_value()
                        print("address == addr")
                        print(f"{address} == {addr}")
                        if address == addr:
                            total_amount += value
                            print("AMOUNT 1:", total_amount)
                            utxo_info = f"• Tx Hash: {utxo.get_tx_hash()[:6]} # Index {utxo.get_index()} # Address: {addr} # Amount {value}"
                            tk.Label(addr_frame, text=utxo_info, bg="white", font=("Arial", 9)).pack(anchor="w", padx=20)

                print("AMOUNT 2:", total_amount)
                label_amount.config(text=f"Total Amount: {total_amount}")


        def add_new_address():
            rsa_comp = RSAHelper()
            address = RSAHelper().get_short_address(rsa_comp.public_key)
            self.addresses[address] = rsa_comp
            update_addresses(address)

        update_addresses()

        controls_frame = tk.Frame(frame, bg=color)
        controls_frame.pack(fill="x", side="bottom", pady=20)

        main_wrapper = tk.Frame(controls_frame, bg=color)
        main_wrapper.pack(fill="x", expand=True, pady=20)
        # Create new address button
        btn_add = tk.Button(main_wrapper, text="➕ Create New Address", font=("Arial", 12, "bold"),
                            bg="#4caf50", fg="white", activebackground="#45a049",
                            relief="flat", command=add_new_address)
        btn_add.pack(pady=10)

        self.screens[name] = frame

        def update_screen():
            if self.last_block_procced and self.last_block_procced.get_hash() == self.blockchain.get_block_at_max_height().block.get_hash():
                update_addresses()

        frame.bind("<Map>", lambda e: update_screen())

    # screen for the creation od the tx
    def create_tx_screen(self, name, color):
        frame = tk.Frame(self.content_area, bg=color)

        title = tk.Label(frame, text="Select recipient address", bg=color, font=("Arial", 24))
        title.pack(pady=20)

        recipient_addresses = list(self.addresses.keys())
        self.selected_recipient = tk.StringVar()
        self.dropdown_address = ttk.Combobox(frame, textvariable=self.selected_recipient,values=recipient_addresses, state="readonly", width=40)
        self.dropdown_address.pack(pady=10)
        if recipient_addresses:
            self.dropdown_address.set("Select address send to")
            self.dropdown_address["state"] = "readonly"
        else:
            self.dropdown_address["state"] = "disabled"
            self.dropdown_address.set("No address were created")


        input_utxo = list(self.utxo_pool.keys())
        self.selected_utxo = tk.StringVar()
        self.dropdown_utxo = ttk.Combobox(frame, textvariable=self.selected_utxo,values=input_utxo, state="readonly", width=40)
        self.dropdown_utxo.pack(pady=10)
        if input_utxo:
            self.dropdown_utxo.set("Select the utxo")
            self.dropdown_utxo["state"] = "readonly"
        else:
            self.dropdown_utxo["state"] = "disabled"
            self.dropdown_utxo.set("No utxo for this address")


        vcmd = (root.register(self.is_valid_float), "%P")
        tk.Label(frame, text="Enter amount:", bg=color, font=("Arial", 12)).pack(pady=10)
        self.amount_entry = tk.Entry(frame, validate="key", validatecommand=vcmd)
        self.amount_entry.pack(pady=5)

        def confirm_selection():
            selected_addr = self.selected_recipient.get()
            selected_utxo = self.selected_utxo.get()
            selected_amnt = self.amount_entry.get()
            print("Create tx:", selected_addr, selected_utxo, selected_amnt)
            # messagebox.showinfo("Success", f"Send to address (public key):\n{selected}")

        confirm_btn = tk.Button(frame, text="Send", font=("Arial", 12, "bold"),
                                bg="#4caf50", fg="white", activebackground="#45a049",
                                relief="flat", command=confirm_selection)
        confirm_btn.pack(pady=20)

        self.screens[name] = frame

    # function to update the screen of the tx creation
    def update_send_to_screen(self):
        if hasattr(self, "dropdown_address"):
            recipient_addresses = list(self.addresses.keys())
            self.dropdown_address['values'] = recipient_addresses
            if recipient_addresses:
                self.dropdown_address.set("Select address send to")
                self.dropdown_address["state"] = "readonly"
            else:
                self.dropdown_address["state"] = "disabled"
                self.dropdown_address.set("No address were created")

        if hasattr(self, "dropdown_utxo"):
            input_utxo = list(self.utxo_pool.keys())
            self.dropdown_utxo['values'] = input_utxo
            if input_utxo:
                self.dropdown_utxo.set("Select the utxo")
                self.dropdown_utxo["state"] = "readonly"
            else:
                self.dropdown_utxo["state"] = "disabled"
                self.dropdown_utxo.set("No utxo for this address")
        return True

    # Add blocks
    def create_blockchain_screen(self, name, color):
        frame = tk.Frame(self.content_area, bg=color)

        title = tk.Label(frame, text="Blockchain", bg=color, font=("Arial", 24))
        title.pack(pady=20)

        main_container = tk.Frame(frame, bg=color)
        main_container.pack(expand=True, fill="both")

        # Scrollable canvas
        canvas = tk.Canvas(main_container, bg=color, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse detection
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/macOS
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))


        controls_frame = tk.Frame(frame, bg=color)
        controls_frame.pack(fill="x", side="bottom", pady=20)

        main_wrapper = tk.Frame(controls_frame, bg=color)
        main_wrapper.pack(fill="x", expand=True, pady=20)


        # Visualization block info
        def add_block_info(blocknode):
            block_frame = tk.Frame(scrollable_frame, bg="white", bd=2, relief="groove")
            block_frame.pack(fill="x", padx=20, pady=10)

            # Headers (hashes)
            tk.Label(block_frame, text=f"Block hash (short): {blocknode.block.get_hash()[:12]}", bg="white",
                     font=("Arial", 10, "bold")).pack(
                anchor="w", padx=10, pady=2)
            blocknode_pr_hash = blocknode.block.get_prev_block_hash()
            prev_hash = blocknode_pr_hash if blocknode_pr_hash is None else blocknode_pr_hash[:12]
            tk.Label(block_frame, text=f"Previous hash (short): {prev_hash}", bg="white", font=("Arial", 10)).pack(
                anchor="w", padx=10, pady=2)

            # Transactions
            tk.Label(block_frame, text="Transactions:", bg="white", font=("Arial", 10, "underline")).pack(anchor="w",
                                                                                                          padx=10,
                                                                                                          pady=(5, 0))

            coinbase_tx = blocknode.block.get_coinbase()
            output = coinbase_tx.get_outputs()[0]
            address = RSAHelper().get_short_address(output.get_address())
            value = output.get_value()
            tx_hash = f"• COINBASE: {coinbase_tx.get_hash()[:6]} # address -> {address} # value -> {value} "
            tk.Label(block_frame, text=tx_hash, bg="white", font=("Arial", 9)).pack(anchor="w", padx=20)

            for tx in blocknode.block.get_transactions():
                tx_hash = f"{tx.get_hash()[:6]})"
                tk.Label(block_frame, text=tx_hash, bg="white", font=("Arial", 9)).pack(anchor="w", padx=20)

            # UTXO pool
            tk.Label(block_frame, text="Final UTXO Pool:", bg="white", font=("Arial", 10, "underline")).pack(anchor="w",
                                                                                                             padx=10,
                                                                                                             pady=(
                                                                                                             5, 0))
            utxo_pool = blocknode.get_utxo_pool_copy()
            for utxo in utxo_pool.get_all_utxo():
                tx_output = utxo_pool.get_tx_output(utxo)
                addr = RSAHelper().get_short_address(tx_output.get_address())

                utxo_info = f"• Tx Hash: {utxo.get_tx_hash()[:6]} # Index {utxo.get_index()} # Address: {addr} # Amount {tx_output.get_value()}"
                tk.Label(block_frame, text=utxo_info, bg="white", font=("Arial", 9)).pack(anchor="w", padx=20)

        def create_new_block():
            if not self.addresses:
                messagebox.showinfo("Warning", "No addresses were created")
            else:
                if not self.blockchain:
                    random_addr = random.choice(list(self.addresses.values()))
                    block = Block(None, random_addr.public_key)
                    block.finalize()
                    self.blockchain = Blockchain(block)
                    self.handle_blocks = HandleBlocks(self.blockchain)
                else:
                    random_addr = random.choice(list(self.addresses.values()))
                    block = self.handle_blocks.block_create(random_addr.public_key)

                self.last_block_procced = block
                blocknode = self.blockchain.blockchain_dict[block.get_hash()]
                add_block_info(blocknode)
            print("New block created")

        self.selected_block = tk.StringVar()
        def create_new_block_by_prev_block():
            selected_block = self.selected_block.get()

            if not self.addresses:
                messagebox.showinfo("Warning", "No addresses were created")
            else:
                if not self.blockchain:
                    random_addr = random.choice(list(self.addresses.values()))
                    block = Block(None, random_addr.public_key)
                    block.finalize()
                    self.blockchain = Blockchain(block)
                    self.handle_blocks = HandleBlocks(self.blockchain)
                else:
                    random_addr = random.choice(list(self.addresses.values()))
                    block = self.handle_blocks.block_create(random_addr.public_key)

                self.last_block_procced = block
                blocknode = self.blockchain.blockchain_dict[block.get_hash()]
                add_block_info(blocknode)
            print("New block created")

        def update_screen():
            all_blocknodes = list(self.blockchain.blockchain_dict.values())

            self.selected_blocknode = tk.StringVar()
            self.dropdown_blocknodes = ttk.Combobox(frame, textvariable=self.selected_blocknode, values=all_blocknodes, state="readonly", width=40)
            self.dropdown_blocknodes.pack(pady=10)

            if all_blocknodes:
                self.dropdown_blocknodes.set("Select the prev block")
                self.dropdown_blocknodes["state"] = "readonly"
            else:
                self.dropdown_blocknodes["state"] = "disabled"
                self.dropdown_blocknodes.set("You need create genesis block")

        self.create_block_btn = tk.Button(main_wrapper,
                                     text="Create Block",
                                     font=("Arial", 12, "bold"),
                                     bg="#4caf50", fg="white", activebackground="#45a049",
                                     relief="flat",
                                     command=create_new_block)
        self.create_block_btn.pack(anchor="center", pady=10)

        self.create_block_btn_by_height = tk.Button(main_wrapper,
                                     text="Create Block By Height",
                                     font=("Arial", 12, "bold"),
                                     bg="#4caf50", fg="white", activebackground="#45a049",
                                     relief="flat",
                                     command=create_new_block)
        self.create_block_btn_by_height.pack(anchor="center", pady=10)

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

        # if name == self.NAME_BLOCKCHAIN and update:
        #     self.update_blockchain_screen()
        #     self.show_screen(self.NAME_BLOCKCHAIN, False)





if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
