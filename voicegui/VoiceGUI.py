# -*- coding: utf-8 -*-
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from GUIHelper import section, primary_button, labeled_scale, styled_combobox
from data_manager.MemoryManager import MemoryManager
from fragments.UIFragments import center_window

PRESET_FILE = Path(__file__).resolve().parent.parent / "utils" / "Preset-Default.json"


def load_presets():
    try:
        with open(PRESET_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


class VoiceSettings(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Voice Settings")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.presets = load_presets()

        container = ttk.Frame(self, padding=20, style="TFrame")
        container.pack(fill="both", expand=True)

        preset_card, preset_inner = section(container, "Presets Selecting")
        preset_card.pack(fill="x", pady=(0, 2))

        last_preset = MemoryManager.get("preset", "Default")
        self.preset_var = tk.StringVar(value=last_preset)
        preset_frame, preset_combo = styled_combobox(
            preset_inner, "Presets", self.preset_var, list(self.presets.keys())
        )
        preset_frame.pack(fill="x", pady=(0, 0))
        preset_combo.bind("<<ComboboxSelected>>", self.apply_preset)

        # --- Voice parameters ---
        param_card, param_inner = section(container, "Voice Parameters")
        param_card.pack(fill="x", pady=(0, 15))


        self.pitch_var = tk.DoubleVar(value=MemoryManager.get("pitch", 0))
        self.pitch_var.trace_add("write", lambda *_: MemoryManager.set("pitch", self.pitch_var.get()))
        labeled_scale(param_inner, "Pitch", self.pitch_var, -10, 10).pack(fill="x")


        self.speed_var = tk.DoubleVar(value=MemoryManager.get("speed", 1.0))
        self.speed_var.trace_add("write", lambda *_: MemoryManager.set("speed", self.speed_var.get()))
        labeled_scale(param_inner, "Speed", self.speed_var, 0.5, 2.0).pack(fill="x")


        self.volume_var = tk.DoubleVar(value=MemoryManager.get("volume", 1.0))
        self.volume_var.trace_add("write", lambda *_: MemoryManager.set("volume", self.volume_var.get()))
        labeled_scale(param_inner, "Volume", self.volume_var, 0.5, 2.0).pack(fill="x")


        effect_card, effect_inner = section(container, "Voice Effects")
        effect_card.pack(fill="x", pady=(0, 15))


        self.echo_var = tk.BooleanVar(value=MemoryManager.get("echo", False))
        self.echo_var.trace_add("write", lambda *_: MemoryManager.set("echo", self.echo_var.get()))
        ttk.Checkbutton(effect_inner, text="Echo", variable=self.echo_var,
                        style="Option.TRadiobutton").pack(anchor="w", pady=2)


        self.reverb_var = tk.BooleanVar(value=MemoryManager.get("reverb", False))
        self.reverb_var.trace_add("write", lambda *_: MemoryManager.set("reverb", self.reverb_var.get()))
        ttk.Checkbutton(effect_inner, text="Reverb", variable=self.reverb_var,
                        style="Option.TRadiobutton").pack(anchor="w", pady=2)

        self.robot_var = tk.BooleanVar(value=MemoryManager.get("robot", False))
        self.robot_var.trace_add("write", lambda *_: MemoryManager.set("robot", self.robot_var.get()))
        ttk.Checkbutton(effect_inner, text="Robotize", variable=self.robot_var,
                        style="Option.TRadiobutton").pack(anchor="w", pady=2)

        primary_button(container, "Close", self.destroy).pack(pady=(10, 0))


        self.update_idletasks()
        parent.update()
        center_window(self, parent)

    def apply_preset(self, *_):
        preset_name = self.preset_var.get()
        MemoryManager.set("preset", preset_name)
        preset = self.presets.get(preset_name, {})
        if not preset:
            return

        self.pitch_var.set(preset.get("pitch", 0))
        self.speed_var.set(preset.get("speed", 1.0))
        self.volume_var.set(preset.get("volume", 1.0))

        self.echo_var.set(preset.get("echo", False))
        self.reverb_var.set(preset.get("reverb", False))
        self.robot_var.set(preset.get("robot", False))
