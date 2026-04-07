import tkinter as tk
from tkinter import ttk ,messagebox
import re

def make_checkbox(parent, col):
    a = tk.BooleanVar(value=False)
    return tk.Checkbutton(parent, variable=a)
field_types = {
    "entry": lambda parent, col: tk.Entry(parent),
    "select": lambda parent, col: ttk.Combobox(parent, values=col["values"], state="readonly"),
    "checkbox": make_checkbox
}

class editPopup:
    def __init__(self, store):
        self.store = store
        self.selected = self.store.selected
        self.row = self.store.db.fetch_one(self.selected[0])
        if not self.store.selected:
            messagebox.showwarning("Warning", "No rows selected")
            return
        elif len(self.store.selected) > 1:
            messagebox.showwarning("Warning", "Select only one row to edit")
            return
        self.popup = tk.Toplevel()
        self.popup.title("Edit Disk")
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
        self.build_form()
        self.fill_form()

    def build_form(self):
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
    def fill_form(self):
        for data, field in zip(self.row, self.field_widgets):
            if isinstance(field, ttk.Combobox):
                field.set(data)
            elif isinstance(field, tk.Entry):
                field.insert(0, data)
            elif isinstance(field, tk.Checkbutton):
                field.setvar(field["variable"], data)
    def handle_save(self):
        data = {}
        for widget, col in zip(self.field_widgets, self.store.config.get("columns")):
            if isinstance(widget, tk.Checkbutton):
                data[col["title"]] = int(widget.getvar(widget["variable"]))
            else:
                data[col["title"]] = widget.get()
        
        error = self.validate(data)
        if error:
            messagebox.showerror("Error", error)
            return
        self.store.db.update(data, self.selected[0])
        self.store.table.refresh()
        self.popup.destroy()
    def validate(self, data: dict) -> str | None:
        for i, col in enumerate(self.store.config.get("columns")):
            value = data.get(col["title"], "")
            if col.get("required") and not value:
                return f"{col['title']} is required"
            if col.get("pattern") and not re.match(col["pattern"], str(value)):
                return f"{col['title']} has wrong format"
            if col.get("unique") and self.store.db.exists(col["title"], value) and value != self.row[i]:
                return f"{col['title']} already exists"
        return None