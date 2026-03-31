import customtkinter as ctk
import json
import os, sys

def resource_path(rel_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)
def external_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

ctk.set_appearance_mode("System")

class App(ctk.CTk):
    JSON_FILE = external_path("data.json")
    CONFIG_FILE = external_path("config.json")
    def __init__(self):
        super().__init__()
        self.selected_index = None
        self.row_widgets = []
        
        self.title("External Disks Manager")
        self.iconbitmap(resource_path("icon.ico"))
        self.geometry("950x500")
        self.resizable(False, False)

        self.load_config()
        
        self.header = ctk.CTkFrame(self, height=24, corner_radius=0)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)
        self.config_btn = ctk.CTkButton(self.header, corner_radius=0, width=24, text="☰", command=self.config_panel_toggle_handler)
        self.config_btn.pack(side="left", pady=0, padx=0)
        self.title = ctk.CTkLabel(self.header, text="External-Disks-Manager")
        self.title.pack(pady=0, padx=0)
        
        self.body = ctk.CTkFrame(self, corner_radius=0)
        self.body.pack(side="top", fill="both", expand=True)

        self.toolbar = ctk.CTkFrame(self.body, corner_radius=0, width=24)
        self.toolbar.pack(side="left", fill="both", expand=False)
        self.toolbar.pack_propagate(False)
        self.tb_rfrsh_btn = ctk.CTkButton(self.toolbar, corner_radius=0, text="↻", height=24, command=self.refresh_handler)
        self.tb_dlt_btn = ctk.CTkButton(self.toolbar, corner_radius=0, text="✕", height=24, command=self.delete_handler)
        self.tb_edt_btn = ctk.CTkButton(self.toolbar, corner_radius=0, text="✎", height=24)
        for e in self.toolbar.winfo_children():
            e.pack(side="top")

        self.main = ctk.CTkFrame(self.body, corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)
        self.table = ctk.CTkFrame(self.main, corner_radius=0)
        self.table.pack(fill="both", expand=True)
        self.form = ctk.CTkFrame(self.main, corner_radius=0)
        self.form.pack(side="bottom", fill="x")

        self.config_panel = ctk.CTkFrame(self.body, corner_radius=0)
        self.cnfg_pnl_mn = ctk.CTkFrame(self.config_panel, corner_radius=0)
        self.cnfg_pnl_mn.pack(side="top", fill="both", expand=True)
        self.cnfg_pnl_mn.grid_columnconfigure(1, weight=1)
        self.cnfg_pnl_mn_UI_lbl = ctk.CTkLabel(self.cnfg_pnl_mn, text="Appearance")
        self.cnfg_pnl_mn_UI_lbl.grid(row=0, column=0, columnspan=2, sticky="we")
        self.cnfg_pnl_mn_UI_thm_lbl = ctk.CTkLabel(self.cnfg_pnl_mn, text="Theme:")
        self.cnfg_pnl_mn_UI_thm_lbl.grid(row=1, column=0, sticky="w", padx=[10, 0], pady=10)
        self.cnfg_pnl_mn_UI_thm_cb = ctk.CTkComboBox(self.cnfg_pnl_mn, corner_radius=0, values=[f.replace(".json", "") for f in os.listdir("themes") if f.endswith(".json")], state="readonly")
        self.cnfg_pnl_mn_UI_thm_cb.grid(row=1, column=1, sticky="w", padx=[10, 0], pady=10)
        self.cnfg_pnl_btns = ctk.CTkFrame(self.config_panel, corner_radius=0)
        self.cnfg_pnl_btns.pack(side="top", fill="x")
        self.cnfg_pnl_sv = ctk.CTkButton(self.cnfg_pnl_btns, corner_radius=0, text="save", command=self.save_config)
        self.cnfg_pnl_sv.pack(side="right", padx=10, pady=10)

        self.construct_table()
        self.apply_config()    
    #data manipulation
    def load_config(self):
        with open(self.CONFIG_FILE, "r") as f:
            self.config = json.load(f)
        self.CONFIG_CHANGE = False
        self.load_theme()
    def change_config(self):
        nTheme = self.cnfg_pnl_mn_UI_thm_cb.get()
        if nTheme != self.config["theme"]:
            self.CONFIG_CHANGE = True
            self.config["theme"] = nTheme
    def save_config(self):
        self.change_config()
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)
        if self.CONFIG_CHANGE:
            self.load_config()
            self.load_theme()
            self.apply_theme(self.theme)
        self.config_panel.place_forget()
    def apply_config(self):
        self.cnfg_pnl_mn_UI_thm_cb.set(self.config["theme"])
        self.construct_form(self.config["form"], self.form)
        self.apply_theme(self.theme)
    def get_data(self):
        try:
            with open(self.JSON_FILE, "r") as file:
                data = json.load(file)
            self.DATA = data
        except FileNotFoundError:
            self.DATA = []
    def update_data(self):
        with open(self.JSON_FILE, 'w') as f:
            json.dump(self.DATA, f, indent=4)
    def load_theme(self):
        with open(external_path(f"themes/{self.config["theme"]}.json")) as f:
            self.theme = json.load(f)
    #doc manepulation
    def construct_table(self):
        def construct_row(rowObj, index):
            click = lambda e, i=index: self.select_handler(i)
            row = ctk.CTkFrame(self.table, corner_radius=0)
            row.pack(side="top")
            id = ctk.CTkLabel(row, text=rowObj["id"], corner_radius=0, width=48)
            ttype = ctk.CTkLabel(row, text=rowObj["type"], corner_radius=0, width=150)
            title = ctk.CTkLabel(row, text=rowObj["title"], corner_radius=0, width=180)
            description = ctk.CTkLabel(row, text=rowObj["description"], corner_radius=0, width=400)
            if(rowObj["isEncrypted"]):
                enc = ctk.CTkLabel(row, text=f"Encrypted ({rowObj["passwordProtocol"]})", width=148, corner_radius=0)
            else:
                enc = ctk.CTkLabel(row, text="Unlocked", width=148, corner_radius=0,)
            for e in [id, ttype, title, description, enc]:
                e.pack(side="left")
                e.bind("<Button-1>", click)
            self.row_widgets.append(row)
        self.get_data()
        for element in self.table.winfo_children():
            element.destroy()
        thead = ctk.CTkFrame(self.table, corner_radius=0)
        thead.pack(side="top")
        thead_id = ctk.CTkLabel(thead, corner_radius=0, text="ID", width=48)
        thead_type = ctk.CTkLabel(thead, corner_radius=0, text="Type", width=150)
        thead_title = ctk.CTkLabel(thead, corner_radius=0, text="Title", width=180)
        thead_dscrptn = ctk.CTkLabel(thead, corner_radius=0, text="Description", width=400)
        thead_state = ctk.CTkLabel(thead, corner_radius=0, width=148, text="State")
        for e in [thead_id, thead_type, thead_title, thead_dscrptn, thead_state]:
            e.pack(side="left")
        self.row_widgets = []
        self.selected_index = None
        for i, rowObj in enumerate(self.DATA):
            construct_row(rowObj, i)
    def construct_form(self, input_Objs:list, form:ctk.CTkFrame):
        inputs = ctk.CTkFrame(form)
        inputs.pack(fill="x", padx=[0, 12], pady=[12, 12])
        for obj in input_Objs:
            match obj["type"]:
                case "small entry":
                    inpt = ctk.CTkEntry(inputs, width=60, placeholder_text=obj["title"])
                case "medium entry":
                    inpt = ctk.CTkEntry(inputs, width=144, placeholder_text=obj["title"])
                case "large entry":
                    inpt = ctk.CTkEntry(inputs, placeholder_text=obj["title"])
                    inpt.pack(side="left", fill="both", expand=True, padx=[12, 0])
                    continue
                case "select":
                    inpt = ctk.CTkComboBox(inputs, width=144, values=obj["values"])
                    inpt.set(obj["title"])
                case _:
                    continue
            inpt.pack(side="left", padx=[12, 0])
        buttons = ctk.CTkFrame(form)
        buttons.pack(fill="x", padx=[0, 12], pady=[0, 12])
        save_button = ctk.CTkButton(buttons, text="save")
        clear_button = ctk.CTkButton(buttons, text="clear")
        for btn in [save_button, clear_button]:
            btn.pack(side="left", padx=[12, 0], fill="both", expand=True)
    def apply_theme(self, theme:dict):
        self.configure(fg_color=theme["main"]["fg-color"])
        self.header.configure(fg_color=theme["header"]["fg-color"])
        self.title.configure(text_color=theme["header"]["text-color"])
        self.body.configure(fg_color=theme["main"]["fg-color"])
        self.toolbar.configure(fg_color=theme["toolbar"]["fg-color"])
        for tool in self.toolbar.winfo_children():
            tool.configure(fg_color=theme["toolbar"]["tool-fg-color"], hover_color=theme["toolbar"]["tool-hover-color"], text_color=theme["toolbar"]["tool-inner-color"])
        self.main.configure(fg_color=theme["main"]["fg-color"])
        self.table.configure(fg_color=theme["table"]["fg-color"])
        for i, e in enumerate(self.table.winfo_children()):
            if i == 0:
                e.configure(fg_color=theme["table"]["head-fg-color"])
                for chld in e.winfo_children():
                    chld.configure(text_color=theme["table"]["head-text-color"])
            else:
                color = theme["table"]["row-fg-color-2"] if i%2==0 else theme["table"]["row-fg-color-1"]
                e.configure(fg_color=color)
                for k, chld in enumerate(e.winfo_children()):
                    if k == len(e.winfo_children())-1:
                        if self.DATA[i-1]["isEncrypted"]:
                            chld.configure(fg_color=theme["table"]["row-badge-fg-color-true"], text_color=theme["table"]["row-badge-text-color-true"])
                        else:
                            chld.configure(fg_color=theme["table"]["row-badge-fg-color-false"], text_color=theme["table"]["row-badge-text-color-false"])
                    else:
                        chld.configure(text_color=theme["table"]["row-text-color"])
        self.form.configure(fg_color=theme["form"]["fg-color"])
        for section in self.form.winfo_children():
            section.configure(fg_color="transparent")
            for element in section.winfo_children():
                if isinstance(element, ctk.CTkEntry):
                    element.configure(fg_color=theme["form"]["input"]["fg-color"], border_color=theme["form"]["input"]["border-color"], text_color=theme["form"]["input"]["text-color"])
                elif isinstance(element, ctk.CTkComboBox):
                    element.configure(fg_color=theme["form"]["combobox"]["fg-color"], border_color=theme["form"]["combobox"]["border-color"], button_color=theme["form"]["combobox"]["button-color"], text_color=theme["form"]["combobox"]["text-color"])
                elif isinstance(element, ctk.CTkButton):
                    if element.cget("text") == "save":
                        element.configure(fg_color=theme["form"]["button"]["primary-fg-color"], hover_color=theme["form"]["button"]["primary-hover-color"], text_color=theme["form"]["button"]["primary-text-color"])
                    else:
                        element.configure(fg_color=theme["form"]["button"]["secondary-fg-color"], hover_color=theme["form"]["button"]["secondary-hover-color"], text_color=theme["form"]["button"]["secondary-text-color"])
        self.config_btn.configure(fg_color=theme["config-panel"]["open-fg-color"], hover_color=theme["config-panel"]["open-hover-color"], text_color=theme["config-panel"]["open-inner-color"])
        self.config_panel.configure(fg_color=theme["config-panel"]["fg-color"])
        self.cnfg_pnl_mn.configure(fg_color="transparent")
        self.cnfg_pnl_btns.configure(fg_color="transparent")
        self.cnfg_pnl_mn_UI_lbl.configure(fg_color=theme["config-panel"]["title-fg-color"], text_color=theme["config-panel"]["title-text-color"])
        self.cnfg_pnl_mn_UI_thm_lbl.configure(text_color=theme["config-panel"]["label-text-color"])
        self.cnfg_pnl_mn_UI_thm_cb.configure(fg_color=theme["config-panel"]["input-fg-color"], border_color=theme["config-panel"]["input-border-color"], button_color=theme["config-panel"]["input-button-color"], text_color=theme["config-panel"]["input-text-color"])
        self.cnfg_pnl_sv.configure(fg_color=theme["config-panel"]["button-fg-color"], hover_color=theme["config-panel"]["button-hover-color"], text_color=theme["config-panel"]["button-text-color"])
    #event handle
    def change_handler(self):
        if self.form_inpt_isencrptd.get():
            self.form_inpt_pswrdprtcl.pack(side="left", padx=[0, 10], pady=10)
        else:
            self.form_inpt_pswrdprtcl.pack_forget()
    def refresh_handler(self):
        self.construct_table()
        self.apply_theme(self.theme)
    def submit_handler(self):
        obj = {}
        obj["id"] = self.form_inpt_id.get()
        obj["title"] = self.form_inpt_ttl.get()
        obj["type"] = self.form_inpt_type.get()
        if(not obj["id"] or not obj["title"] or obj["type"] == "Type"):
            return
        obj["description"] = self.form_inpt_dscrptn.get() if self.form_inpt_dscrptn.get() else "No Description"
        if self.form_inpt_isencrptd.get():
            obj["isEncrypted"] = True
            obj["passwordProtocol"] = "TP3" if self.form_inpt_pswrdprtcl.get()=="ToPower3" else self.form_inpt_pswrdprtcl.get()
        else:
            obj["isEncrypted"] = False
            obj["passwordProtocol"] = ""
        self.clear_handler()
        self.DATA.append(obj)
        self.update_data()
        self.refresh_handler()
    def clear_handler(self):
        for input in [self.form_inpt_id, self.form_inpt_ttl, self.form_inpt_dscrptn]:
            input.delete(0, "end")
        self.form_inpt_id.configure(placeholder_text="ID")
        self.form_inpt_ttl.configure(placeholder_text="Title")
        self.form_inpt_dscrptn.configure(placeholder_text="Description")
        self.form_inpt_type.set("Type")
        self.form_inpt_isencrptd.deselect()
        self.change_handler()
        self.form_inpt_pswrdprtcl.set("Password Protocol")
    def select_handler(self, index):
        if self.selected_index is not None:
            color = self.theme["table"]["row-fg-color-1"] if self.selected_index%2==0 else self.theme["table"]["row-fg-color-2"]
            self.row_widgets[self.selected_index].configure(fg_color=color)
        self.selected_index = index
        self.row_widgets[index].configure(fg_color=self.theme["table"]["row-fg-color-selected"])
    def delete_handler(self):
        if self.selected_index is None:
            return
        del self.DATA[self.selected_index]
        self.update_data()
        self.refresh_handler()
    def config_panel_toggle_handler(self):
        if self.config_panel.winfo_ismapped():
            self.config_panel.place_forget()
        else:
            self.config_panel.place(x=0, y=0, relwidth=1, relheight=1)

if __name__ == "__main__":
    app = App()
    app.mainloop()