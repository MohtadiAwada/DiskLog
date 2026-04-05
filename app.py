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
        self.load_config()
        self.build_ui()
        self.render_data()
        self.apply_config()
    def build_ui(self):
        self.title("External Disks Manager")
        #self.iconbitmap(resource_path("icon.ico")) #icon not available
        self.geometry("950x500")
        
        self.header = ctk.CTkFrame(self, height=24, corner_radius=0)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)
        self.header_config_btn = ctk.CTkButton(self.header, corner_radius=0, width=24, text="☰", command=self.config_panel_toggle_handler)
        self.header_config_btn.pack(side="left", pady=0, padx=0)
        self.header_title_lbl = ctk.CTkLabel(self.header, text="External-Disks-Manager")
        self.header_title_lbl.pack(pady=0, padx=0)

        self.body = ctk.CTkFrame(self, corner_radius=0)
        self.body.pack(side="top", fill="both", expand=True)
        self.toolbar = ctk.CTkFrame(self.body, corner_radius=0, width=24)
        self.toolbar.pack(side="left", fill="both", expand=False)
        self.toolbar.pack_propagate(False)
        self.toolbar_refresh_btn = ctk.CTkButton(self.toolbar, corner_radius=0, text="↻", height=24, command=self.refresh_handler)
        self.toolbar_delete_btn = ctk.CTkButton(self.toolbar, corner_radius=0, text="✕", height=24, command=self.delete_handler)
        self.toolbar_edit_btn = ctk.CTkButton(self.toolbar, corner_radius=0, text="✎", height=24)
        for e in self.toolbar.winfo_children():
            e.pack(side="top")
        self.main = ctk.CTkFrame(self.body, corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)
        self.table = ctk.CTkFrame(self.main, corner_radius=0)
        self.table.pack(fill="both", expand=True)
        self.form = ctk.CTkFrame(self.main, corner_radius=0)
        self.form.pack(side="bottom", fill="x")
        self.config_panel = self.construct_configPanel(self.body, self.CONFIG)
    #data manipulation
    def load_config(self):
        def load_theme(theme_name:str):
            with open(external_path(f"themes/{theme_name}.json")) as theme_file:
                self.theme = json.load(theme_file)
        with open(self.CONFIG_FILE, "r") as config_file:
            self.CONFIG = json.load(config_file)
        self.CONFIG_CHANGE = False
        load_theme(self.CONFIG["Appearance"]["Theme"])
    def save_config(self):
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.CONFIG, f, indent=4)
        self.load_config()
        self.apply_config()
        self.config_panel.place_forget()
    def apply_config(self):
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
                sec.grid_columnconfigure(0, weight=1)
                for index, (label, value) in enumerate(section.items()):
                    frame = ctk.CTkFrame(sec)
                    frame.grid(row=index, column=0, sticky="w")
                    lbl = ctk.CTkLabel(frame, text=label+":")
                    lbl.pack(side="left", padx=[12, 6])
                    val = ctk.CTkLabel(frame, text=value)
                    val.pack(side="left")
                    btn = ctk.CTkButton(sec, text="✎", width=24)
                    btn.configure(command=lambda t="Appearance", s=sec, r=index: self.cnfg_edit_handler(t, s, r))
                    btn.grid(row=index, column=1, padx=12)
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
                    edit = ctk.CTkButton(sec, text="✎", width=24)
                    edit.configure(command=lambda t="Data Entry", s=sec, r=row: self.cnfg_edit_handler(t, s, r))
                    edit.grid(row=row, column=3, padx=12)
            sec.pack(side="top", fill="x", padx=0, pady=0)
        button_frame = ctk.CTkFrame(panel)
        button_frame.pack(side="bottom", fill="x")
        save_button = ctk.CTkButton(button_frame, text="save", command=self.save_config)
        save_button.pack(side="right", padx=12, pady=12)
        return panel
    def construct_table(self, table:ctk.CTkFrame, data:dict) -> list[ctk.CTkFrame]:
        def construct_row(rowObj:dict, index:int):
            click = lambda e, i=index: self.select_handler(i)
            row = ctk.CTkFrame(table, corner_radius=0)
            row.pack(side="top", fill="x")
            for d in self.CONFIG["Data Entry"]:
                try:
                    text = rowObj[d["Title"]]
                except KeyError:
                    text = ""
                match d["Type"]:
                    case "small entry":
                        td = ctk.CTkLabel(row, text=text, width=12*6)
                    case "medium entry" | "select":
                        td = ctk.CTkLabel(row, text=text, width=12*14)
                    case "large entry":
                        td = ctk.CTkLabel(row, text=text)
                        td.pack(side="left", fill="both", expand=True)
                        td.bind("<Button-1>", click)
                        continue
                td.pack(side="left")
                td.bind("<Button-1>", click)
            rows_widget.append(row)
        rows_widget = []
        for element in table.winfo_children():
            element.destroy()
        thead = ctk.CTkFrame(table, corner_radius=0)
        thead.pack(side="top", fill="x")
        for tht in self.CONFIG["Data Entry"]:
            match tht["Type"]:
                case "small entry":
                    th = ctk.CTkLabel(thead, text=tht["Title"], width=12*6)
                case "medium entry" | "select":
                    th = ctk.CTkLabel(thead, text=tht["Title"], width=12*14)
                case "large entry":
                    th = ctk.CTkLabel(thead, text=tht["Title"])
                    th.pack(side='left', fill='x', expand=True)
                    continue
            th.pack(side="left")
        for i, rowObj in enumerate(data):
            construct_row(rowObj, i)
        self.apply_theme(self.theme)
        return rows_widget
    def construct_form(self, input_Objs:list, form:ctk.CTkFrame):
        for element in form.winfo_children():
            element.destroy()
        inputs = ctk.CTkFrame(form)
        inputs.pack(fill="x", padx=[0, 12], pady=12)
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
        clear_button = ctk.CTkButton(buttons, text="clear", command=lambda i=inputs: self.clear_handler(i))
        for btn in [save_button, clear_button]:
            btn.pack(side="left", padx=[12, 0], fill="both", expand=True)
    def apply_theme(self, theme:dict):
        self.configure(fg_color=theme["main"]["fg-color"])
        self.header.configure(fg_color=theme["header"]["fg-color"])
        self.header_title_lbl.configure(text_color=theme["header"]["text-color"])
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
                    #if k == len(e.winfo_children())-1:
                        #if self.DATA[i-1]["isEncrypted"]:
                        #    chld.configure(fg_color=theme["table"]["row-badge-fg-color-true"], text_color=theme["table"]["row-badge-text-color-true"])
                        #else:
                        #    chld.configure(fg_color=theme["table"]["row-badge-fg-color-false"], text_color=theme["table"]["row-badge-text-color-false"])
                        #pass
                    #else:
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
        self.header_config_btn.configure(fg_color=theme["config-panel"]["open-fg-color"], hover_color=theme["config-panel"]["open-hover-color"], text_color=theme["config-panel"]["open-inner-color"])
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
                                    if isinstance(child, ctk.CTkEntry):
                                        child.configure(fg_color=theme["config-panel"]["input-fg-color"], border_color=theme["config-panel"]["input-border-color"], text_color=theme["config-panel"]["input-text-color"])
                                    elif isinstance(child, ctk.CTkComboBox):
                                        child.configure(fg_color=theme["config-panel"]["input-fg-color"], border_color=theme["config-panel"]["input-border-color"], button_color=theme["config-panel"]["input-button-color"], text_color=theme["config-panel"]["input-text-color"])
                                    else:
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
        self.clear_handler(inputs)
    def clear_handler(self, inputs):
        for i, d in zip(inputs.winfo_children(), self.CONFIG["Data Entry"]):
            if isinstance(i, ctk.CTkEntry):
                i.delete(0, "end")
                i.configure(placeholder_text=d["Title"])
            elif isinstance(i, ctk.CTkComboBox):
                i.set(d["Title"])
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
    def cnfg_edit_handler(self, title:str, section:ctk.CTkFrame, row_num:int):
        row = section.grid_slaves(row=row_num)
        temp = []
        planB = False
        for cell in row:
            if isinstance(cell, ctk.CTkFrame):
                temp.append({cell.winfo_children()[0].cget("text")[:-1]: cell.winfo_children()[1].cget("text")})
            elif isinstance(cell, ctk.CTkLabel):
                planB = True
        if planB:
            temp.append({row[2].cget("text")[:-1]: row[1].cget('text')})
        temp.reverse()
        for cell in row:
            cell.destroy()
        for i, lbl in enumerate(temp):
            edit_frame = ctk.CTkFrame(section)
            for k, v in lbl.items():
                label = ctk.CTkLabel(edit_frame, text=k+":")
                label.pack(side="left", padx=[12, 6])
                input = None
                match k:
                    case "Type":
                        input=ctk.CTkComboBox(edit_frame, values=["small entry", "medium entry", "large entry", "select"], state="readonly")
                        input.configure(command=lambda val, s=section, r=row_num: self.type_change_handler(val, s, r))
                        input.set(v)
                    case "Class":
                        input=ctk.CTkComboBox(edit_frame, values=["ID", "String"], state="readonly")
                        input.set(v)
                    case "Theme":
                        themes = []
                        for theme in os.listdir(external_path("themes")):
                            if theme.endswith(".json"):
                                themes.append(theme[:-5])
                        input=ctk.CTkComboBox(edit_frame, values=themes, state="readonly")
                        input.set(v)
                    case _:
                        input=ctk.CTkEntry(edit_frame)
                        input.insert(0, v)
                input.pack(side="left")
            edit_frame.grid(row=row_num, column=i, sticky="w")
            last = i
        button = ctk.CTkButton(section, text="✓", width=24, command=lambda r=row_num, s=section, t=title: self.save_config_handler(r, s, t))
        button.grid(row=row_num, column=last+1, padx=12)
        self.apply_theme(self.theme)
    def type_change_handler(self, value:str, section:ctk.CTkFrame, row_num:int):
        slaves = section.grid_slaves(row=row_num, column=2)
        match value:
            case "select":
                if not isinstance(slaves[0].winfo_children()[1], ctk.CTkEntry):
                    slaves[0].destroy()
                    frame = ctk.CTkFrame(section)
                    frame.grid(row=row_num, column=2, sticky="w")
                    label = ctk.CTkLabel(frame, text="Values:")
                    label.pack(side="left", padx=[12, 6])
                    input = ctk.CTkEntry(frame)
                    input.pack(side="left")
            case _:
                if not isinstance(slaves[0].winfo_children()[1], ctk.CTkComboBox):
                    slaves[0].destroy()
                    frame = ctk.CTkFrame(section)
                    frame.grid(row=row_num, column=2, sticky="w")
                    label = ctk.CTkLabel(frame, text="Class:")
                    label.pack(side="left", padx=[12, 6])
                    input = ctk.CTkComboBox(frame, values=["ID", "String"], state="readonly")
                    input.set("String")
                    input.pack(side="left")
        self.apply_theme(self.theme)
    def save_config_handler(self, row_num, section, title):
        row = section.grid_slaves(row=row_num)
        temp = []
        for cell in row:
            if isinstance(cell, ctk.CTkFrame):
                temp.append({cell.winfo_children()[0].cget("text")[:-1]: cell.winfo_children()[1].get()})
        temp.reverse()
        data_obj = {}
        for i in temp:
            for k, v in i.items():
                data_obj[k]=v
        if title == "Data Entry":
            if data_obj["Type"] == "select":
                data_obj["Values"] = data_obj["Values"].split(", ")
            self.CONFIG[title][row_num] = data_obj
        elif title == "Appearance":
            self.CONFIG[title][next(iter(data_obj))] = data_obj[next(iter(data_obj))]
        for cell in row:
            cell.destroy()
        for i, lbl in enumerate(temp):
            display_frame = ctk.CTkFrame(section)
            for k, v in lbl.items():
                label = ctk.CTkLabel(display_frame, text=k+':')
                label.pack(side="left", padx=[12, 6])
                val_label = ctk.CTkLabel(display_frame, text=v)
                val_label.pack(side="left")
            display_frame.grid(row=row_num, column=i, sticky="w")
            last = i
        edit_button = ctk.CTkButton(section, text="✎", width=24, command=lambda t=title, s=section, r=row_num: self.cnfg_edit_handler(t, s, r))
        edit_button.grid(row=row_num, column=last+1, padx=12)
        self.apply_theme(self.theme)
    def error(self, message):
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()