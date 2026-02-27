import tkinter as tk
from models.gesture_data import GESTURE_INFO


class InstructionView:
    """
    Instruction popup for a selected mode.
    """

    def __init__(self, root, controller, mode_name):
        self.controller = controller
        self.mode_name = mode_name

        self.window = tk.Toplevel(root)
        self.window.title(f"{mode_name} Instructions")
        self.window.geometry("550x420")
        self.window.configure(bg="#121212")
        self.window.resizable(False, False)

        self._build_layout()

    def _build_layout(self):

        tk.Label(
            self.window,
            text=f"{self.mode_name} Instructions",
            font=("Segoe UI", 18, "bold"),
            bg="#121212",
            fg="white"
        ).pack(pady=20)

        tk.Label(
            self.window,
            text=GESTURE_INFO.get(self.mode_name, "No instructions available."),
            font=("Segoe UI", 12),
            bg="#121212",
            fg="#cccccc",
            justify="left"
        ).pack(pady=10)

        tk.Button(
            self.window,
            text="Start Mode",
            font=("Segoe UI", 11, "bold"),
            bg="#00aa66",
            fg="white",
            bd=0,
            width=15,
            height=2,
            command=self._start_mode
        ).pack(pady=20)

        tk.Button(
            self.window,
            text="Back",
            font=("Segoe UI", 10),
            bg="#444444",
            fg="white",
            bd=0,
            width=15,
            height=2,
            command=self.window.destroy
        ).pack()

    def _start_mode(self):
        self.window.destroy()
        self.controller.start_mode(self.mode_name)