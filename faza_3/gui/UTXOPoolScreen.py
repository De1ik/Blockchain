import tkinter as tk
from BaseScreen import BaseScreen
from faza_3.RSA import RSAHelper



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
