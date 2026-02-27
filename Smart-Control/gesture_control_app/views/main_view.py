import tkinter as tk
from views.sidebar_view import SidebarView


class MainView:
    """
    Main application window.
    Responsible for layout and status updates.
    """

    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Smart Control")
        self.root.geometry("950x600")
        self.root.configure(bg="#121212")
        self.root.resizable(False, False)

        self.status_label = None
        self._build_layout()

    def _build_layout(self):
        # Sidebar
        SidebarView(self.root, self.controller)

        # Main Content Area
        main_area = tk.Frame(self.root, bg="#121212")
        main_area.pack(side="right", fill="both", expand=True)

        title = tk.Label(
            main_area,
            text="Smart Control",
            font=("Segoe UI", 28, "bold"),
            bg="#121212",
            fg="white"
        )
        title.pack(pady=40)

        subtitle = tk.Label(
            main_area,
            text="Powered by Computer Vision",
            font=("Segoe UI", 14),
            bg="#121212",
            fg="#888888"
        )
        subtitle.pack(pady=10)

        self.status_label = tk.Label(
            main_area,
            text="System Ready",
            font=("Segoe UI", 13),
            bg="#121212",
            fg="#aaaaaa"
        )
        self.status_label.pack(pady=30)

        footer = tk.Label(
            main_area,
            text="Smart Control v1.0  |  Built by L.A",
            font=("Segoe UI", 9),
            bg="#121212",
            fg="#555555"
        )
        footer.pack(side="bottom", pady=15)

    def update_status(self, text, color="#aaaaaa"):
        self.status_label.config(text=text, fg=color)

    def start(self):
        self.root.mainloop()