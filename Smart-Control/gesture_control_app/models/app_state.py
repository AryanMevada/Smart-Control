class AppState:
    """
    Stores the runtime state of the application.
    This is the single source of truth for:
    - current running mode
    - whether a mode is active
    """

    def __init__(self):
        self.current_mode = None
        self.mode_running = False

    def start_mode(self, mode_name):
        self.current_mode = mode_name
        self.mode_running = True

    def stop_mode(self):
        self.current_mode = None
        self.mode_running = False