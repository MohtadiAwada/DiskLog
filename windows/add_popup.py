import tkinter as tk
from tkinter import ttk, messagebox
import re

def make_checkbox(parent, col):
    a = tk.BooleanVar(value=False)
    checkbox = tk.Checkbutton(parent, variable=a)
    checkbox.var = a  # Store variable as widget attribute
    return checkbox
field_types = {
    "entry": lambda parent, col: tk.Entry(parent),
    "select": lambda parent, col: ttk.Combobox(parent, values=col["values"], state="readonly"),
    "checkbox": make_checkbox
}

class addPopup:
    def __init__(self, store):
        self.store = store
        self.popup = tk.Toplevel()
        self.popup.title("Add Disk")
        self.popup.update_idletasks()

        root = self.popup.master
        x = root.winfo_rootx() + root.winfo_width()//2 - self.popup.winfo_width()//2
        y = root.winfo_rooty() + root.winfo_height()//2 - self.popup.winfo_height()//2
        self.popup.geometry(f"+{x}+{y}")

        self.popup.resizable(True, False)
        self.popup.minsize(self.popup.winfo_width(), self.popup.winfo_height())
        self.popup.grab_set()
        self.popup.focus_set()

        self.field_widgets = []
        self.build_from()

    def build_from(self):
        for col in self.store.config.get("columns"):
            frame = tk.Frame(self.popup)
            frame.pack(side="top", fill='x', pady=[6, 0], padx=[0, 12])
            tk.Label(frame, text=col["title"]+":").pack(side="left", padx=[12, 6])
            field = field_types[col["type"]](frame, col)
            if isinstance(field, tk.Entry):
                field.pack(side="left", fill="both", expand=True)
            else:
                field.pack(side="left")
            self.field_widgets.append(field)
        frame = tk.Frame(self.popup)
        frame.pack(side="top", fill="x", pady=12, padx=12)
        tk.Button(frame, text="save", command=self.handle_save).pack(side="right")
        tk.Button(frame, text="cancel", command=self.popup.destroy).pack(side="left")
    def handle_save(self):
        data = {}
        for widget, col in zip(self.field_widgets, self.store.config.get("columns")):
            if isinstance(widget, tk.Checkbutton):
                data[col["title"]] = int(widget.var.get())
            else:
                data[col["title"]] = widget.get()
        
        error = self.validate(data)
        if error:
            messagebox.showerror("Error", error)
            return
        self.store.db.insert(data)
        self.store.data_table.refresh(self.store.db.search(""))
        self.popup.destroy()
    def validate(self, data: dict) -> str | None:
        for col in self.store.config.get("columns"):
            value = data.get(col["title"], "")
            if col.get("required") and not value:
                return f"{col['title']} is required"
            if col.get("pattern") and not re.match(col["pattern"], str(value)):
                return f"{col['title']} has wrong format"
            if col.get("unique") and self.store.db.exists(col["title"], value):
                return f"{col['title']} already exists"
        return None