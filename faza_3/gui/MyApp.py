import tkinter as tk
from .AddressScreen import AddressScreen
from .BlockchainScreen import BlockchainScreen
from .GraphicalBlockchainScreen import GraphicalBlockchainScreen
from .Sidebar import Sidebar
from .TxPoolScreen import TxPoolScreen
from .TxScreen import TxScreen
from .UTXOPoolScreen import UTXOPoolScreen


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

