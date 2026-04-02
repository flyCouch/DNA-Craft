# ==============================================================================
# PROJECT:   DNA_MARK_I_V17_PROFILE_VISIBILITY
# THEME:     Clinical Blue / Medical White
# FOCUS:     Active Profile Display / JSON I/O / Restored UI Scaling
# __FILE__:  DNAprinter1.py
# __DATE__:  2026-04-02
# __TIME__:  20:15:00
# ==============================================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
from datetime import datetime

STATION_NAMES = ["Adenine", "Cytosine", "Guanine", "Thymine", "Oxidizer", "Capping", "Deblock", "WASH"]

class StationData:
    def __init__(self, name, i):
        self.name = name
        self.reagent_ms = ctk.IntVar(value=250)
        self.activator_ms = ctk.IntVar(value=250)
        self.adv_release_ms = ctk.IntVar(value=50)
        self.r_deg = ctk.DoubleVar(value=float(i * 45)) 
        self.x_pos = ctk.DoubleVar(value=20.0)          

class DNAMarkI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Lyttle reSearch DNA Crafting Control")
        self.geometry("1450x1000")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.storage = {name: StationData(name, i) for i, name in enumerate(STATION_NAMES)}
        
        # System State
        self.raw_sequence = ctk.StringVar(value="")
        self.active_profile_name = ctk.StringVar(value="DEFAULT_STATIONS")
        self.total_req_time = ctk.StringVar(value="00:00:00")
        self.time_remaining = ctk.StringVar(value="00:00:00")
        self.jog_step = ctk.StringVar(value="1.0") 
        self.active_station = ctk.StringVar(value="WASH")

        self.setup_ui()
        self.update_clocks()

    def setup_ui(self):
        # --- TOP PANEL: MISSION CONTROL ---
        self.top_panel = ctk.CTkFrame(self, height=180, corner_radius=0, fg_color="#1B4965")
        self.top_panel.pack(side="top", fill="x")

        # 1. Station Profiles (With Active Display)
        self.profile_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        self.profile_frame.pack(side="left", padx=20)
        ctk.CTkLabel(self.profile_frame, text="STATION PROFILES", text_color="#62B6CB", font=("Arial", 10, "bold")).pack()
        
        # Profile Status Box
        self.profile_display = ctk.CTkEntry(self.profile_frame, textvariable=self.active_profile_name, width=160, font=("Arial", 11, "italic"), fg_color="#12344D", text_color="#BEE9E8", state="readonly")
        self.profile_display.pack(pady=2)
        
        ctk.CTkButton(self.profile_frame, text="LOAD PROFILE", fg_color="#62B6CB", text_color="black", font=("Arial", 11, "bold"), width=160, command=self.load_station_profile).pack(pady=2)
        ctk.CTkButton(self.profile_frame, text="SAVE PROFILE", fg_color="#62B6CB", text_color="black", font=("Arial", 11, "bold"), width=160, command=self.save_station_profile).pack(pady=2)

        # 2. File Management
        self.file_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        self.file_frame.pack(side="left", padx=10)
        ctk.CTkLabel(self.file_frame, text="FILE OPS", text_color="#5FA8D3", font=("Arial", 10, "bold")).pack()
        ctk.CTkButton(self.file_frame, text="LOAD SEQUENCE", fg_color="#5FA8D3", text_color="black", font=("Arial", 11, "bold"), width=140, command=self.load_sequence_file).pack(pady=2)
        ctk.CTkButton(self.file_frame, text="LOAD G-CODE", fg_color="#5FA8D3", text_color="black", font=("Arial", 11, "bold"), width=140, command=self.load_gcode_file).pack(pady=2)
        ctk.CTkButton(self.file_frame, text="SLICE & SAVE", fg_color="#BEE9E8", text_color="black", font=("Arial", 11, "bold"), width=140, command=self.slice_to_gcode).pack(pady=2)

        # 3. Sequence Entry
        self.seq_entry = ctk.CTkEntry(self.top_panel, textvariable=self.raw_sequence, width=320, font=("Courier", 14))
        self.seq_entry.pack(side="left", padx=20)

        # 4. Control Cluster (START / STOP)
        self.control_frame = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        self.control_frame.pack(side="right", padx=30)
        self.start_btn = ctk.CTkButton(self.control_frame, text="START", fg_color="#2D6A4F", width=150, height=110, font=("Arial", 30, "bold"), command=self.start_synthesis)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = ctk.CTkButton(self.control_frame, text="STOP", fg_color="#E63946", width=150, height=110, font=("Arial", 30, "bold"), command=self.emergency_stop)
        self.stop_btn.pack(side="left", padx=5)

        # --- MONITORING PANEL ---
        self.monitor_frame = ctk.CTkFrame(self, fg_color="#BEE9E8", corner_radius=0)
        self.monitor_frame.pack(fill="x")
        timer_row = ctk.CTkFrame(self.monitor_frame, fg_color="transparent")
        timer_row.pack(fill="x", pady=10)
        self.create_timer_box(timer_row, "TOTAL CYCLE", self.total_req_time, "#1B4965")
        self.create_timer_box(timer_row, "REMAINING", self.time_remaining, "#E63946")

        # --- MOTION CONTROL PANEL ---
        self.motion_frame = ctk.CTkFrame(self, fg_color="#CAE9FF", corner_radius=0)
        self.motion_frame.pack(fill="x")
        inner_motion = ctk.CTkFrame(self.motion_frame, fg_color="transparent")
        inner_motion.pack(pady=15, padx=20, fill="x")

        # Jog & Home
        jog_ctrl = ctk.CTkFrame(inner_motion, fg_color="white", border_width=1, border_color="#1B4965")
        jog_ctrl.pack(side="left", padx=10)
        ctk.CTkButton(jog_ctrl, text="HOME ALL", fg_color="#1B4965", text_color="white", font=("Arial", 14, "bold"), height=45, command=self.home_axes).pack(pady=5, padx=10, fill="x")
        step_row = ctk.CTkFrame(jog_ctrl, fg_color="transparent")
        step_row.pack()
        for s in ["0.1", "1.0", "10.0"]:
            ctk.CTkRadioButton(step_row, text=s, variable=self.jog_step, value=s, font=("Arial", 11)).pack(side="left", padx=5)
        btn_grid = ctk.CTkFrame(jog_ctrl, fg_color="transparent")
        btn_grid.pack(pady=5, padx=10)
        for i, ax in enumerate(["R", "X", "Z"]):
            ctk.CTkButton(btn_grid, text=f"{ax}-", width=60, height=38, command=lambda a=ax: self.jog(a, -1)).grid(row=i, column=0, padx=2, pady=2)
            ctk.CTkButton(btn_grid, text=f"{ax}+", width=60, height=38, command=lambda a=ax: self.jog(a, 1)).grid(row=i, column=1, padx=2, pady=2)

        # Station Radio (Box Fill)
        snap_ctrl = ctk.CTkFrame(inner_motion, fg_color="white", border_width=1, border_color="#1B4965")
        snap_ctrl.pack(side="left", expand=True, fill="both", padx=10)
        ctk.CTkLabel(snap_ctrl, text="STATION SNAP-ALIGNMENT", font=("Arial", 14, "bold")).pack(pady=8)
        radio_grid = ctk.CTkFrame(snap_ctrl, fg_color="transparent")
        radio_grid.pack(expand=True, fill="both", padx=10, pady=5)
        radio_grid.grid_columnconfigure((0,1,2,3), weight=1)
        radio_grid.grid_rowconfigure((0,1), weight=1)
        for i, name in enumerate(STATION_NAMES):
            ctk.CTkRadioButton(radio_grid, text=name.upper(), variable=self.active_station, value=name, font=("Arial", 15, "bold"),
                               radiobutton_width=26, radiobutton_height=26, command=lambda n=name: self.snap_to(n)).grid(row=i//4, column=i%4, padx=15, pady=18, sticky="nsew")

        # --- STATION CONFIG CARDS ---
        self.grid_frame = ctk.CTkFrame(self, fg_color="#F0F5F9")
        self.grid_frame.pack(fill="both", expand=True, padx=30, pady=20)
        for i, name in enumerate(STATION_NAMES):
            card = ctk.CTkFrame(self.grid_frame, border_width=1, border_color="#62B6CB", fg_color="white")
            card.grid(row=i//4, column=i%4, padx=8, pady=8, sticky="nsew")
            ctk.CTkLabel(card, text=name.upper(), font=("Arial", 12, "bold"), text_color="#1B4965").pack(pady=(12, 5))
            ctk.CTkButton(card, text="⚙", width=90, height=55, font=("Arial", 36), fg_color="transparent", text_color="#1B4965", hover_color="#CAE9FF", command=lambda n=name: self.open_settings(n)).pack(pady=12)

        self.grid_frame.grid_columnconfigure((0,1,2,3), weight=1)
        self.grid_frame.grid_rowconfigure((0,1), weight=1)

    # --- PROFILE I/O ---
    def save_station_profile(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Profile", "*.json")])
        if not path: return
        profile_data = {}
        for name, data in self.storage.items():
            profile_data[name] = {
                "reagent_ms": data.reagent_ms.get(),
                "activator_ms": data.activator_ms.get(),
                "adv_release_ms": data.adv_release_ms.get(),
                "r_deg": data.r_deg.get(),
                "x_pos": data.x_pos.get()
            }
        with open(path, 'w') as f:
            json.dump(profile_data, f, indent=4)
        
        self.active_profile_name.set(os.path.basename(path).upper())
        messagebox.showinfo("Profile", f"Saved: {os.path.basename(path)}")

    def load_station_profile(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Profile", "*.json")])
        if not path: return
        try:
            with open(path, 'r') as f:
                profile_data = json.load(f)
                for name, vals in profile_data.items():
                    if name in self.storage:
                        self.storage[name].reagent_ms.set(vals["reagent_ms"])
                        self.storage[name].activator_ms.set(vals["activator_ms"])
                        self.storage[name].adv_release_ms.set(vals["adv_release_ms"])
                        self.storage[name].r_deg.set(vals["r_deg"])
                        self.storage[name].x_pos.set(vals["x_pos"])
            
            self.active_profile_name.set(os.path.basename(path).upper())
            messagebox.showinfo("Profile", f"Loaded: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile: {e}")

    # --- ACTION WRAPPERS ---
    def load_gcode_file(self):
        path = filedialog.askopenfilename(filetypes=[("G-code", "*.gcode")])
        if path: messagebox.showinfo("G-Code", f"Active: {os.path.basename(path)}")

    def load_sequence_file(self): self.raw_sequence.set("LOADED_SEQ_V1")
    def slice_to_gcode(self): print("Slicing...")
    def home_axes(self): self.active_station.set("WASH")
    def start_synthesis(self): print("STARTING MISSION")
    def emergency_stop(self): print("HALT")
    def jog(self, axis, dir): print(f"JOG {axis} {dir}")
    def snap_to(self, s): print(f"SNAP {s}")

    def create_timer_box(self, parent, label, var, color):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(side="left", expand=True)
        ctk.CTkLabel(box, text=label, font=("Arial", 12, "bold"), text_color="#1B4965").pack()
        ctk.CTkLabel(box, textvariable=var, font=("Courier", 55, "bold"), text_color=color).pack()

    def update_clocks(self):
        self.time_remaining.set(datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_clocks)

    def open_settings(self, name):
        data = self.storage[name]
        popup = ctk.CTkToplevel(self)
        popup.title(f"Config: {name}")
        popup.geometry("400x520")
        popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text=f"STATION {name.upper()}", font=("Arial", 16, "bold")).pack(pady=10)
        self.create_input(popup, "Valve (ms):", data.reagent_ms)
        if name in ["Adenine", "Cytosine", "Guanine", "Thymine"]:
            self.create_input(popup, "Activator (ms):", data.activator_ms)
            self.create_input(popup, "Advance (ms):", data.adv_release_ms)
        self.create_input(popup, "Rotary (deg):", data.r_deg)
        self.create_input(popup, "X-Pos (mm):", data.x_pos)
        ctk.CTkButton(popup, text="SAVE", command=popup.destroy).pack(pady=20)

    def create_input(self, master, label, var):
        f = ctk.CTkFrame(master, fg_color="transparent"); f.pack(fill="x", padx=50, pady=3)
        ctk.CTkLabel(f, text=label).pack(side="left")
        ctk.CTkEntry(f, textvariable=var, width=60).pack(side="right")

if __name__ == "__main__":
    DNAMarkI().mainloop()
