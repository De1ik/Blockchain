import tkinter as tk
from BaseScreen import BaseScreen


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

