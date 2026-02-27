import tkinter as tk


class SidebarView:
    """
    Left navigation sidebar.
    Only UI. Calls controller methods.
    """

    def __init__(self, root, controller):
        self.controller = controller

        sidebar = tk.Frame(root, bg="#1a1a1a", width=280)
        sidebar.pack(side="left", fill="y")

        tk.Label(
            sidebar,
            text="Smart Control",
            font=("Segoe UI", 16, "bold"),
            bg="#1a1a1a",
            fg="white"
        ).pack(pady=20)

        modes = ["Mouse", "Keyboard", "Media", "Volume", "Presentation"]

        for mode in modes:
            tk.Button(
                sidebar,
                text=mode,
                font=("Segoe UI", 11),
                bg="#1a1a1a",
                fg="white",
                bd=0,
                height=2,
                activebackground="#333333",
                command=lambda m=mode: controller.show_instructions(m)
            ).pack(fill="x", pady=5)

        tk.Frame(sidebar, bg="#333333", height=1).pack(fill="x", pady=20)

        tk.Button(
            sidebar,
            text="Exit",
            font=("Segoe UI", 11),
            bg="#1a1a1a",
            fg="white",
            bd=0,
            height=2,
            activebackground="#333333",
            command=controller.exit_app
        ).pack(side="bottom", fill="x", pady=10)