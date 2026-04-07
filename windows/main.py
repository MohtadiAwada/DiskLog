import tkinter as tk
from tkinter import ttk
from models.tools import Tools
from windows.table import Table
from core.store import Store

store = Store()
class MainWindow:
    def __init__(self, root:tk.Tk):
        self.root = root
        self.root.title("DiskLog")
        
        tk.Frame(self.root, height=1, bg="#CCCCCC").pack(side="top", fill="x", padx=12, pady=[12, 0])

        self.head = tk.Frame(self.root)
        self.head.pack(side="top", fill="x", padx=14, pady=6)
        self.search = tk.Frame(self.head)
        self.search.pack(side="left")
        tk.Label(self.search, text="Search:").pack(side="left", padx=[0, 6])
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.table.refresh(self.search_var.get()))
        self.search_bar = tk.Entry(self.search, textvariable=self.search_var)
        self.search_bar.pack(side="left")
        self.tools = Tools(self.head, store)
        self.tools.pack(side="right")
        
        tk.Frame(self.root, height=1, bg="#CCCCCC").pack(side="top", fill="x", padx=12)

        self.table = Table(self.root, store)
        self.table.pack(side="top", fill="both", expand=True, padx=[14, 0], pady=[6, 24])
