import tkinter as tk
from tkinter import ttk
from models.tools import Tools
from models.tools import ToolTip
from models.table import Table
from windows.config_popup import configPopup
from core.store import Store


class MainWindow:
    def __init__(self, root:tk.Tk):
        self.store = Store(root)
        self.root = root
        self.root.title("DiskLog")
        
        tk.Frame(self.root, height=1, bg="#CCCCCC").pack(side="top", fill="x", padx=12, pady=[12, 0])

        self.head = tk.Frame(self.root)
        self.head.pack(side="top", fill="x", padx=14, pady=6)
        tk.Button(self.head, text="\u2630", command = lambda: configPopup(self.store)).pack(side="left", padx=[0, 6])
        tk.Frame(self.head, width=1, bg="#CCCCCC").pack(side="left", fill="y", padx=6)
        self.search = tk.Frame(self.head)
        self.search.pack(side="left", fill="both", expand=True)
        tk.Label(self.search, text="Search:").pack(side="left", padx=[6, 6])
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.table.refresh(self.search_var.get()))
        self.search_bar = tk.Entry(self.search, textvariable=self.search_var)
        self.search_bar.pack(side="left", fill="x", expand=True, padx=[0, 6])
        tk.Frame(self.head, width=1, bg="#CCCCCC").pack(side="left", fill="y", padx=6)
        self.tools = Tools(self.head, self.store)
        self.tools.pack(side="right")
        
        tk.Frame(self.root, height=1, bg="#CCCCCC").pack(side="top", fill="x", padx=12)

        self.table = Table(self.root, self.store)
        self.table.pack(side="top", fill="both", expand=True, padx=[14, 0], pady=[6, 24])
