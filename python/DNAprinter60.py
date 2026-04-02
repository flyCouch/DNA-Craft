# ==============================================================================
# PROJECT:   DNA_MARK_I_V60_UNIVERSAL_LABELS
# THEME:     Clinical Blue / Medical White
# FOCUS:     All Pop-up Inputs now use Specific Station Names (No more "Reagent")
# __FILE__:  DNAprinter1.py
# __DATE__:  2026-04-02
# __TIME__:  19:45:00
# ==============================================================================

import customtkinter as ctk
from datetime import datetime

STATION_NAMES = ["Adenine", "Cytosine", "Guanine", "Thymine", "Oxidizer", "Capping", "Deblock", "WASH"]

class StationData:
    def __init__(self, name):
        self.name = name
        self.reagent_ms = ctk.IntVar(value=250)
        self.activator_ms = ctk.IntVar(value=250)
        self.adv_release_ms = ctk.IntVar(value=50)
        self.pos_x = ctk.DoubleVar(value=0.0)
        self.pos_r = ctk.DoubleVar(value=0.0) 
        self.pos_z = ctk.DoubleVar(value=15.0)

class DNAMarkI(ctk.CTk):
    def __init__(self):
        super().__init__()

        print(f"Project: DNA_MARK_I_V60 | Date: {datetime.now().strftime('%Y-%m-%d')} | Time: {datetime.now().strftime('%H:%M:%S')}")

        self.title("Lyttle reSearch DNA Crafting Control")
        self.geometry("1650x1000")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.storage = {name: StationData(name) for name in STATION_NAMES}
        
        # --- UI VARIABLES ---
        self.active_profile_name = ctk.StringVar(value="DEFAULT_STATIONS")
        self.active_print_file = ctk.StringVar(value="NO_FILE_LOADED")
        self.total_req_time = ctk.StringVar(value="00:00:00")
        self.time_remaining = ctk.StringVar(value="00:00:00")
        self.cur_x = ctk.StringVar(value="000.0")
        self.cur_r = ctk.StringVar(value="000.0°")
        self.cur_z = ctk.StringVar(value="000.0")
        self.cylinder_height = ctk.StringVar(value="15.5")
        self.jog_step = ctk.StringVar(value="1.0") 
        self.active_station = ctk.StringVar(value="WASH")
        self.speed_r = ctk.IntVar(value=3000) 
        self.speed_x = ctk.IntVar(value=2000)
        self.speed_z = ctk.IntVar(value=1000)

        # --- ATMOSPHERIC VARIABLES ---
        self.argon_psi = ctk.StringVar(value="0.00")
        self.o2_top = ctk.StringVar(value="20.9")
        self.o2_mid = ctk.StringVar(value="20.9")
        self.o2_bot = ctk.StringVar(value="20.9")

        self.setup_ui()

    def setup_ui(self):
        # --- 1. MISSION CONTROL HEADER ---
        self.top_panel = ctk.CTkFrame(self, height=280, corner_radius=0, fg_color="#1B4965")
        self.top_panel.pack(side="top", fill="x")
        self.top_panel.pack_propagate(False)

        p_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        p_frame.pack(side="left", padx=40, expand=True)
        ctk.CTkLabel(p_frame, text="HARDWARE PROFILE", text_color="#62B6CB", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkEntry(p_frame, textvariable=self.active_profile_name, width=280, height=50, font=("Arial", 18, "bold"), justify="center").pack(pady=10)
        
        p_btns = ctk.CTkFrame(p_frame, fg_color="transparent"); p_btns.pack()
        ctk.CTkButton(p_btns, text="LOAD", width=135, height=45, fg_color="#62B6CB", text_color="black").pack(side="left", padx=5)
        ctk.CTkButton(p_btns, text="SAVE", width=135, height=45, fg_color="#62B6CB", text_color="black").pack(side="left", padx=5)

        j_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        j_frame.pack(side="left", expand=True, padx=20)
        ctk.CTkLabel(j_frame, text="ACTIVE SYNTHESIS JOB", text_color="#BEE9E8", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkEntry(j_frame, textvariable=self.active_print_file, width=550, height=60, font=("Courier", 22, "bold"), text_color="#E63946", justify="center").pack(pady=10)
        
        f_row = ctk.CTkFrame(j_frame, fg_color="transparent"); f_row.pack()
        for txt in ["LOAD SEQ", "LOAD G-CODE", "GENERATE"]:
            ctk.CTkButton(f_row, text=txt, width=170, height=45, fg_color="#5FA8D3", text_color="black").pack(side="left", padx=5)

        a_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        a_frame.pack(side="right", padx=50, expand=True)
        ctk.CTkButton(a_frame, text="START", fg_color="#2D6A4F", width=220, height=180, font=("Arial", 42, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(a_frame, text="STOP", fg_color="#E63946", width=220, height=180, font=("Arial", 42, "bold")).pack(side="left", padx=10)

        # --- 2. MONITORING BAR ---
        self.monitor_frame = ctk.CTkFrame(self, fg_color="#BEE9E8", corner_radius=0, height=120) 
        self.monitor_frame.pack(fill="x")
        m_cont = ctk.CTkFrame(self.monitor_frame, fg_color="transparent")
        m_cont.pack(expand=True)
        
        t1 = ctk.CTkFrame(m_cont, fg_color="transparent"); t1.pack(side="left", padx=20)
        ctk.CTkLabel(t1, text="TOTAL CYCLE TIME", font=("Arial", 10, "bold"), text_color="#1B4965").pack()
        ctk.CTkLabel(t1, textvariable=self.total_req_time, font=("Courier", 42, "bold"), text_color="#1B4965").pack()
        
        dro_bg = ctk.CTkFrame(m_cont, fg_color="#1B4965", corner_radius=12, width=600, height=90)
        dro_bg.pack(side="left", padx=20); dro_bg.pack_propagate(False)
        dro_inner = ctk.CTkFrame(dro_bg, fg_color="transparent")
        dro_inner.place(relx=0.5, rely=0.5, anchor="center")
        for i, (axis, var) in enumerate([("X", self.cur_x), ("R", self.cur_r), ("Z", self.cur_z)]):
            cell = ctk.CTkFrame(dro_inner, fg_color="transparent", width=180)
            cell.grid(row=0, column=i, padx=5)
            ctk.CTkLabel(cell, text=axis, font=("Arial", 12, "bold"), text_color="#62B6CB").pack()
            ctk.CTkLabel(cell, textvariable=var, font=("Courier", 24, "bold"), text_color="white").pack()

        t2 = ctk.CTkFrame(m_cont, fg_color="transparent"); t2.pack(side="left", padx=20)
        ctk.CTkLabel(t2, text="REMAINING", font=("Arial", 10, "bold"), text_color="#1B4965").pack()
        ctk.CTkLabel(t2, textvariable=self.time_remaining, font=("Courier", 42, "bold"), text_color="#E63946").pack()

        # --- 3. MOTION & ATMOSPHERE ---
        self.work_frame = ctk.CTkFrame(self, fg_color="#CAE9FF", corner_radius=0)
        self.work_frame.pack(fill="x")
        w_inner = ctk.CTkFrame(self.work_frame, fg_color="transparent")
        w_inner.pack(pady=10, padx=20, fill="x")

        # Jogging
        jog_col = ctk.CTkFrame(w_inner, fg_color="white", border_width=1, border_color="#1B4965")
        jog_col.pack(side="left", padx=5)
        step_row = ctk.CTkFrame(jog_col, fg_color="transparent"); step_row.pack(pady=5)
        for s in ["0.1", "1.0", "10.0"]:
            ctk.CTkRadioButton(step_row, text=s, variable=self.jog_step, value=s, font=("Arial", 9, "bold")).pack(side="left", padx=5)
        g = ctk.CTkFrame(jog_col, fg_color="transparent"); g.pack(padx=10, pady=5)
        for i, ax in enumerate(["ROT", "X", "Z"]):
            ctk.CTkButton(g, text=f"{ax}-", width=45, height=30).grid(row=i, column=0, padx=2, pady=2)
            ctk.CTkButton(g, text=f"{ax}+", width=45, height=30).grid(row=i, column=1, padx=2, pady=2)
            ctk.CTkButton(g, text=f"HOME {ax}", fg_color="#1B4965", width=80, height=30, font=("Arial", 9, "bold")).grid(row=i, column=2, padx=(5, 2), pady=2)

        # Speeds
        sp_box = ctk.CTkFrame(w_inner, fg_color="white", border_width=1, border_color="#1B4965")
        sp_box.pack(side="left", padx=5, fill="y")
        ctk.CTkLabel(sp_box, text="MOTION VELOCITY", font=("Arial", 11, "bold")).pack(pady=5)
        self.add_speed_control(sp_box, "ROTATION", self.speed_r)
        self.add_speed_control(sp_box, "X-TRAVEL", self.speed_x)
        self.add_speed_control(sp_box, "Z-PLUNGE", self.speed_z)

        # Snap
        sn_box = ctk.CTkFrame(w_inner, fg_color="white", border_width=1, border_color="#1B4965")
        sn_box.pack(side="left", expand=True, fill="both", padx=5)
        ctk.CTkLabel(sn_box, text="STATION SNAP-ALIGNMENT", font=("Arial", 11, "bold")).pack(pady=5)
        r_grid = ctk.CTkFrame(sn_box, fg_color="transparent"); r_grid.pack(expand=True, fill="both", padx=10)
        for col in range(4): r_grid.grid_columnconfigure(col, weight=1)
        for row in range(2): r_grid.grid_rowconfigure(row, weight=1)
        for i, name in enumerate(STATION_NAMES):
            ctk.CTkRadioButton(r_grid, text=name.upper(), variable=self.active_station, value=name, font=("Arial", 12, "bold")).grid(row=i//4, column=i%4, sticky="nsew")

        # Atmospheric Monitor
        at_box = ctk.CTkFrame(w_inner, fg_color="white", border_width=2, border_color="#1B4965", width=220)
        at_box.pack(side="left", fill="y", padx=5)
        at_box.pack_propagate(False)
        p_row = ctk.CTkFrame(at_box, fg_color="#1B4965", corner_radius=5)
        p_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(p_row, text="ARGON PSI", text_color="#62B6CB", font=("Arial", 9, "bold")).pack()
        ctk.CTkLabel(p_row, textvariable=self.argon_psi, text_color="white", font=("Arial", 20, "bold")).pack()

        for loc, var in [("O2 TOP", self.o2_top), ("O2 MID", self.o2_mid), ("O2 BOT", self.o2_bot)]:
            o_row = ctk.CTkFrame(at_box, fg_color="#F0F5F9", corner_radius=5)
            o_row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(o_row, text=loc, font=("Arial", 8, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(o_row, textvariable=var, font=("Arial", 12, "bold"), text_color="#E63946").pack(side="right", padx=5)

        # --- 4. STATION CARDS ---
        self.card_frame = ctk.CTkFrame(self, fg_color="#F0F5F9")
        self.card_frame.pack(fill="both", expand=True, padx=20, pady=20)
        for i, name in enumerate(STATION_NAMES):
            card = ctk.CTkFrame(self.card_frame, border_width=1, border_color="#62B6CB", fg_color="white")
            card.grid(row=i//4, column=i%4, padx=5, pady=5, sticky="nsew")
            ctk.CTkLabel(card, text=name.upper(), font=("Arial", 12, "bold"), text_color="#1B4965").pack(pady=5)
            
            t_info = ctk.CTkFrame(card, fg_color="transparent")
            t_info.pack()
            data = self.storage[name]
            
            if name in ["Adenine", "Cytosine", "Guanine", "Thymine"]:
                # Card overview still uses shorthand R and A for space
                ctk.CTkLabel(t_info, text=f"R: {data.reagent_ms.get()}ms", font=("Arial", 9)).pack(side="left", padx=2)
                ctk.CTkLabel(t_info, text=f"A: {data.activator_ms.get()}ms", font=("Arial", 9)).pack(side="left", padx=2)
            else:
                ctk.CTkLabel(t_info, text=f"{name.upper()}: {data.reagent_ms.get()}ms", font=("Arial", 9)).pack(padx=2)
            
            ctk.CTkButton(card, text="⚙", width=60, height=40, font=("Arial", 24), fg_color="transparent", text_color="#1B4965", command=lambda n=name: self.open_settings(n)).pack(pady=5)
        self.card_frame.grid_columnconfigure((0,1,2,3), weight=1); self.card_frame.grid_rowconfigure((0,1), weight=1)

    def add_speed_control(self, master, txt, var):
        f = ctk.CTkFrame(master, fg_color="transparent"); f.pack(fill="x", padx=10)
        ctk.CTkLabel(f, text=txt, font=("Arial", 9, "bold")).pack(side="left")
        ctk.CTkLabel(f, textvariable=var, font=("Arial", 9), text_color="#1B4965").pack(side="right")
        ctk.CTkSlider(master, from_=100, to=5000, variable=var, height=12, width=150).pack(padx=10, pady=(0, 5))

    def open_settings(self, name):
        data = self.storage[name]
        popup = ctk.CTkToplevel(self); popup.title(f"Config: {name}"); popup.geometry("450x650"); popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text=f"STATION: {name.upper()}", font=("Arial", 18, "bold")).pack(pady=20)
        
        p_box = ctk.CTkFrame(popup, fg_color="#F0F5F9", corner_radius=10); p_box.pack(fill="x", padx=25, pady=10)
        self.create_input(p_box, "X-Pos (mm):", data.pos_x)
        self.create_input(p_box, "R-Rot (Deg):", data.pos_r)
        self.create_input(p_box, "Z-Travel (mm):", data.pos_z)
        
        t_box = ctk.CTkFrame(popup, fg_color="transparent"); t_box.pack(fill="x", pady=10)
        
        # UNIVERSAL FIX: Every input now uses the specific station name (e.g. ADENINE (ms):)
        self.create_input(t_box, f"{name.upper()} (ms):", data.reagent_ms)
        
        if name in ["Adenine", "Cytosine", "Guanine", "Thymine"]:
            self.create_input(t_box, "Activator (ms):", data.activator_ms)
            self.create_input(t_box, "Adv Release (ms):", data.adv_release_ms)
            
        ctk.CTkButton(popup, text="SAVE CALIBRATION", width=220, height=45, fg_color="#1B4965", command=popup.destroy).pack(pady=30)

    def create_input(self, master, label_text, variable):
        frame = ctk.CTkFrame(master, fg_color="transparent"); frame.pack(fill="x", padx=40, pady=6)
        ctk.CTkLabel(frame, text=label_text).pack(side="left")
        ctk.CTkEntry(frame, textvariable=variable, width=90, justify="center").pack(side="right")

if __name__ == "__main__":
    DNAMarkI().mainloop()
