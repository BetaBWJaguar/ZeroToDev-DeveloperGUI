import tkinter as tk
from tkinter import ttk
from GUI import TTSMenuApp
from STTGUI import STTMenuApp
from GUIError import GUIError
from ai_system.data_collection.DataCollectionDatabaseManager import DataCollectionDatabaseManager
from ai_system.data_collection.DataCollectionManager import DataCollectionManager
from ai_system.providers.TimedProviders import TimedProvider
from fragments.UIFragments import center_window, apply_auth_style
from logs_manager.LogsHelperManager import LogsHelperManager
from data_manager.MemoryManager import MemoryManager
from usermanager.UserManager import UserManager
from auth_gui.auth_factory import MainAuthFactory
from auth_gui.ResetPasswordGUI import ResetPasswordGUI
from auth_gui.RegisterGUI import RegisterGUI
from ai_system.providers.ProviderRegistry import ProviderRegistry
from ai_system.providers.DeepInfraProvider import DeepInfraProvider
from ai_system.config.AIConfig import AIConfig


class LoginGUI(tk.Tk):
    def __init__(self, lang_manager, logger):
        super().__init__()

        apply_auth_style(self)

        self.lang = lang_manager
        self.logger = logger
        self.user_manager = UserManager(self.lang)

        self.title(self.lang.get("auth_login_title"))
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.go_back)

        container = ttk.Frame(self, padding=25, style="AuthCard.TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=self.lang.get("auth_login_header"),
                  style="AuthTitle.TLabel").pack(anchor="center", pady=(0, 15))

        ttk.Label(container, text=self.lang.get("auth_field_username"),
                  style="AuthLabel.TLabel").pack(anchor="w")
        self.username_var = tk.StringVar(value=MemoryManager.get("cached_username", ""))
        ttk.Entry(container, textvariable=self.username_var,
                  style="Auth.TEntry").pack(fill="x", pady=(0, 10))

        ttk.Label(container, text=self.lang.get("auth_field_password"),
                  style="AuthLabel.TLabel").pack(anchor="w")
        self.pass_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.pass_var,
                  show="*", style="Auth.TEntry").pack(fill="x")

        self.error_label = ttk.Label(container, text="", foreground="#d9534f",
                                     style="AuthLabel.TLabel")
        self.error_label.pack(anchor="w", pady=(10, 10))

        ttk.Button(container, text=self.lang.get("auth_login_button"),
                   style="AuthAccent.TButton",
                   command=self.login).pack(fill="x", pady=(0, 8))

        ttk.Button(container, text=self.lang.get("auth_forgot_password"),
                   style="Auth.TButton",
                   command=self.open_reset_password).pack(fill="x", pady=(0, 8))

        ttk.Button(container, text=self.lang.get("auth_register_button"),
                   style="Auth.TButton",
                   command=self.open_register).pack(fill="x")

        ttk.Button(container, text=self.lang.get("auth_back_button"),
                   style="Auth.TButton",
                   command=self.go_back).pack(fill="x", pady=(10, 0))

        center_window(self)


    def open_reset_password(self):
        self.destroy()
        ResetPasswordGUI(self.lang, self.logger)

    def open_twofa_window(self,user_obj):
        from usermanager.verfiy_manager.twofa_manager.TwoFAVerifyGUI import TwoFAVerifyGUI
        TwoFAVerifyGUI(self,user_obj,self.lang)


    def open_register(self):
        self.destroy()
        RegisterGUI(self.lang, self.logger)

    def go_back(self):
        self.destroy()
        MainAuthFactory(self.lang, self.logger)

    def login(self):
        LogsHelperManager.log_button(self.logger, "LOGIN_ATTEMPT")

        username = self.username_var.get().strip()
        password = self.pass_var.get().strip()

        if not username or not password:
            msg = self.lang.get("auth_error_empty_fields")
            self.error_label.config(text=msg)
            GUIError(self, self.lang.get("error_title"), msg, "❌", mode='auth')
            return

        result = self.user_manager.login_user(username, password)

        if isinstance(result, str):
            GUIError(self, self.lang.get("auth_login_failed"), result, "❌", mode='auth')
            return

        user_obj = result

        if user_obj.id.get("twofa_enabled"):
            self.open_twofa_window(user_obj)
            return

        MemoryManager.set("cached_username", username)
        LogsHelperManager.log_success(self.logger, "LOGIN_SUCCESS", {"user": result.username})

        try:
            config = AIConfig.load()
            provider_config = config.get("provider", {})

            api_key = provider_config.get("api_key", "")

            deepinfra_provider = DeepInfraProvider(
                api_key=api_key,
                model=provider_config.get("model")
            )

            timed_provider = TimedProvider(
                provider=deepinfra_provider,
                provider_name="deepinfra"
            )

            ProviderRegistry.register(timed_provider)

            LogsHelperManager.log_success(self.logger, "AI_PROVIDER_INITIALIZED", {
                "provider": "deepinfra",
                "model": provider_config.get("model")
            })

            try:
                runtime_collector = DataCollectionManager()
                db_collector = DataCollectionDatabaseManager()

                payload = {
                    "preferences": {
                        "tts": runtime_collector.get_tts_preferences(),
                        "stt": runtime_collector.get_stt_preferences()
                    },
                    "usage_statistics": runtime_collector.get_usage_statistics(),
                    "behavior": runtime_collector.get_behavior_for_ai(),
                    "system_usage": runtime_collector.get_system_usage_data(),
                    "output_files": runtime_collector.get_output_files(limit=1000)
                }

                user_id = user_obj.id.get("id", user_obj.id)

                db_collector.collect_and_save_user_data(user_id, payload)

                LogsHelperManager.log_success(
                    self.logger,
                    "USER_SNAPSHOT_SAVED",
                    {"user": user_obj.username}
                )

            except Exception as snapshot_err:
                LogsHelperManager.log_error(
                    self.logger,
                    "USER_SNAPSHOT_FAILED",
                    str(snapshot_err)
                )

        except Exception as e:
            LogsHelperManager.log_error(
                self.logger,
                "AI_PROVIDER_INIT_FAILED",
                str(e)
            )

        self.destroy()

        selected_mode = MemoryManager.get("app_mode", "TTS")
        
        if selected_mode == "STT":
            app = STTMenuApp(lang_manager=self.lang, current_user=user_obj, user_manager=self.user_manager)
        else:
            app = TTSMenuApp(lang_manager=self.lang, current_user=user_obj, user_manager=self.user_manager)
           
        print("DEBUG USER:", user_obj.id if isinstance(user_obj.id, dict) else {})
        print("DEBUG MODE:", selected_mode)
        app.mainloop()
