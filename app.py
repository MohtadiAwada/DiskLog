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
        self.SELECTED = None
        self.ROWS = []
        
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

        self.config_panel = self.construct_configPanel(self.body, self.CONFIG)

        self.render_data()
        self.apply_config()    
    #data manipulation
    def load_config(self):
        def load_theme(theme_name:str):
            with open(external_path(f"themes/{theme_name}.json")) as theme_file:
                self.theme = json.load(theme_file)
        with open(self.CONFIG_FILE, "r") as config_file:
            self.CONFIG = json.load(config_file)
        self.CONFIG_CHANGE = False
        load_theme(self.CONFIG["Appearance"]["Theme"])
    def change_config(self):
        nTheme = self.cnfg_pnl_mn_UI_thm_cb.get()
        if nTheme != self.CONFIG["Appearance"]["Theme"]:
            self.CONFIG_CHANGE = True
            self.CONFIG["Appearance"]["Theme"] = nTheme
    def save_config(self):
        self.change_config()
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.CONFIG, f, indent=4)
        if self.CONFIG_CHANGE:
            self.load_config()
            self.apply_config()
        self.config_panel.place_forget()
    def apply_config(self):
        #self.cnfg_pnl_mn_UI_thm_cb.set(self.CONFIG["Appearance"]["Theme"])
        self.construct_form(self.CONFIG["Data Entry"], self.form)
        self.apply_theme(self.theme)
    def load_data(self):
        try:
            with open(self.JSON_FILE, "r") as file:
                self.DATA = json.load(file)
        except FileNotFoundError:
            self.DATA = []
    def save_data(self):
        with open(self.JSON_FILE, 'w') as f:
            json.dump(self.DATA, f, indent=4)
        self.render_data()
    def render_data(self):
        self.load_data()
        self.ROWS = self.construct_table(self.table, self.DATA)
        self.SELECTED = None
    #doc manepulation
    def construct_configPanel(self, parent:ctk.CTkFrame, config:dict) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(parent)
        main = ctk.CTkFrame(panel)
        main.pack(side="top", fill="x")
        for title, section in config.items():
            ttl = ctk.CTkLabel(main, text=title)
            ttl.pack(side="top", fill="x")
            if title == "Appearance":
                sec = ctk.CTkFrame(main)
                sec.grid_columnconfigure(1, weight=1)
                for index, (label, value) in enumerate(section.items()):
                    lbl = ctk.CTkLabel(sec, text=label+":")
                    lbl.grid(row=index, column=0, padx=[12, 6])
                    val = ctk.CTkLabel(sec, text=value) #temp
                    val.grid(row=index, column=1, sticky="w")
            elif title == "Data Entry":
                sec = ctk.CTkFrame(main)
                sec.grid_columnconfigure(2, weight=1)
                for row, item in enumerate(section):
                    for index, (label, value) in enumerate(item.items()):
                        frame = ctk.CTkFrame(sec)
                        frame.grid(row=row, column=index, sticky="w")
                        lbl = ctk.CTkLabel(frame, text=label+":")
                        lbl.pack(side="left", padx=[12, 6])
                        val = ctk.CTkLabel(frame, text=", ".join(value) if isinstance(value, list) else value)
                        val.pack(side="left")
                    edit = ctk.CTkButton(sec, text="✎", width=24, command=lambda r=row, s=sec: self.config_dataEntry_edit_handler(r, s))
                    edit.grid(row=row, column=3, padx=12)
            sec.pack(side="top", fill="x")
        button_frame = ctk.CTkFrame(panel)
        button_frame.pack(side="bottom", fill="x")
        save_button = ctk.CTkButton(button_frame, text="save")
        save_button.pack(side="right", padx=12, pady=12)
        return panel
    def construct_table(self, table:ctk.CTkFrame, data:dict) -> list[ctk.CTkFrame]:
        def construct_row(rowObj:dict, index:int):
            click = lambda e, i=index: self.select_handler(i)
            row = ctk.CTkFrame(table, corner_radius=0)
            row.pack(side="top")
            id = ctk.CTkLabel(row, text=rowObj["ID"], corner_radius=0, width=48)
            ttype = ctk.CTkLabel(row, text=rowObj["Type"], corner_radius=0, width=150)
            title = ctk.CTkLabel(row, text=rowObj["Title"], corner_radius=0, width=180)
            description = ctk.CTkLabel(row, text=rowObj["Description"], corner_radius=0, width=400)
            if(rowObj["isEncrypted"]):
                enc = ctk.CTkLabel(row, text=f"Encrypted ({rowObj["passwordProtocol"]})", width=148, corner_radius=0)
            else:
                enc = ctk.CTkLabel(row, text="Unlocked", width=148, corner_radius=0,)
            for e in [id, ttype, title, description, enc]:
                e.pack(side="left")
                e.bind("<Button-1>", click)
            rows_widget.append(row)
        rows_widget = []
        for element in table.winfo_children():
            element.destroy()
        thead = ctk.CTkFrame(table, corner_radius=0)
        thead.pack(side="top")
        thead_id = ctk.CTkLabel(thead, corner_radius=0, text="ID", width=48)
        thead_type = ctk.CTkLabel(thead, corner_radius=0, text="Type", width=150)
        thead_title = ctk.CTkLabel(thead, corner_radius=0, text="Title", width=180)
        thead_dscrptn = ctk.CTkLabel(thead, corner_radius=0, text="Description", width=400)
        thead_state = ctk.CTkLabel(thead, corner_radius=0, width=148, text="State")
        for e in [thead_id, thead_type, thead_title, thead_dscrptn, thead_state]:
            e.pack(side="left")
        for i, rowObj in enumerate(data):
            construct_row(rowObj, i)
        return rows_widget
    def construct_form(self, input_Objs:list, form:ctk.CTkFrame):
        for element in form.winfo_children():
            element.destroy()
        inputs = ctk.CTkFrame(form)
        inputs.pack(fill="x", padx=[0, 12], pady=[12, 12])
        for obj in input_Objs:
            match obj["Type"]:
                case "small entry":
                    inpt = ctk.CTkEntry(inputs, width=60, placeholder_text=obj["Title"])
                case "medium entry":
                    inpt = ctk.CTkEntry(inputs, width=144, placeholder_text=obj["Title"])
                case "large entry":
                    inpt = ctk.CTkEntry(inputs, placeholder_text=obj["Title"])
                    inpt.pack(side="left", fill="both", expand=True, padx=[12, 0])
                    continue
                case "select":
                    inpt = ctk.CTkComboBox(inputs, width=144, values=obj["Values"], state="readonly")
                    inpt.set(obj["Title"])
                case _:
                    continue
            inpt.pack(side="left", padx=[12, 0])
        buttons = ctk.CTkFrame(form)
        buttons.pack(fill="x", padx=[0, 12], pady=[0, 12])
        save_button = ctk.CTkButton(buttons, text="save", command=self.form_submit_handler)
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
        for i, part in enumerate(self.config_panel.winfo_children()):
            if i == 0:
                part.configure(fg_color="transparent")
                for element in part.winfo_children():
                    if isinstance(element, ctk.CTkLabel):
                        element.configure(fg_color=theme["config-panel"]["title-fg-color"], text_color=theme["config-panel"]["title-text-color"])
                    else:
                        element.configure(fg_color="transparent")
                        for children in element.winfo_children():
                            if isinstance(children, ctk.CTkFrame):
                                children.configure(fg_color="transparent")
                                for child in children.winfo_children():
                                    child.configure(text_color=theme["config-panel"]["label-text-color"])
                            elif isinstance(children, ctk.CTkButton):
                                children.configure(fg_color=theme["toolbar"]["tool-fg-color"], hover_color=theme["toolbar"]["tool-hover-color"], text_color=theme["toolbar"]["tool-inner-color"])
                            else:
                                children.configure(text_color=theme["config-panel"]["label-text-color"])
            else:
                part.configure(fg_color="transparent")
                for button in part.winfo_children():
                    button.configure(fg_color=theme["config-panel"]["button-fg-color"], hover_color=theme["config-panel"]["button-hover-color"], text_color=theme["config-panel"]["button-text-color"])
    #event handle
    def change_handler(self):
        if self.form_inpt_isencrptd.get():
            self.form_inpt_pswrdprtcl.pack(side="left", padx=[0, 10], pady=10)
        else:
            self.form_inpt_pswrdprtcl.pack_forget()
    def refresh_handler(self):
        self.render_data()
        self.apply_theme(self.theme)
    def form_submit_handler(self):
        inputs = self.form.winfo_children()[0]
        data_dict = {}
        for index, input in enumerate(inputs.winfo_children()):
            if isinstance(input, ctk.CTkEntry):
                match self.CONFIG["Data Entry"][index]["Class"]:
                    case "String":
                        if not input.get():
                            self.error("missing value")
                            return
                    case "ID":
                        IDs = list(map(lambda obj: obj["ID"], self.DATA))
                        if input.get() in IDs:
                            self.error("existing id")
                            return
                        elif not input.get().isdigit():
                            self.error("wrong type")
                            return
            elif isinstance(input, ctk.CTkComboBox):
                if input.get()==self.CONFIG["Data Entry"][index]["Title"]:
                    self.error("missing value")
                    return
            data_dict[self.CONFIG["Data Entry"][index]["Title"]] = input.get()
        self.DATA.append(data_dict)
        self.save_data()
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
        if self.SELECTED is not None:
            color = self.theme["table"]["row-fg-color-1"] if self.SELECTED%2==0 else self.theme["table"]["row-fg-color-2"]
            self.ROWS[self.SELECTED].configure(fg_color=color)
        self.SELECTED = index
        self.ROWS[index].configure(fg_color=self.theme["table"]["row-fg-color-selected"])
    def delete_handler(self):
        if self.SELECTED is None:
            return
        del self.DATA[self.SELECTED]
        self.save_data()
        self.refresh_handler()
    def config_panel_toggle_handler(self):
        if self.config_panel.winfo_ismapped():
            self.config_panel.place_forget()
        else:
            self.config_panel.place(x=0, y=0, relwidth=1, relheight=1)
    def config_dataEntry_edit_handler(self, row:int, section:ctk.CTkFrame):
        button = section.grid_slaves(row=row, column=3)[0]
        button.configure(text="✓", command=lambda: self.config_dataEntry_submit_handler(row, section))
        columns = []
        for c in range(3):
            slaves = section.grid_slaves(row=row, column=c)
            if slaves:
                columns.append(slaves[0])
        for element in columns:
            for i, lbl in enumerate(element.winfo_children()):
                if i == 0:
                    continue
                else:
                    lbl.pack_forget()
                    change = ctk.CTkEntry(element)
                    change.insert(0, lbl.cget("text"))
                    change.pack(side="left")
    def config_dataEntry_submit_handler(self, row:int, section:ctk.CTkFrame):
        button = section.grid_slaves(row=row, column=3)[0]
        button.configure(text="✎", command=lambda: self.config_dataEntry_edit_handler(row, section))
        columns = []
        for c in range(3):
            slaves = section.grid_slaves(row=row, column=c)
            if slaves:
                columns.append(slaves[0])
        for element in columns:
            children = element.winfo_children()
            lbl = children[1]   # the label (index 0)
            entry = children[2] # the entry (index 1, created after pack_forget)
            if len(children) > 1 and isinstance(children[2], ctk.CTkEntry):
                lbl.configure(text=entry.get())
                entry.destroy()
                lbl.pack(side="left")
    def error(self, Message):
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()