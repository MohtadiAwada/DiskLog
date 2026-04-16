import tkinter as tk
from tkinter import ttk, messagebox
from windows.add_popup import addPopup
from windows.edit_popup import editPopup

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tooltip:
            return
        
        # Create a temporary hidden window to calculate required size
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.withdraw() 
        
        lbl = tk.Label(self.tooltip, text=self.text, padx=6, pady=3)
        lbl.pack()
        
        # Force geometry calculation
        self.tooltip.update_idletasks()
        
        tip_width = self.tooltip.winfo_reqwidth()
        tip_height = self.tooltip.winfo_reqheight()
        
        # Get widget dimensions and position
        w_x = self.widget.winfo_rootx()
        w_y = self.widget.winfo_rooty()
        w_width = self.widget.winfo_width()
        w_height = self.widget.winfo_height()

        # Calculate X: Center the tooltip horizontally relative to the widget
        x = w_x + (w_width // 2) - (tip_width // 2)
        
        # Calculate Y: Default to appearing UNDER the widget
        y = w_y + w_height + 2
        
        # Screen constraints
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        
        # Boundary Check - Horizontal (Keep it on screen)
        if x < 0:
            x = 0
        elif x + tip_width > screen_width:
            x = screen_width - tip_width

        # Boundary Check - Vertical (Flip ABOVE if it goes off bottom)
        if y + tip_height > screen_height:
            y = w_y - tip_height - 2

        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.tooltip.deiconify()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
class Tools:
    def __init__(self, parent, store):
        self.store = store
        self.tools = [
            {
                "name": "Add",
                "sign": "\u002B",
                "command": lambda: addPopup(self.store)
            },
            {
                "name": "Delete",
                "sign": "\u2715",
                "command": self.delete_handler
            },
            {
                "name": "Edit",
                "sign": "\u270e",
                "command": lambda: editPopup(self.store)
            }
        ]
        self.frame = tk.Frame(parent)
        self.load_tools()
    def load_tools(self):
        for tool in self.tools:
            btn = tk.Button(self.frame, text=tool["sign"], command=tool["command"])
            btn.pack(side="right", padx=[6, 0])
            ToolTip(btn, tool["name"])
    def delete_handler(self):
        if not self.store.data_table.get_selected():
            messagebox.showwarning("Warning", "No rows selected")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(self.store.data_table.get_selected())} entry?"):
            return
        for id_val in self.store.data_table.get_selected():
            self.store.db.delete(id_val)
        self.store.data_table.refresh(self.store.db.search(""))
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)