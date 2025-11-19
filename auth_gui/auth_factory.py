def MainAuthFactory(lang_manager, logger):
    from auth_gui.MainAuthGUI import MainAuthGUI
    app = MainAuthGUI(lang_manager, logger)
    app.mainloop()
