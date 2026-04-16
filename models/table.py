import tkinter as tk
from tkinter import ttk

class Table:
    def __init__(self, parent:tk.Frame, heads, data, store):
        self.store = store
        self.frame = tk.Frame(parent)

        cols = [col["title"] for col in heads]
        self.table = ttk.Treeview(self.frame, columns=cols+["_id"], show="headings", selectmode="extended")
        for col in heads:
            self.table.heading(col["title"], text=col["title"])
            self.table.column(col["title"], width=col.get("width", 100), anchor="center")
        self.table.column("_id", width=0, stretch=False)
        self.table.heading("_id", text="")

        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.table.yview, width=14)
        self.table.configure(yscrollcommand=self.scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.refresh(data)
    def refresh(self, data):
        self.table.delete(*self.table.get_children())
        for row in data:
            self.table.insert("", "end", values=row)
    def get_selected(self):
        return [self.table.item(item)["values"][-1] for item in self.table.selection()]
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)