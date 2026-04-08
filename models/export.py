import csv, sqlite3
import threading
import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from pathlib import Path

class Export:
    def __init__(self, store):
        self.store = store
        messagebox.showinfo("Export Visible Data", "Only the visible data in the table will be exported.")
        self.popup = tk.Toplevel()
        #self.popup.geometry("200x200")
        self.popup.overrideredirect(True)
        self.popup.update_idletasks()

        root = self.popup.master
        x = root.winfo_rootx() + root.winfo_width()//2 - self.popup.winfo_width()//2
        y = root.winfo_rooty() + root.winfo_height()//2 - self.popup.winfo_height()//2
        self.popup.geometry(f"+{x}+{y}")

        self.popup.resizable(False, False)
        self.popup.grab_set()
        self.popup.focus_set()
        self.popup.bind("<Escape>", lambda e: self.popup.destroy())

        tk.Label(self.popup, text="Export").pack(side="top", pady=12)
        tk.Frame(self.popup, height=1, bg="#CCCCCC").pack(side="top", fill="x", padx=12, pady=[0, 6])
        name_frame = tk.Frame(self.popup)
        name_frame.pack(side="top", fill="x", padx=14, pady=[0, 6])
        tk.Label(name_frame, text="File Name:").pack(side="left", padx=[0, 6])
        self.file_name = tk.Entry(name_frame)
        self.file_name.pack(side="left", fill="x", expand=True)
        location_frame = tk.Frame(self.popup)
        location_frame.pack(side="top", fill="x", padx=14, pady=[0, 6])
        tk.Label(location_frame, text="Location:").pack(side="left", padx=[0, 6])
        self.file_location = tk.Entry(location_frame)
        self.file_location.pack(side="left", fill="x", expand=True)
        tk.Button(location_frame, text="\u2398", command=self.select_dir).pack(side="left", padx=[3, 0])
        type_frame = tk.Frame(self.popup)
        type_frame.pack(side="top", fill="x", padx=14, pady=[0, 6])
        tk.Label(type_frame, text="Export to:").pack(side="left", padx=[0, 6])
        self.file_type = ttk.Combobox(type_frame, values=["Table Sheet", "Database File"], state="readonly")
        self.file_type.set("Table Sheet")
        self.file_type.pack(side="left")
        tk.Frame(self.popup, height=1, bg="#CCCCCC").pack(side="top", fill="x", padx=12)
        tk.Button(self.popup, text="Export", command=self.handle_save).pack(side="top", fill="x", expand=True, padx=14, pady=[6, 0])
        tk.Button(self.popup, text="Cancel", command=self.popup.destroy).pack(side="top", fill="x", expand=True, padx=14, pady=[6, 12])

    def select_dir(self):
        file_dir = filedialog.askdirectory(title="Export", initialdir=Path.cwd())
        self.file_location.delete(0, "end")
        self.file_location.insert(0, file_dir)

    def handle_save(self):
        for input in [self.file_location, self.file_name]:
            if not input.get():
                messagebox.showwarning("Unvalid Input", "All fields are required.")
                return
        if not os.path.exists(self.file_location.get()):
            messagebox.showwarning("Unvalid File Location", "the directory doesn't exits. please enter a valid path")
            return
        self.file_path = os.path.join(self.file_location.get(), self.file_name.get())
        if Path(self.file_path).exists():
            if not messagebox.askyesno("File Exits", "this file already exists.\nDo you want to replace it."):
                return
        data = []
        all_table = self.store.table.tree.get_children()
        fieldnames = [col["title"] for col in self.store.config.get("columns")]
        for item in all_table:
            row = {}
            for key, value in zip(fieldnames, self.store.table.tree.item(item)['values']):
                row[key] = value
            data.append(row)
        if self.file_type.get() == "Table Sheet":
            self.export_csv(fieldnames, data)
        else:
            self.export_db(fieldnames, data)
        self.popup.destroy()

    def export_csv(self, fieldnames, data):
        with open(self.file_path + ".csv", mode="w", newline="") as exp_file:
            writer = csv.DictWriter(exp_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def export_db(self, fieldnames, data):
        conn = sqlite3.connect(self.file_path + ".db")
