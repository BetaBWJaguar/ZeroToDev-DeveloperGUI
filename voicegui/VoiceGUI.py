# -*- coding: utf-8 -*-
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from GUIHelper import section, primary_button, labeled_scale, styled_combobox
from data_manager.MemoryManager import MemoryManager
from fragments.UIFragments import center_window
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager
from GuideLabel import GuideLabel

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

        self.lang = parent.lang
        self.title(self.lang.get("voice_settings_title"))

        self.transient(parent)
        self.logger = LogsManager.get_logger("VoiceSettings")
        self.grab_set()
        self.resizable(False, False)

        self.presets = load_presets()

        container = ttk.Frame(self, padding=20, style="TFrame")
        container.pack(fill="both", expand=True)

        # --- Preset selection ---
        preset_card, preset_inner = section(container, self.lang.get("voice_settings_preset_section"))
        preset_card.pack(fill="x", pady=(0, 2))

        last_preset = MemoryManager.get("preset", "Default")
        self.preset_var = tk.StringVar(value=last_preset)
        translated_list = [self.translate_preset(name) for name in self.presets.keys()]

        original_to_display = {
            key: self.translate_preset(key) for key in self.presets.keys()
        }

        self.preset_var = tk.StringVar(
            value=original_to_display.get(MemoryManager.get("preset", "Default"))
        )

        preset_frame, preset_combo = styled_combobox(
            preset_inner,
            self.lang.get("voice_settings_preset_label"),
            self.preset_var,
            translated_list
        )
        preset_frame.pack(fill="x", pady=(0, 0))

        GuideLabel(preset_inner, self.lang.get("voice_settings_preset_guide"))

        preset_combo.bind("<<ComboboxSelected>>", self.apply_preset)

        param_card, param_inner = section(container, self.lang.get("voice_settings_params_section"))
        param_card.pack(fill="x", pady=(0, 15))

        self.pitch_var = tk.DoubleVar(value=MemoryManager.get("pitch", 0))
        self.pitch_var.trace_add("write", lambda *_: self._on_param_change("pitch", self.pitch_var.get()))
        labeled_scale(param_inner, self.lang.get("voice_settings_pitch_label"), self.pitch_var, -10, 10).pack(fill="x")
        GuideLabel(param_inner, self.lang.get("voice_settings_pitch_guide"))

        self.speed_var = tk.DoubleVar(value=MemoryManager.get("speed", 1.0))
        self.speed_var.trace_add("write", lambda *_: self._on_param_change("speed", self.speed_var.get()))
        labeled_scale(param_inner, self.lang.get("voice_settings_speed_label"), self.speed_var, 0.5, 2.0).pack(fill="x")
        GuideLabel(param_inner, self.lang.get("voice_settings_speed_guide"))

        self.volume_var = tk.DoubleVar(value=MemoryManager.get("volume", 1.0))
        self.volume_var.trace_add("write", lambda *_: self._on_param_change("volume", self.volume_var.get()))
        labeled_scale(param_inner, self.lang.get("voice_settings_volume_label"), self.volume_var, 0.5, 2.0).pack(fill="x")
        GuideLabel(param_inner, self.lang.get("voice_settings_volume_guide"))

        effect_card, effect_inner = section(container, self.lang.get("voice_settings_effects_section"))
        effect_card.pack(fill="x", pady=(0, 15))

        self.echo_var = tk.BooleanVar(value=MemoryManager.get("echo", False))
        self.echo_var.trace_add("write", lambda *_: self._on_param_change("echo", self.echo_var.get()))
        ttk.Checkbutton(effect_inner, text=self.lang.get("voice_settings_echo_label"), variable=self.echo_var,
                        style="Option.TRadiobutton").pack(anchor="w", pady=2)
        GuideLabel(effect_inner, self.lang.get("voice_settings_echo_guide"))

        self.reverb_var = tk.BooleanVar(value=MemoryManager.get("reverb", False))
        self.reverb_var.trace_add("write", lambda *_: self._on_param_change("reverb", self.reverb_var.get()))
        ttk.Checkbutton(effect_inner, text=self.lang.get("voice_settings_reverb_label"), variable=self.reverb_var,
                        style="Option.TRadiobutton").pack(anchor="w", pady=2)
        GuideLabel(effect_inner, self.lang.get("voice_settings_reverb_guide"))

        self.robot_var = tk.BooleanVar(value=MemoryManager.get("robot", False))
        self.robot_var.trace_add("write", lambda *_: self._on_param_change("robot", self.robot_var.get()))
        ttk.Checkbutton(effect_inner, text=self.lang.get("voice_settings_robot_label"), variable=self.robot_var,
                        style="Option.TRadiobutton").pack(anchor="w", pady=2)
        GuideLabel(effect_inner, self.lang.get("voice_settings_robot_guide"))

        # --- Close button ---
        primary_button(container, self.lang.get("close_button"), self.destroy).pack(pady=(10, 0))

        self.update_idletasks()
        parent.update()
        center_window(self, parent)

    def apply_preset(self, *_):
        display_name = self.preset_var.get()
        preset_name = self.reverse_translate_preset(display_name)

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

        LogsHelperManager.log_event(self.logger, "PRESET_APPLY", {"preset": preset_name})

    def _on_param_change(self, key, value, delay=800):
        old_value = MemoryManager.get(key, None)
        MemoryManager.set(key, value)

        if not hasattr(self, "_pending_logs"):
            self._pending_logs = {}

        if key in self._pending_logs:
            self.after_cancel(self._pending_logs[key])

        def do_log():
            LogsHelperManager.log_config_change(self.logger, key, old_value, value)
            if key in self._pending_logs:
                del self._pending_logs[key]

        self._pending_logs[key] = self.after(delay, do_log)

    def translate_preset(self, key: str) -> str:
        lang_key = "preset_" + key.lower().replace(" ", "_")
        return self.lang.get(lang_key)

    def reverse_translate_preset(self, display_value: str) -> str:
        for key in self.presets.keys():
            if self.translate_preset(key) == display_value:
                return key
        return display_value
