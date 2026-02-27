import sys
from threading import Thread

from models.app_state import AppState
from models.mode_registry import MODE_REGISTRY

from views.main_view import MainView
from views.instruction_view import InstructionView


class AppController:
    """
    Central controller of Smart Control.
    Handles:
    - Mode switching
    - Thread management
    - View communication
    - Application lifecycle
    """

    def __init__(self):
        self.state = AppState()
        self.view = MainView(self)
        self.mode_thread = None

    # ================= APP START =================
    def run(self):
        self.view.start()

    # ================= SHOW INSTRUCTIONS =================
    def show_instructions(self, mode_name):
        InstructionView(self.view.root, self, mode_name)

    # ================= START MODE =================
    def start_mode(self, mode_name):

        if self.state.mode_running:
            self.view.update_status(
                "⚠ A mode is already running",
                "#ff4d4d"
            )
            return

        self.state.start_mode(mode_name)
        self.view.update_status(
            f"Running: {mode_name}",
            "#00ffcc"
        )

        self.mode_thread = Thread(
            target=self._run_mode_thread,
            args=(mode_name,)
        )
        self.mode_thread.daemon = True
        self.mode_thread.start()

    # ================= THREAD WRAPPER =================
    def _run_mode_thread(self, mode_name):
        try:
            mode_function = MODE_REGISTRY.get(mode_name)

            if mode_function:
                mode_function()

        finally:
            # When camera window closes
            self.state.stop_mode()
            self.view.update_status(
                "System Ready",
                "#aaaaaa"
            )

    # ================= STOP MODE (Optional future feature) =================
    def stop_mode(self):
        # Currently modes close via ESC in camera window
        self.view.update_status(
            "Close camera window to stop mode",
            "#ffaa00"
        )

    # ================= EXIT APP =================
    def exit_app(self):
        sys.exit()