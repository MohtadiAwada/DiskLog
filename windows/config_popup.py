import tkinter as tk
import json
from tkinter import messagebox

class configPopup:
    def __init__(self, store):
        self.store = store
        self.popup = tk.Toplevel()
        self.popup.title("Change Configuration")
        self.popup.update_idletasks()
        root = self.popup.master
        x = root.winfo_rootx() + root.winfo_width()//2 - self.popup.winfo_width()//2
        y = root.winfo_rooty() + root.winfo_height()//2 - self.popup.winfo_height()//2
        self.popup.geometry(f"+{x}+{y}")
        self.popup.grab_set()
        self.popup.focus_set()
        self.build_form()
    def build_form(self):
        textarea_frame=tk.Frame(self.popup)
        textarea_frame.pack(side="top", fill="both", expand=True, padx=12, pady=12)
        self.textarea = tk.Text(textarea_frame)
        self.textarea.pack(fill="both", expand=True)
        self.textarea.insert(0.0, self.store.config.load_raw())
        button_frame = tk.Frame(self.popup)
        button_frame.pack(side="top", fill="x", padx=12, pady=[0, 24])
        tk.Button(button_frame, text="save", command=self.handle_save).pack(side="right")
        tk.Button(button_frame, text="cancel", command=self.handle_cancel).pack(side="left")
        tk.Button(button_frame, text="reset", command=self.handle_reset).pack(side="left", padx=6)
    def handle_save(self):
        try:
            data = json.loads(self.textarea.get(0.0, tk.END))
        except json.decoder.JSONDecodeError as e:
            messagebox.showerror("Invalid JSON", f"Could not save. Error: \n{str(e)}")
            return
        error = self.store.config.validate(data)
        if error:
            messagebox.showwarning("Config error", error)
            return
        if data == self.store.config.CONFIG:
            self.popup.destroy()
            return
        if not messagebox.askyesno("Confirm", "Change configuration? You cannot undo this action.\nThe app will close automatically after saving."):
            return
        self.store.config.save(data)
        self.popup.destroy()
        self.store.root.destroy()
    def handle_cancel(self):
        if self.textarea.get(0.0, tk.END).strip() != self.store.config.load_raw().strip():
            messagebox.showwarning("Unsaved changes", "The changes you made will not be saved")
            self.popup.destroy()
        self.popup.destroy()
    def handle_reset(self):
        default = self.store.config.DEFAULT
        if self.textarea.get(0.0, tk.END).strip() == json.dumps(default, indent=4).strip():
            return
        if not messagebox.askyesno("Confirm reset", "Reset configuration to default? This action cannot be undone."):
            return
        self.textarea.delete(0.0, tk.END)
        self.textarea.insert(0.0, json.dumps(self.store.config.DEFAULT, indent=4))