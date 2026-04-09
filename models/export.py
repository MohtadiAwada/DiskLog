import csv, sqlite3
import re
import threading
import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from pathlib import Path

class Export:
    DB_RESERVED = {
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", 
        "CREATE", "TABLE", "DATABASE", "INDEX", "VIEW", "TRIGGER", 
        "FROM", "WHERE", "JOIN", "AS", "ON", "INTO", "VALUES", 
        "GRANT", "REVOKE", "PRIMARY", "KEY", "USER"
    }
    DB_REGEX = r"^[a-zA-Z][a-zA-Z0-9_]{0,63}$"
    FILENAME_REGEX = r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,254}$"
    def __init__(self, store):
        self.store = store
        messagebox.showinfo("Export Visible Data", "Only the visible data in the table will be exported.")
        self.popup = tk.Toplevel()
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
        input_frame = tk.Frame(self.popup)
        input_frame.pack(side="top")
        name_frame = tk.Frame(input_frame)
        name_frame.pack(side="top", fill="x", padx=14, pady=[0, 6])
        tk.Label(name_frame, text="File Name:").pack(side="left", padx=[0, 6])
        self.file_name = tk.Entry(name_frame)
        self.file_name.pack(side="left", fill="x", expand=True)
        location_frame = tk.Frame(input_frame)
        location_frame.pack(side="top", fill="x", padx=14, pady=[0, 6])
        tk.Label(location_frame, text="Location:").pack(side="left", padx=[0, 6])
        self.file_location = tk.Entry(location_frame)
        self.file_location.pack(side="left", fill="x", expand=True)
        tk.Button(location_frame, text="\u2398", command=self.select_dir).pack(side="left", padx=[3, 0])
        type_frame = tk.Frame(input_frame)
        type_frame.pack(side="top", fill="x", padx=14, pady=[0, 6])
        tk.Label(type_frame, text="Export to:").pack(side="left", padx=[0, 6])
        self.file_type = ttk.Combobox(type_frame, values=["Table Sheet", "Database File"], state="readonly")
        self.file_type.set("Table Sheet")
        self.file_type.bind("<<ComboboxSelected>>", self.change_input)
        self.file_type.pack(side="left")
        self.db_data_frame = tk.Frame(input_frame)
        table_name_frame = tk.Frame(self.db_data_frame)
        table_name_frame.pack(side="top", fill="x", padx=14, pady=[0, 6])
        tk.Label(table_name_frame, text="Table Name:").pack(side="left", padx=[0, 6])
        self.table_name = tk.Entry(table_name_frame)
        self.table_name.pack(side="left", fill="x", expand=True)
        primary_key_frame = tk.Frame(self.db_data_frame)
        primary_key_frame.pack(side="top", fill="x", padx=14, pady=[0, 6])
        tk.Label(primary_key_frame, text="Primary Key:").pack(side="left", padx=[0, 6])
        self.table_primarykey = tk.Entry(primary_key_frame)
        self.table_primarykey.pack(side="left", fill="x", expand=True)
        tk.Frame(self.popup, height=1, bg="#CCCCCC").pack(side="top", fill="x", padx=12)
        tk.Button(self.popup, text="Export", command=self.handle_save).pack(side="top", fill="x", expand=True, padx=14, pady=[6, 0])
        tk.Button(self.popup, text="Cancel", command=self.popup.destroy).pack(side="top", fill="x", expand=True, padx=14, pady=[6, 12])

    def select_dir(self):
        file_dir = filedialog.askdirectory(title="Export", initialdir=Path.cwd())
        self.file_location.delete(0, "end")
        self.file_location.insert(0, file_dir)
    
    def change_input(self, event):
        if self.file_type.get() == "Database File":
            self.db_data_frame.pack(side="top", fill="x")
        else:
            self.db_data_frame.pack_forget()

    def handle_save(self):
        for input in [self.file_location, self.file_name]:
            if not input.get():
                messagebox.showwarning("Invalid Input", "All fields are required.")
                return
        if not re.fullmatch(self.FILENAME_REGEX, self.file_name.get()):
            messagebox.showwarning("Invalid Value", f"'{self.file_name.get()}' is an invalid value!\nPlease enter a valid value.")
            return
        if not os.path.exists(self.file_location.get()):
            messagebox.showwarning("Invalid File Location", "The directory doesn't exist. Please enter a valid path.")
            return
        self.file_path = os.path.join(self.file_location.get(), self.file_name.get())
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
            self.export_db(data)

    def export_csv(self, fieldnames, data):
        if Path(self.file_path + ".csv").exists():
            if not messagebox.askyesno("File Exists", "This file already exists!\nDo you want to replace it?"):
                return
        with open(self.file_path + ".csv", mode="w", newline="") as exp_file:
            writer = csv.DictWriter(exp_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        self.popup.destroy()

    def export_db(self, data):
        if Path(self.file_path + ".db").exists():
            if messagebox.askyesno("File Exists", "This file already exists!\nDo you want to replace it?"):
                os.remove(self.file_path + ".db")
            else:
                return
        cols = self.store.config.get("columns").copy()
        for col in cols: col["title"] = col["title"].replace(" ", "_")
        name = self.table_name.get()
        primarykey = self.table_primarykey.get()
        for input in [name, primarykey]:
            if not input:
                messagebox.showwarning("Invalid Input", "All fields are required.")
                return
            if not re.fullmatch(self.DB_REGEX, input):
                messagebox.showwarning("Invalid Value", f"'{input}' is an invalid value!\nPlease enter a valid value.")
                return
            if input.upper() in self.DB_RESERVED:
                messagebox.showwarning("Invalid Value", f"'{input}' is a reserved word!\nPlease enter a valid value.")
                return
        if primarykey.lower() in [x["title"].lower() for x in cols]:
            messagebox.showwarning("Invalid Primary Key", "You cannot use a column title as a primary key.")
            return
        conn = sqlite3.connect(self.file_path + ".db")
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} ({primarykey} INTEGER PRIMARY KEY AUTOINCREMENT)")
        conn.commit()
        for col in cols:
            cursor.execute(f"ALTER TABLE {name} ADD COLUMN {col["title"]} {col["db_type"]}")
            conn.commit()
            print(col["title"])
        placeholders = ", ".join(["?" for _ in cols])
        for row in data:
            cursor.execute(f"INSERT INTO {name} ({", ".join([x["title"] for x in cols])}) VALUES ({placeholders})", tuple(row.values()))
            conn.commit()
        self.popup.destroy()