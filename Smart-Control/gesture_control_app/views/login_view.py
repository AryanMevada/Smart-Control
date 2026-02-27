import customtkinter as ctk

TEXT = "#e6edf3"
ERR = "#f85149"
ACCENT = "#58a6ff"


class LoginView(ctk.CTkFrame):

    def __init__(self, parent, auth_controller, on_login_success):
        super().__init__(parent, fg_color="transparent")

        self.auth_controller = auth_controller
        self.on_login_success = on_login_success

        # Title
        ctk.CTkLabel(
            self,
            text="Welcome Back 👋",
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT
        ).pack(pady=20)

        # Username Entry
        self.username_entry = ctk.CTkEntry(
            self,
            placeholder_text="Username",
            height=40
        )
        self.username_entry.pack(padx=30, pady=10, fill="x")

        # Password Entry
        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*",
            height=40
        )
        self.password_entry.pack(padx=30, pady=10, fill="x")

        # Error / Status Label
        self.message_label = ctk.CTkLabel(
            self,
            text="",
            text_color=ERR
        )
        self.message_label.pack()

        # Login Button
        ctk.CTkButton(
            self,
            text="Sign In",
            fg_color=ACCENT,
            command=self.handle_login
        ).pack(padx=30, pady=20, fill="x")

        # Press Enter to login
        self.password_entry.bind("<Return>", lambda e: self.handle_login())

    # ---------------- LOGIN LOGIC ----------------
    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        success, message = self.auth_controller.login(username, password)

        if success:
            # Close auth window and open main app
            self.winfo_toplevel().destroy()
            self.on_login_success()
        else:
            self.message_label.configure(text=message)