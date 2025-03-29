import tkinter as tk
from tkinter import ttk, messagebox

from BaseScreen import BaseScreen
from faza_3.RSA import RSAHelper
from faza_3.Transaction import Transaction



class TxScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.input_rows = []
        self.output_rows = []
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

