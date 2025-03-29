import tkinter as tk
from BaseScreen import BaseScreen
from faza_3.RSA import RSAHelper


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
