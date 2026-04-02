# ==============================================================================
# PROJECT:   DNA_MARK_I_MISSION_CONTROL_V4
# THEME:     Clinical Blue / Medical White
# FOCUS:     Icon Scaling / Vertical Text Spacing
# __FILE__:  DNAprinter1.py
# __DATE__:  2026-04-02
# __TIME__:  14:35:00
# ==============================================================================

import customtkinter as ctk
from datetime import datetime

# --- GLOBAL CONFIGURATION ---
STATION_NAMES = [
    "Adenine", "Cytosine", "Guanine", "Thymine", 
    "Oxidizer", "Capping", "Deblock", "WASH"
]

class StationData:
    def __init__(self, name):
        self.name = name
        self.activator_ms = ctk.IntVar(value=250)
        self.adv_release_ms = ctk.IntVar(value=50)
        self.reagent_ms = ctk.IntVar(value=250) 

class DNAMarkI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Lyttle reSearch DNA Crafting Control")
        self.geometry("1200x850")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.storage = {name: StationData(name) for name in STATION_NAMES}
        
        # System Variables
        self.sys_psi = ctk.StringVar(value="5.00 PSI")
        self.sys_o2 = ctk.StringVar(value="0.01%")
        self.total_req_time = ctk.StringVar(value="02:45:00")
        self.time_remaining = ctk.StringVar(value="01:12:34")
        
        self.setup_ui()
        self.update_clocks()

    def setup_ui(self):
        # --- TOP PANEL: EMERGENCY & UTILITY ---
        self.top_panel = ctk.CTkFrame(self, height=110, corner_radius=0, fg_color="#1B4965")
        self.top_panel.pack(side="top", fill="x")

        # Controls (Left)
        self.ctrl_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        self.ctrl_frame.pack(side="left", padx=30)
        ctk.CTkButton(self.ctrl_frame, text="OPEN SEQUENCE", font=("Arial", 11, "bold"), fg_color="#62B6CB", text_color="black", width=120).grid(row=0, column=0, padx=4, pady=4)
        ctk.CTkButton(self.ctrl_frame, text="ARGON PURGE", font=("Arial", 11, "bold"), fg_color="#5FA8D3", text_color="black", width=120).grid(row=0, column=1, padx=4, pady=4)
        ctk.CTkButton(self.ctrl_frame, text="SAVE LOG", font=("Arial", 11, "bold"), fg_color="#62B6CB", text_color="black", width=120).grid(row=1, column=0, padx=4, pady=4)
        ctk.CTkButton(self.ctrl_frame, text="PRIME LINES", font=("Arial", 11, "bold"), fg_color="#5FA8D3", text_color="black", width=120).grid(row=1, column=1, padx=4, pady=4)

        # Emergency Stop (Right)
        self.stop_btn = ctk.CTkButton(self.top_panel, text="STOP", fg_color="#E63946", 
                                      hover_color="#BA2D33", width=220, height=80, 
                                      font=("Arial", 38, "bold"), command=self.emergency_stop)
        self.stop_btn.pack(side="right", padx=30)

        # --- CENTRAL MONITORING STATION ---
        self.monitor_frame = ctk.CTkFrame(self, fg_color="#BEE9E8", corner_radius=0)
        self.monitor_frame.pack(fill="x")

        # Dual Timer Row
        timer_row = ctk.CTkFrame(self.monitor_frame, fg_color="transparent")
        timer_row.pack(fill="x", pady=25)

        # Left: Total Time Required (Added pady to labels to fix cramping)
        total_box = ctk.CTkFrame(timer_row, fg_color="transparent")
        total_box.pack(side="left", expand=True, padx=20)
        ctk.CTkLabel(total_box, text="TOTAL TIME REQUIRED", font=("Arial", 14, "bold"), text_color="#1B4965").pack(pady=(0, 10))
        ctk.CTkLabel(total_box, textvariable=self.total_req_time, font=("Courier", 60, "bold"), text_color="#1B4965").pack()

        # Right: Time Remaining (Added pady to labels to fix cramping)
        remain_box = ctk.CTkFrame(timer_row, fg_color="transparent")
        remain_box.pack(side="left", expand=True, padx=20)
        ctk.CTkLabel(remain_box, text="TIME REMAINING", font=("Arial", 14, "bold"), text_color="#1B4965").pack(pady=(0, 10))
        ctk.CTkLabel(remain_box, textvariable=self.time_remaining, font=("Courier", 60, "bold"), text_color="#E63946").pack()

        # Big Data Row (PSI & O2)
        data_row = ctk.CTkFrame(self.monitor_frame, fg_color="transparent")
        data_row.pack(fill="x", pady=(0, 25))
        
        psi_box = ctk.CTkFrame(data_row, fg_color="white", corner_radius=12, border_width=2, border_color="#1B4965")
        psi_box.pack(side="left", expand=True, padx=60, ipadx=15, ipady=8)
        ctk.CTkLabel(psi_box, text="SYSTEM PSI", font=("Arial", 12, "bold"), text_color="#1B4965").pack(pady=(0, 5))
        ctk.CTkLabel(psi_box, textvariable=self.sys_psi, font=("Courier", 42, "bold"), text_color="#1B4965").pack()
        
        o2_box = ctk.CTkFrame(data_row, fg_color="white", corner_radius=12, border_width=2, border_color="#1B4965")
        o2_box.pack(side="left", expand=True, padx=60, ipadx=15, ipady=8)
        ctk.CTkLabel(o2_box, text="O2 CONCENTRATION", font=("Arial", 12, "bold"), text_color="#1B4965").pack(pady=(0, 5))
        ctk.CTkLabel(o2_box, textvariable=self.sys_o2, font=("Courier", 42, "bold"), text_color="#1B4965").pack()

        # --- BOTTOM GRID: 8 STATIONS ---
        self.grid_frame = ctk.CTkFrame(self, fg_color="#F0F5F9")
        self.grid_frame.pack(fill="both", expand=True, padx=30, pady=20)

        for i, name in enumerate(STATION_NAMES):
            card = ctk.CTkFrame(self.grid_frame, border_width=1, border_color="#62B6CB", fg_color="white")
            card.grid(row=i//4, column=i%4, padx=6, pady=6, sticky="nsew")
            
            ctk.CTkLabel(card, text=name.upper(), font=("Arial", 11, "bold"), text_color="#1B4965").pack(pady=(8, 2))
            
            # Setting Icons (⚙) - Doubled size to width=60, height=40, font=28
            ctk.CTkButton(card, text="⚙", width=60, height=40, font=("Arial", 28), 
                                fg_color="transparent", text_color="#1B4965", hover_color="#CAE9FF",
                                command=lambda n=name: self.open_settings(n)).pack(pady=8)

        self.grid_frame.grid_columnconfigure((0,1,2,3), weight=1)
        self.grid_frame.grid_rowconfigure((0,1), weight=1)

    def open_settings(self, name):
        data = self.storage[name]
        popup = ctk.CTkToplevel(self)
        popup.title(f"Config: {name}")
        popup.geometry("380x350")
        popup.attributes("-topmost", True)
        
        is_monomer = name in ["Adenine", "Cytosine", "Guanine", "Thymine"]
        ctk.CTkLabel(popup, text=f"CALIBRATION: {name}", font=("Arial", 16, "bold")).pack(pady=15)

        if is_monomer:
            self.create_input(popup, "Activator Strike (ms):", data.activator_ms)
            self.create_input(popup, "Activator Advance (ms):", data.adv_release_ms)
            self.create_input(popup, "Monomer Strike (ms):", data.reagent_ms)
        else:
            self.create_input(popup, "Strike Duration (ms):", data.reagent_ms)
        
        ctk.CTkButton(popup, text="SAVE", width=100, fg_color="#1B4965", command=popup.destroy).pack(pady=20)

    def create_input(self, master, label_text, variable):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=4)
        ctk.CTkLabel(frame, text=label_text, font=("Arial", 11)).pack(side="left")
        ctk.CTkEntry(frame, textvariable=variable, width=60, height=22, justify="center").pack(side="right")

    def update_clocks(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_remaining.set(now)
        self.after(1000, self.update_clocks)

    def emergency_stop(self):
        print("HALTED")

if __name__ == "__main__":
    app = DNAMarkI()
    app.mainloop()
