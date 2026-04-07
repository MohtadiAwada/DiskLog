import tkinter as tk
from tkinter import ttk

class Table:
    def __init__(self, parent:tk.Frame, store):
        self.store = store
        self.frame = tk.Frame(parent)

        cols = [col["title"] for col in self.store.config.get("columns")]
        self.tree = ttk.Treeview(self.frame, columns=cols+["_id"], show="headings", selectmode="extended")
        for col in self.store.config.get("columns"):
            self.tree.heading(col["title"], text=col["title"])
            self.tree.column(col["title"], width=col.get("width", 100), anchor="center")
        self.tree.column("_id", width=0, stretch=False)
        self.tree.heading("_id", text="")

        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview, width=14)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.store.table = self
        self.tree.bind("<<TreeviewSelect>>", self.select_handler)
        self.refresh()
    def refresh(self, query: str = ""):
        self.tree.delete(*self.tree.get_children())
        for row in self.store.db.search(query):
            self.tree.insert("", "end", values=row)
    def select_handler(self, event):
        selected = self.tree.selection()
        self.store.selected = [self.tree.item(item)["values"][-1] for item in selected]
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)