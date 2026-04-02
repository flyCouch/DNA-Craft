# ==============================================================================
# PROJECT:   DNA_MARK_I_V30_ERGONOMIC_LAYOUT
# THEME:     Clinical Blue / Medical White
# FOCUS:     Lateral Homing Buttons / Improved Jogging Ergonomics
# __FILE__:  DNAprinter1.py
# __DATE__:  2026-04-03
# __TIME__:  13:10:00
# ==============================================================================

import customtkinter as ctk
from tkinter import filedialog
import os
from datetime import datetime

STATION_NAMES = ["Adenine", "Cytosine", "Guanine", "Thymine", "Oxidizer", "Capping", "Deblock", "WASH"]

class StationData:
    def __init__(self, name):
        self.name = name
        self.reagent_ms = ctk.IntVar(value=250)
        self.activator_ms = ctk.IntVar(value=250)
        self.adv_release_ms = ctk.IntVar(value=50)

class DNAMarkI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Project Header Print ---
        print(f"Project: DNA_MARK_I_V30 | Date: {datetime.now().strftime('%Y-%m-%d')} | Time: {datetime.now().strftime('%H:%M:%S')}")

        self.title("Lyttle reSearch DNA Crafting Control")
        self.geometry("1650x1000")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.storage = {name: StationData(name) for name in STATION_NAMES}
        
        self.active_profile_name = ctk.StringVar(value="DEFAULT_STATIONS")
        self.active_print_file = ctk.StringVar(value="NO_FILE_LOADED")
        self.total_req_time = ctk.StringVar(value="00:00:00")
        self.time_remaining = ctk.StringVar(value="00:00:00")
        
        self.jog_step = ctk.StringVar(value="1.0") 
        self.active_station = ctk.StringVar(value="WASH")
        self.speed_r = ctk.IntVar(value=1500)
        self.speed_x = ctk.IntVar(value=2000)
        self.speed_z = ctk.IntVar(value=1000)

        self.setup_ui()
        self.update_clocks()

    def setup_ui(self):
        # --- 1. MISSION CONTROL HEADER ---
        self.top_panel = ctk.CTkFrame(self, height=320, corner_radius=0, fg_color="#1B4965")
        self.top_panel.pack(side="top", fill="x")
        self.top_panel.pack_propagate(False)

        # Profile / Job / Start-Stop (Kept from V29)
        p_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        p_frame.pack(side="left", padx=40, expand=True)
        ctk.CTkLabel(p_frame, text="HARDWARE PROFILE", text_color="#62B6CB", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkEntry(p_frame, textvariable=self.active_profile_name, width=280, height=50, font=("Arial", 18, "bold"), fg_color="white", text_color="#1B4965", state="readonly", justify="center").pack(pady=10)
        btn_row = ctk.CTkFrame(p_frame, fg_color="transparent")
        btn_row.pack()
        ctk.CTkButton(btn_row, text="LOAD", width=135, height=45, fg_color="#62B6CB", text_color="black", font=("Arial", 14, "bold"), command=lambda: print("Load")).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="SAVE", width=135, height=45, fg_color="#62B6CB", text_color="black", font=("Arial", 14, "bold"), command=lambda: print("Save")).pack(side="left", padx=5)

        j_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        j_frame.pack(side="left", expand=True, padx=20)
        ctk.CTkLabel(j_frame, text="ACTIVE SYNTHESIS JOB", text_color="#BEE9E8", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkEntry(j_frame, textvariable=self.active_print_file, width=550, height=60, font=("Courier", 22, "bold"), fg_color="white", text_color="#E63946", state="readonly", justify="center").pack(pady=10)
        f_btn_row = ctk.CTkFrame(j_frame, fg_color="transparent")
        f_btn_row.pack()
        ctk.CTkButton(f_btn_row, text="LOAD SEQ", width=170, height=45, fg_color="#5FA8D3", text_color="black", font=("Arial", 13, "bold"), command=lambda: print("Seq")).pack(side="left", padx=5)
        ctk.CTkButton(f_btn_row, text="LOAD G-CODE", width=170, height=45, fg_color="#5FA8D3", text_color="black", font=("Arial", 13, "bold"), command=lambda: print("Gcode")).pack(side="left", padx=5)
        ctk.CTkButton(f_btn_row, text="GENERATE", width=170, height=45, fg_color="#BEE9E8", text_color="black", font=("Arial", 13, "bold"), command=lambda: print("Gen")).pack(side="left", padx=5)

        a_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        a_frame.pack(side="right", padx=50, expand=True)
        ctk.CTkButton(a_frame, text="START", fg_color="#2D6A4F", width=220, height=180, font=("Arial", 42, "bold"), command=lambda: print("START")).pack(side="left", padx=10)
        ctk.CTkButton(a_frame, text="STOP", fg_color="#E63946", width=220, height=180, font=("Arial", 42, "bold"), command=lambda: print("HALT")).pack(side="left", padx=10)

        # --- 2. MONITORING BAR ---
        self.monitor_frame = ctk.CTkFrame(self, fg_color="#BEE9E8", corner_radius=0, height=110) 
        self.monitor_frame.pack(fill="x")
        self.monitor_frame.pack_propagate(False)
        t_cont = ctk.CTkFrame(self.monitor_frame, fg_color="transparent")
        t_cont.pack(expand=True, fill="both")
        for var, lbl, clr in [(self.total_req_time, "TOTAL CYCLE TIME", "#1B4965"), (self.time_remaining, "REMAINING DURATION", "#E63946")]:
            box = ctk.CTkFrame(t_cont, fg_color="transparent")
            box.pack(side="left", expand=True)
            ctk.CTkLabel(box, text=lbl, font=("Arial", 10, "bold"), text_color="#1B4965").pack(pady=(5, 0))
            ctk.CTkLabel(box, textvariable=var, font=("Courier", 44, "bold"), text_color=clr).pack(pady=(4, 6))

        # --- 3. MOTION CONTROL (LATERAL HOMING) ---
        self.motion_frame = ctk.CTkFrame(self, fg_color="#CAE9FF", corner_radius=0)
        self.motion_frame.pack(fill="x")
        m_inner = ctk.CTkFrame(self.motion_frame, fg_color="transparent")
        m_inner.pack(pady=10, padx=20, fill="x")

        # Jogging Box
        jog_box = ctk.CTkFrame(m_inner, fg_color="white", border_width=1, border_color="#1B4965")
        jog_box.pack(side="left", padx=10)
        
        # Step Size Row
        s_row = ctk.CTkFrame(jog_box, fg_color="transparent")
        s_row.pack(pady=(5, 0))
        for s in ["0.1", "1.0", "10.0"]:
            ctk.CTkRadioButton(s_row, text=s, variable=self.jog_step, value=s, font=("Arial", 11)).pack(side="left", padx=10)
        
        # Main Grid: Jog buttons on left, Home buttons on right
        g = ctk.CTkFrame(jog_box, fg_color="transparent")
        g.pack(pady=5, padx=10)
        for i, ax in enumerate(["ROT", "X", "Z"]):
            axis_name = "R" if ax == "ROT" else ax
            # Directional Buttons
            ctk.CTkButton(g, text=f"{ax}-", width=55, height=35, command=lambda a=axis_name: print(f"{a}-")).grid(row=i, column=0, padx=2, pady=2)
            ctk.CTkButton(g, text=f"{ax}+", width=55, height=35, command=lambda a=axis_name: print(f"{a}+")).grid(row=i, column=1, padx=2, pady=2)
            # Home Buttons (To the right)
            ctk.CTkButton(g, text=f"HOME {ax}", fg_color="#1B4965", width=90, height=35, font=("Arial", 9, "bold"), 
                          command=lambda a=ax: print(f"Homing {a}")).grid(row=i, column=2, padx=(15, 2), pady=2)

        # Axis Speeds
        sp_box = ctk.CTkFrame(m_inner, fg_color="white", border_width=1, border_color="#1B4965")
        sp_box.pack(side="left", padx=10, fill="y")
        ctk.CTkLabel(sp_box, text="AXIS SPEEDS (mm/min)", font=("Arial", 12, "bold")).pack(pady=5)
        self.add_speed_control(sp_box, "ROT", self.speed_r)
        self.add_speed_control(sp_box, "X-AXIS", self.speed_x)
        self.add_speed_control(sp_box, "Z-LIFT", self.speed_z)

        # Snap Alignment
        sn_box = ctk.CTkFrame(m_inner, fg_color="white", border_width=1, border_color="#1B4965")
        sn_box.pack(side="left", expand=True, fill="both", padx=10)
        ctk.CTkLabel(sn_box, text="STATION SNAP-ALIGNMENT", font=("Arial", 13, "bold")).pack(pady=5)
        r_grid = ctk.CTkFrame(sn_box, fg_color="transparent")
        r_grid.pack(expand=True, fill="both", padx=10, pady=5)
        r_grid.grid_columnconfigure((0,1,2,3), weight=1)
        r_grid.grid_rowconfigure((0,1), weight=1)
        for i, name in enumerate(STATION_NAMES):
            ctk.CTkRadioButton(r_grid, text=name.upper(), variable=self.active_station, value=name, 
                               font=("Arial", 14, "bold"), radiobutton_width=24, radiobutton_height=24).grid(row=i//4, column=i%4, sticky="nsew", padx=10, pady=12)

        # --- 4. STATION PLACARDS ---
        self.card_frame = ctk.CTkFrame(self, fg_color="#F0F5F9")
        self.card_frame.pack(fill="both", expand=True, padx=30, pady=20)
        for i, name in enumerate(STATION_NAMES):
            card = ctk.CTkFrame(self.card_frame, border_width=1, border_color="#62B6CB", fg_color="white")
            card.grid(row=i//4, column=i%4, padx=8, pady=8, sticky="nsew")
            ctk.CTkLabel(card, text=name.upper(), font=("Arial", 12, "bold"), text_color="#1B4965").pack(pady=(12, 5))
            ctk.CTkButton(card, text="⚙", width=90, height=55, font=("Arial", 36), fg_color="transparent", text_color="#1B4965", hover_color="#CAE9FF", 
                          command=lambda n=name: self.open_settings(n)).pack(pady=12)
        self.grid_setup()

    def grid_setup(self):
        self.card_frame.grid_columnconfigure((0,1,2,3), weight=1)
        self.card_frame.grid_rowconfigure((0,1), weight=1)

    def add_speed_control(self, master, txt, var):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(fill="x", padx=10)
        ctk.CTkLabel(f, text=txt, font=("Arial", 10, "bold")).pack(side="left")
        ctk.CTkLabel(f, textvariable=var, font=("Arial", 10), text_color="#1B4965").pack(side="right")
        ctk.CTkSlider(master, from_=100, to=5000, variable=var, height=15, width=160).pack(padx=10, pady=(0, 5))

    def open_settings(self, name):
        data = self.storage[name]
        popup = ctk.CTkToplevel(self)
        popup.title(f"Config: {name}"); popup.geometry("380x400"); popup.attributes("-topmost", True)
        is_monomer = name in ["Adenine", "Cytosine", "Guanine", "Thymine"]
        ctk.CTkLabel(popup, text=f"CALIBRATION: {name.upper()}", font=("Arial", 16, "bold")).pack(pady=15)
        if is_monomer:
            self.create_input(popup, "Activator Strike (ms):", data.activator_ms)
            self.create_input(popup, "Activator Advance (ms):", data.adv_release_ms)
            self.create_input(popup, "Monomer Strike (ms):", data.reagent_ms)
        else:
            self.create_input(popup, "Strike Duration (ms):", data.reagent_ms)
        ctk.CTkButton(popup, text="SAVE & CLOSE", width=200, height=40, fg_color="#1B4965", command=popup.destroy).pack(pady=30)

    def create_input(self, master, lbl, var):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=6)
        ctk.CTkLabel(frame, text=lbl, font=("Arial", 11)).pack(side="left")
        ctk.CTkEntry(frame, textvariable=var, width=80, justify="center").pack(side="right")

    def update_clocks(self):
        self.time_remaining.set(datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_clocks)

if __name__ == "__main__":
    DNAMarkI().mainloop()
