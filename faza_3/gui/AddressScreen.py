import tkinter as tk
from faza_3.RSA import RSAHelper
from .BaseScreen import BaseScreen


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
