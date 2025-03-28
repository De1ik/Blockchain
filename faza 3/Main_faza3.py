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

# Базовый класс для экранов
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
        # Создаем Canvas для отрисовки графа блокчейна
        self.canvas = tk.Canvas(self.frame, bg="#fafafa")
        self.canvas.pack(fill="both", expand=True)
        # При отображении экрана запускаем перерисовку графа
        self.frame.bind("<Map>", lambda e: self.draw_blockchain())

    def draw_blockchain(self):
        # Очищаем canvas
        self.canvas.delete("all")
        if not self.app.blockchain:
            self.canvas.create_text(400, 300, text="No blockchain data", font=("Arial", 24))
            return

        # Ищем генезис-блок (узел без родителя)
        genesis = None
        for node in self.app.blockchain.blockchain_dict.values():
            if node.parent is None:
                genesis = node
                break
        if not genesis:
            self.canvas.create_text(400, 300, text="No genesis block", font=("Arial", 24))
            return

        # Собираем узлы по уровням (глубинах) с помощью обхода в ширину
        levels = {}
        def traverse(node, depth):
            if depth not in levels:
                levels[depth] = []
            levels[depth].append(node)
            for child in node.children:
                traverse(child, depth + 1)
        traverse(genesis, 0)

        # Параметры отрисовки
        canvas_width = self.canvas.winfo_width() or 800
        vertical_spacing = 100
        node_width = 80
        node_height = 40
        y_offset = 50  # отступ сверху
        positions = {}  # сопоставляем узел -> (x, y)

        # Для каждого уровня равномерно располагаем узлы по горизонтали
        for depth, nodes in levels.items():
            n = len(nodes)
            for i, node in enumerate(nodes):
                x = (i + 1) * canvas_width / (n + 1)
                y = y_offset + depth * vertical_spacing
                positions[node] = (x, y)
                # Отрисовываем прямоугольник для узла
                self.canvas.create_rectangle(x - node_width / 2, y - node_height / 2,
                                             x + node_width / 2, y + node_height / 2,
                                             fill="lightblue", outline="black")
                # Выводим текст с кратким хэшем и высотой
                text = f"{node.block.get_hash()[:6]}\nH:{node.height}"
                self.canvas.create_text(x, y, text=text, font=("Arial", 10))

        # Рисуем линии от родителя к дочерним узлам
        for depth, nodes in levels.items():
            for node in nodes:
                if node.parent:
                    x1, y1 = positions[node.parent]
                    x2, y2 = positions[node]
                    # Линия от нижней границы родителя до верхней границы ребенка
                    self.canvas.create_line(x1, y1 + node_height / 2,
                                            x2, y2 - node_height / 2,
                                            arrow=tk.LAST)



class BlockchainScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.create_widgets()
    def create_widgets(self):
        title = tk.Label(self.frame, text="Blockchain", bg=self.frame["bg"], font=("Arial", 24))
        title.pack(pady=20)
        self.main_container = tk.Frame(self.frame, bg=self.frame["bg"])
        self.main_container.pack(expand=True, fill="both")
        # Настройка прокручиваемого холста
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
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        # Панель управления
        self.controls_frame = tk.Frame(self.frame, bg=self.frame["bg"])
        self.controls_frame.pack(fill="x", side="bottom", pady=20)
        self.main_wrapper = tk.Frame(self.controls_frame, bg=self.frame["bg"])
        self.main_wrapper.pack(fill="x", expand=True, pady=20)
        self.create_block_btn = tk.Button(
            self.main_wrapper,
            text="Create Block",
            font=("Arial", 12, "bold"),
            bg="#4caf50", fg="white", activebackground="#45a049",
            relief="flat",
            command=self.create_new_block
        )
        self.create_block_btn.pack(anchor="center", pady=10)


    def create_new_block(self):
        if not self.app.addresses:
            messagebox.showwarning("Block can not be created", "No addresses were created")
            return
        if not self.app.blockchain:
            random_addr = random.choice(list(self.app.addresses.values()))
            block = Block(None, random_addr.public_key)
            block.finalize()
            self.app.blockchain = Blockchain(block)
            self.app.handle_blocks = HandleBlocks(self.app.blockchain)
        else:
            random_addr = random.choice(list(self.app.addresses.values()))
            block = self.app.handle_blocks.block_create(random_addr.public_key)

        # self.app.last_block_procced = block
        blocknode = self.app.blockchain.blockchain_dict[block.get_hash()]
        self.add_block_info(blocknode)


    def add_block_info(self, blocknode):
        block_frame = tk.Frame(self.scrollable_frame, bg="white", bd=2, relief="groove")
        block_frame.pack(fill="x", padx=20, pady=10)

        # show hash info
        tk.Label(block_frame, text=f"Block hash (short): {blocknode.block.get_hash()[:12]}",
                 bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)
        prev_hash = blocknode.block.get_prev_block_hash()
        prev_hash_short = prev_hash[:12] if prev_hash else "None"
        tk.Label(block_frame, text=f"Previous hash (short): {prev_hash_short}",
                 bg="white", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)

        # show tx info
        tk.Label(block_frame, text="Transactions:", bg="white", font=("Arial", 10, "underline")).pack(
            anchor="w", padx=10, pady=(5, 0))
        coinbase_tx = blocknode.block.get_coinbase()
        output = coinbase_tx.get_outputs()[0]
        address = RSAHelper().get_short_address(output.get_address())
        value = output.get_value()
        tx_hash = f"• COINBASE: {coinbase_tx.get_hash()[:6]} # address -> {address} # value -> {value}"
        tk.Label(block_frame, text=tx_hash, bg="white", font=("Arial", 9)).pack(anchor="w", padx=20)
        for tx in blocknode.block.get_transactions():
            tx_hash = f"{tx.get_hash()[:6]})"
            tk.Label(block_frame, text=tx_hash, bg="white", font=("Arial", 9)).pack(anchor="w", padx=20)

        # UTXO pool after this block was processed
        tk.Label(block_frame, text="Final UTXO Pool:", bg="white", font=("Arial", 10, "underline")).pack(
            anchor="w", padx=10, pady=(5, 0))
        utxo_pool = blocknode.get_utxo_pool_copy()
        for utxo in utxo_pool.get_all_utxo():
            tx_output = utxo_pool.get_tx_output(utxo)
            addr = RSAHelper().get_short_address(tx_output.get_address())
            utxo_info = f"• Tx Hash: {utxo.get_tx_hash()[:6]} # Index {utxo.get_index()} # Address: {addr} # Amount {tx_output.get_value()}"
            tk.Label(block_frame, text=utxo_info, bg="white", font=("Arial", 9)).pack(anchor="w", padx=20)



class AddressScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.create_widgets()
    def create_widgets(self):
        title = tk.Label(self.frame, text="Wallet Addresses", bg=self.frame["bg"], font=("Arial", 24))
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
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        controls_frame = tk.Frame(self.frame, bg=self.frame["bg"])
        controls_frame.pack(fill="x", side="bottom", pady=20)

        buttons_container = tk.Frame(controls_frame, bg=self.frame["bg"])
        buttons_container.pack(expand=True)

        btn_add = tk.Button(
            buttons_container,
            text="➕ Create New Address",
            font=("Arial", 12, "bold"),
            bg="#4caf50", fg="white", activebackground="#45a049",
            relief="flat",
            command=self.add_new_address
        )
        btn_add.pack(side="left", padx=10, pady=10)

        btn_update = tk.Button(
            buttons_container,
            text="Update to proceed new txs",
            font=("Arial", 12, "bold"),
            bg="#4caf50", fg="white", activebackground="#45a049",
            relief="flat",
            command=self.update_addresses
        )
        btn_update.pack(side="left", padx=10, pady=10)

    def update_addresses(self, address=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        list_addresses = [address] if address else list(self.app.addresses.keys())
        for addr in list_addresses:
            print(addr[:10])
            addr_frame = tk.Frame(self.scrollable_frame, bg="white", bd=1, relief="groove")
            addr_frame.pack(fill="x", padx=20, pady=10)
            tk.Label(addr_frame, text=addr, bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)
            total_amount = 0
            if self.app.blockchain :
                for utxo in self.app.blockchain.get_utxo_pool_at_max_height().get_all_utxo():
                    tx_output = self.app.blockchain.utxo_pool.get_tx_output(utxo)
                    short_addr = RSAHelper().get_short_address(tx_output.get_address())
                    value = tx_output.get_value()
                    if addr == short_addr:
                        total_amount += value
                        utxo_info = f"• Tx Hash: {utxo.get_tx_hash()[:6]} # Index {utxo.get_index()} # Address: {short_addr} # Amount {value}"
                        tk.Label(addr_frame, text=utxo_info, bg="white", font=("Arial", 9)).pack(anchor="w", padx=20)
            tk.Label(addr_frame, text=f"Total Amount: {total_amount}", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)


    def add_new_address(self):
        rsa_comp = RSAHelper()
        address = RSAHelper().get_short_address(rsa_comp.public_key)
        self.app.addresses[address] = rsa_comp
        addr_frame = tk.Frame(self.scrollable_frame, bg="white", bd=1, relief="groove")
        addr_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(addr_frame, text=address, bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)
        total_amount = 0
        tk.Label(addr_frame, text=f"Total Amount: {total_amount}", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)


class TxPoolScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.frame.bind("<Map>", lambda event: self.create_widgets())

    def create_widgets(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        title = tk.Label(self.frame, text="Txs Pool", bg=self.frame["bg"], font=("Arial", 24))
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
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        if self.app.blockchain:
            print("TX POOL:", self.app.blockchain.get_transaction_pool().get_transactions())
            for tx in self.app.blockchain.get_transaction_pool().get_transactions():
                tx_frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief="raised")
                tx_frame.pack(fill="x", padx=20, pady=10)
                tk.Label(tx_frame, text=f"Hash: {tx.get_hash()[:10]}", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)

                inputs = tx.get_inputs()
                tk.Label(tx_frame, text=f"INPUTS", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)
                counter = 0
                for input in inputs:
                    tk.Label(tx_frame, text=f"№{counter}", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10,pady=2)
                    tk.Label(tx_frame, text=f"From: {input.prevTxHash[:12]}", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10,pady=2)
                    tk.Label(tx_frame, text=f"Index: {input.index}", bg="white",font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)

                outputs = tx.get_outputs()
                tk.Label(tx_frame, text=f"OUTPUTS", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10,pady=2)
                counter = 0
                for output in outputs:
                    tk.Label(tx_frame, text=f"№{counter}", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10,pady=2)
                    tk.Label(tx_frame, text=f"Address to: {RSAHelper.get_short_address(output.address)}", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=10,pady=2)
                    tk.Label(tx_frame, text=f"Amount: {output.vakue}", bg="white",font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=2)


# Экран пула UTXO
class UTXOPoolScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self.frame, text="Utxo Pool For The Latest Block", bg=self.frame["bg"], font=("Arial", 24))
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
        # Обновление UTXO при отображении экрана
        self.frame.bind("<Map>", lambda e: self.update_utxo())

    def update_utxo(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        if self.app.blockchain:
            for utxo in self.app.blockchain.get_utxo_pool_at_max_height().get_all_utxo():
                utxo_frame = tk.Frame(self.scrollable_frame, bg="white", bd=1, relief="groove")
                utxo_frame.pack(padx=20, pady=10, anchor='center')
                tx_output = self.app.blockchain.utxo_pool.get_tx_output(utxo)
                addr = RSAHelper().get_short_address(tx_output.get_address())
                value = tx_output.get_value()
                tk.Label(utxo_frame, text=f"• Tx Hash: {utxo.get_tx_hash()[:6]}", bg="white", font=("Arial", 12)).pack(anchor="w", padx=20)
                tk.Label(utxo_frame, text=f"• Index {utxo.get_index()}", bg="white", font=("Arial", 12)).pack(anchor="w", padx=20)
                tk.Label(utxo_frame, text=f"• Tx Address: {addr}", bg="white", font=("Arial", 12)).pack(anchor="w", padx=20)
                tk.Label(utxo_frame, text=f"• Amount {value}", bg="white", font=("Arial", 12)).pack(anchor="w", padx=20)


# Экран создания транзакций
class TxScreen(BaseScreen):
    def __init__(self, parent, app, name, bg_color):
        super().__init__(parent, name, bg_color)
        self.app = app
        self.frame.bind("<Map>", lambda event: self.create_widgets())

    def create_widgets(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        title = tk.Label(self.frame, text="Select recipient address", bg=self.frame["bg"], font=("Arial", 24))
        title.pack(pady=20)

        # Комбобокс для отправителя
        self.sender_object = None
        sender_addresses = list(self.app.addresses.keys())
        self.selected_sender = tk.StringVar()
        self.dropdown_sender = ttk.Combobox(self.frame, textvariable=self.selected_sender,
                                            values=sender_addresses, state="readonly", width=40)
        self.dropdown_sender.pack(pady=10)
        if sender_addresses:
            self.dropdown_sender.set("Select address of sender")
            self.dropdown_sender["state"] = "readonly"
        else:
            self.dropdown_sender["state"] = "disabled"
            self.dropdown_sender.set("No address were created")
        self.dropdown_sender.bind("<<ComboboxSelected>>", self.on_sender_selected)
        # Отслеживаем изменение выбора отправителя
        self.selected_sender.trace("w", self.update_confirm_button_state)

        # Комбобокс для utxo (будет обновлен после выбора отправителя)
        self.input_utxo_object = None
        self.selected_utxo = tk.StringVar()
        self.dropdown_utxo = ttk.Combobox(self.frame, textvariable=self.selected_utxo,
                                          values=[], state="disabled", width=40)
        self.dropdown_utxo.pack(pady=10)
        self.selected_utxo.trace("w", self.update_confirm_button_state)

        # Комбобокс для получателя
        recipient_addresses = list(self.app.addresses.keys())
        self.selected_recipient = tk.StringVar()
        self.dropdown_recipient = ttk.Combobox(self.frame, textvariable=self.selected_recipient,
                                               values=recipient_addresses, state="readonly", width=40)
        self.dropdown_recipient.pack(pady=10)
        if recipient_addresses:
            self.dropdown_recipient.set("Select address send to")
            self.dropdown_recipient["state"] = "readonly"
        else:
            self.dropdown_recipient["state"] = "disabled"
            self.dropdown_recipient.set("No address were created")
        self.selected_recipient.trace("w", self.update_confirm_button_state)

        # Поле для ввода суммы
        vcmd = (self.frame.register(self.is_valid_float), "%P")
        tk.Label(self.frame, text="Enter amount:", bg=self.frame["bg"], font=("Arial", 12)).pack(pady=10)
        self.amount_entry = tk.Entry(self.frame, validate="key", validatecommand=vcmd)
        self.amount_entry.pack(pady=5)
        # Отслеживаем изменения в поле суммы
        self.amount_entry.bind("<KeyRelease>", lambda event: self.update_confirm_button_state())

        # Кнопка подтверждения отправки
        self.confirm_btn = tk.Button(
            self.frame,
            text="Send",
            font=("Arial", 12, "bold"),
            bg="#4caf50", fg="white", activebackground="#45a049",
            relief="flat",
            command=self.confirm_selection
        )
        self.confirm_btn.pack(pady=20)
        self.confirm_btn["state"] = "disabled"  # Изначально кнопка недоступна


    def on_sender_selected(self, event):
        sender = self.selected_sender.get()
        self.sender_object = self.app.addresses[sender]
        input_utxo = self.get_utxo_per_addr(sender)
        self.dropdown_utxo['values'] = list(input_utxo.keys())
        self.selected_utxo.set("")
        if not input_utxo:
            self.dropdown_utxo.set("No utxo for this sender")
            self.dropdown_utxo["state"] = "disabled"
        else:
            self.dropdown_utxo.set("Select the utxo")
            self.dropdown_utxo["state"] = "readonly"


    def get_utxo_per_addr(self, address):
        input_utxo = dict()
        if not self.app.blockchain:
            return input_utxo

        utxo_pool_component = self.app.blockchain.get_utxo_pool_at_max_height()
        for utxo in utxo_pool_component.get_all_utxo():
            tx_output = utxo_pool_component.get_tx_output(utxo)
            addr = RSAHelper().get_short_address(tx_output.get_address())
            if addr == address:
                hash = utxo.get_tx_hash()
                value = tx_output.get_value()
                input_utxo[hash] = value
                self.input_utxo_object = utxo
        return input_utxo

    def update_confirm_button_state(self, *args):
        sender = self.selected_sender.get()
        utxo = self.selected_utxo.get()
        recipient = self.selected_recipient.get()
        amount = self.amount_entry.get().strip()

        if (sender and sender != "Select address of sender" and
                utxo and utxo != "Select the utxo" and
                recipient and recipient != "Select address send to" and
                amount):
            self.confirm_btn["state"] = "normal"
        else:
            self.confirm_btn["state"] = "disabled"

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
            messagebox.showwarning("Tx can not be created", "No addresses were created")
            return

        receiver = self.selected_recipient.get()
        receiver_object = self.app.addresses[receiver]

        sender = self.sender_object

        utxo_hash = self.input_utxo_object.get_tx_hash()
        index = self.input_utxo_object.get_index()
        selected_amnt = self.amount_entry.get()


        tx0 = Transaction()
        tx0.add_input(utxo_hash, index)
        tx0.add_output(1, address=receiver_object.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = sender.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        is_added = self.app.blockchain.transaction_add(tx0)
        if is_added:
            messagebox.showinfo("Success", "Tx was created")
            self.create_widgets()
        else:
            messagebox.showerror("Error", "Tx was not created due some issues")

        print("Create tx:", selected_amnt)


# Основной класс приложения
class MyApp:
    NAME_CREATE_TX = "Create Tx"
    NAME_BLOCKCHAIN = "Blockchain"
    def __init__(self, root):
        self.root = root
        self.root.title("Beautiful Desktop App")
        self.root.geometry("800x500")
        self.root.minsize(800, 500)
        self.root.maxsize(1000, 1000)
        self.root.configure(bg="#f0f4f8")
        # Состояние приложения
        self.addresses = {}
        self.tx_pool = {}
        self.blockchain = None
        self.handle_blocks = None
        self.last_block_procced = None
        self.screens = {}
        # Настройка layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        # Создаём сайдбар
        sidebar_buttons = ["Graphical BC", self.NAME_BLOCKCHAIN, "Addresses", "Txs Pool", "UTXO Pool", self.NAME_CREATE_TX]
        self.sidebar = Sidebar(self.root, sidebar_buttons, self.show_screen)
        # Область для контента
        self.content_area = tk.Frame(self.root, bg="#fafafa")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        # Инициализация экранов
        self.screens["Graphical BC"] = GraphicalBlockchainScreen(self.content_area, self, "Graphical BC", "#ffffff")
        self.screens[self.NAME_BLOCKCHAIN] = BlockchainScreen(self.content_area, self, self.NAME_BLOCKCHAIN, "#c8e6c9")
        self.screens["Addresses"] = AddressScreen(self.content_area, self, "Addresses", "#e0f7fa")
        self.screens["Txs Pool"] = TxPoolScreen(self.content_area, self, "Txs Pool", "#ffe0b2")
        self.screens["UTXO Pool"] = UTXOPoolScreen(self.content_area, self, "UTXO Pool", "#e1bee7")
        self.screens[self.NAME_CREATE_TX] = TxScreen(self.content_area, self, self.NAME_CREATE_TX, "#c8e6c9")
        self.show_screen(self.NAME_BLOCKCHAIN)
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
