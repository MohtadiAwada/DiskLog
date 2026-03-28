import customtkinter as ctk
import json

ctk.set_appearance_mode("System")

class App(ctk.CTk):
    JSON_FILE = "data.json"
    JSON_DATA = []
    def __init__(self):
        super().__init__()
        self.selected_index = None
        self.row_widgets = []
        
        self.title("External Disks Manager")
        self.iconbitmap("icon.ico")
        self.geometry("950x500")
        self.resizable(False, False)

        self.header = ctk.CTkFrame(self, height=20, corner_radius=0, fg_color="#2A2A3D")
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)
        self.title = ctk.CTkLabel(self.header, text="External-Disks-Manager", text_color="#C9C9E0")
        self.title.pack(pady=0, padx=0)

        self.body = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.body.pack(side="top", fill="both", expand=True)

        self.toolbar = ctk.CTkFrame(self.body, corner_radius=0, fg_color="#252535", width=24)
        self.toolbar.pack(side="left", fill="both", expand=False)
        self.toolbar.pack_propagate(False)
        self.tb_edt_rfrsh = ctk.CTkButton(self.toolbar, corner_radius=0, text="R",fg_color="transparent", height=24, command=self.construct_table, text_color="#9D9DB8", hover_color="#35354A")
        self.tb_edt_rfrsh.pack(side="top", fill="x")
        self.tb_dlt_btn = ctk.CTkButton(self.toolbar, corner_radius=0, text="D",fg_color="transparent", height=24, text_color="#9D9DB8", hover_color="#35354A", command=self.delete)
        self.tb_dlt_btn.pack(side="top", fill="x")
        self.tb_edt_btn = ctk.CTkButton(self.toolbar, corner_radius=0, text="E",fg_color="transparent", height=24, text_color="#9D9DB8", hover_color="#35354A")
        self.tb_edt_btn.pack(side="top", fill="x")

        self.main = ctk.CTkFrame(self.body, corner_radius=0, fg_color="#1E1E2E")
        self.main.pack(side="left", fill="both", expand=True)

        self.table = ctk.CTkFrame(self.main, corner_radius=0, fg_color="#1E1E2E")
        self.table.pack(fill="both", expand=True)

        self.form = ctk.CTkFrame(self.main, corner_radius=0, fg_color="#22223A")
        self.form.pack(side="bottom", fill="x")
        self.form_inpt = ctk.CTkFrame(self.form, corner_radius=0, fg_color="transparent")
        self.form_inpt.pack(side="top", fill="x")
        self.form_inpt_id = ctk.CTkEntry(self.form_inpt, corner_radius=0, width=48, placeholder_text="ID", fg_color="#2C2C42", border_color="#4A4A6A", text_color="#D0D0E8", placeholder_text_color="#6A6A8A")
        self.form_inpt_id.pack(side="left", padx=[10, 0], pady=10)
        self.form_inpt_ttl = ctk.CTkEntry(self.form_inpt, corner_radius=0, width=180, placeholder_text="Title", fg_color="#2C2C42", border_color="#4A4A6A", text_color="#D0D0E8", placeholder_text_color="#6A6A8A")
        self.form_inpt_ttl.pack(side="left", padx=[10, 0], pady=10)
        self.form_inpt_dscrptn = ctk.CTkEntry(self.form_inpt, corner_radius=0, placeholder_text="Description", fg_color="#2C2C42", border_color="#4A4A6A", text_color="#D0D0E8", placeholder_text_color="#6A6A8A")
        self.form_inpt_dscrptn.pack(side="left", fill="both", expand=True, padx=[10, 10], pady=10)
        self.form_inpt_type = ctk.CTkComboBox(self.form_inpt, corner_radius=0, values=["HDD", "SSD", "NVMe", "Flash Drive", "Memory Card"], state="readonly", width=120, fg_color="#2C2C42", border_color="#4A4A6A", text_color="#D0D0E8", button_color="#3D3D58")
        self.form_inpt_type.set("Type")
        self.form_inpt_type.pack(side="left", padx=[0, 10], pady=10)
        self.form_inpt_isencrptd = ctk.CTkCheckBox(self.form_inpt, corner_radius=0, text="Encrypted", command=self.change_handler, text_color="#B0B0D0", fg_color="#9B72CF", hover_color="#9B72CF", border_color="#4A4A6A")
        self.form_inpt_isencrptd.pack(side="left", padx=[0, 10], pady=10)
        self.form_inpt_pswrdprtcl = ctk.CTkComboBox(self.form_inpt, corner_radius=0, values=["Defualt", "ToPower3", "None"], state="readonly", width=144, fg_color="#2C2C42", border_color="#4A4A6A", text_color="#D0D0E8", button_color="#3D3D58")
        self.form_inpt_pswrdprtcl.set("Password Protocol")
        self.form_btn = ctk.CTkFrame(self.form, corner_radius=0, fg_color="transparent")
        self.form_btn.pack(side="top", fill="x")
        self.form_btn_sv = ctk.CTkButton(self.form_btn, corner_radius=0, text="save", command=self.submit_handler, fg_color="#6B4FA0", hover_color="#7D5FB5", text_color="#FFFFFF")
        self.form_btn_sv.pack(side="left", fill="both", expand=True, padx=[10, 0], pady=[0, 10])
        self.form_btn_clr = ctk.CTkButton(self.form_btn, corner_radius=0, text="clear", fg_color="#3A3A52", hover_color="#4A4A65", text_color="#C0C0DC", command=self.clear)
        self.form_btn_clr.pack(side="left", fill="both", expand=True, padx=[10, 10], pady=[0, 10])
        self.construct_table()

    def change_handler(self):
        if self.form_inpt_isencrptd.get():
            self.form_inpt_pswrdprtcl.pack(side="left", padx=[0, 10], pady=10)
        else:
            self.form_inpt_pswrdprtcl.pack_forget()
    
    def construct_row(self, rowObj, color, index):
        row = ctk.CTkFrame(self.table, corner_radius=0, fg_color=color)
        row.pack(fill="x")
        id = ctk.CTkLabel(row, text=rowObj["id"], corner_radius=0, width=48)
        id.pack(side="left")
        ttype = ctk.CTkLabel(row, text=rowObj["type"], corner_radius=0, width=150)
        ttype.pack(side="left")
        title = ctk.CTkLabel(row, text=rowObj["title"], corner_radius=0, width=180)
        title.pack(side="left")
        description = ctk.CTkLabel(row, text=rowObj["description"], corner_radius=0, width=400)
        description.pack(side="left")
        if(rowObj["isEncrypted"]):
            enc = ctk.CTkLabel(row, text=f"Ecrypted ({rowObj["passwordProtocol"]})", width=148, corner_radius=0, fg_color="#3A2E50", text_color="#C8A8F0")
            enc.pack(side="left")
        else:
            enc = ctk.CTkLabel(row, text="Unlocked", width=148, corner_radius=0, fg_color="#2A3040", text_color="#90A8C8")
            enc.pack(side="left")
        self.row_widgets.append(row)
        click = lambda e, i=index: self.handle_select(i)
        id.bind("<Button-1>", click)
        ttype.bind("<Button-1>", click)
        title.bind("<Button-1>", click)
        description.bind("<Button-1>", click)
        enc.bind("<Button-1>", click)
    
    def get_data(self):
        try:
            with open(self.JSON_FILE, "r") as file:
                data = json.load(file)
            self.JSON_DATA = data
            return data
        except FileNotFoundError:
            return

    def update_data(self):
        with open(self.JSON_FILE, 'w') as f:
            json.dump(self.JSON_DATA, f, indent=4)
    
    def construct_table(self):
        self.get_data()
        for element in self.table.winfo_children():
            element.destroy()
        table_head = ctk.CTkFrame(self.table, corner_radius=0, fg_color="#2E2E45")
        table_head.pack(fill="x")
        table_head_id = ctk.CTkLabel(table_head, corner_radius=0, text="ID", width=48, text_color="#A0A0C0", fg_color="#2E2E45")
        table_head_id.pack(side="left")
        table_head_type = ctk.CTkLabel(table_head, corner_radius=0, text="Type", width=150, text_color="#A0A0C0", fg_color="#2E2E45")
        table_head_type.pack(side="left")
        table_head_title = ctk.CTkLabel(table_head, corner_radius=0, text="Title", width=180, text_color="#A0A0C0", fg_color="#2E2E45")
        table_head_title.pack(side="left")
        table_head_dscrptn = ctk.CTkLabel(table_head, corner_radius=0, text="Description", width=400, text_color="#A0A0C0", fg_color="#2E2E45")
        table_head_dscrptn.pack(side="left")
        table_head_state = ctk.CTkLabel(table_head, corner_radius=0, width=148, text="State", text_color="#A0A0C0", fg_color="#2E2E45")
        table_head_state.pack(side="left")
        data = self.JSON_DATA
        self.row_widgets = []
        self.selected_index = None
        for i, rowObj in enumerate(data):
            color = "#272738" if i%2==0 else "#232333"
            self.construct_row(rowObj, color, i)
    
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
        self.clear()
        self.JSON_DATA.append(obj)
        self.update_data()
        self.construct_table()

    def clear(self):
        self.form_inpt_id.delete(0, "end")
        self.form_inpt_id.configure(placeholder_text="ID")
        self.form_inpt_ttl.delete(0, "end")
        self.form_inpt_ttl.configure(placeholder_text="Title")
        self.form_inpt_dscrptn.delete(0, "end")
        self.form_inpt_dscrptn.configure(placeholder_text="Description")
        self.form_inpt_type.set("Type")
        self.form_inpt_isencrptd.deselect()
        self.change_handler()
        self.form_inpt_pswrdprtcl.set("Password Protocol")

    def handle_select(self, index):
        if self.selected_index is not None:
            color = color = "#272738" if self.selected_index%2==0 else "#232333"
            self.row_widgets[self.selected_index].configure(fg_color=color)
        self.selected_index = index
        self.row_widgets[index].configure(fg_color="#3D2F5A")

    def delete(self):
        if self.selected_index is None:
            return
        del self.JSON_DATA[self.selected_index]
        self.update_data()
        self.construct_table()

if __name__ == "__main__":
    app = App()
    app.mainloop()