import customtkinter as ctk
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG       = "#0d1117"
CARD     = "#161b22"
ACCENT   = "#58a6ff"
ACCENT2  = "#3fb950"
TEXT     = "#e6edf3"
SUBTEXT  = "#8b949e"
INPUT_BG = "#21262d"
ERR      = "#f85149"
BORDER   = "#30363d"


class AuthView(ctk.CTk):

    def __init__(self, auth_controller, on_login_success):
        super().__init__()

        self.auth_controller = auth_controller
        self.on_login_success = on_login_success

        self.title("Smart Control — Authentication")
        self.geometry("480x640")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self._center()
        self._build_header()
        self._build_tabs()
        self._build_card()
        self._build_footer()

    # ---------------- CENTER ----------------
    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 480) // 2
        y = (self.winfo_screenheight() - 640) // 2
        self.geometry(f"480x640+{x}+{y}")

    # ---------------- HEADER ----------------
    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=BG)
        hdr.pack(fill="x", pady=(24, 0))

        ctk.CTkLabel(hdr, text="🤖",
                     font=("Segoe UI Emoji", 40),
                     text_color=ACCENT).pack()

        ctk.CTkLabel(hdr, text="Smart Control",
                     font=("Segoe UI", 24, "bold"),
                     text_color=TEXT).pack()

        ctk.CTkLabel(hdr, text="Gesture-Powered Desktop Experience",
                     font=("Segoe UI", 11),
                     text_color=SUBTEXT).pack()

    # ---------------- TABS ----------------
    def _build_tabs(self):
        tf = ctk.CTkFrame(self, fg_color=BG)
        tf.pack(pady=(20, 0))

        self.login_tab = ctk.CTkButton(
            tf, text="Login", width=140,
            fg_color=ACCENT,
            command=self._show_login)
        self.login_tab.grid(row=0, column=0, padx=4)

        self.reg_tab = ctk.CTkButton(
            tf, text="Register", width=140,
            fg_color=INPUT_BG,
            command=self._show_register)
        self.reg_tab.grid(row=0, column=1, padx=4)

    # ---------------- CARD ----------------
    def _build_card(self):
        self.card = ctk.CTkFrame(
            self, fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDER)
        self.card.pack(padx=40, pady=16, fill="both", expand=True)

        self.login_frame = self._make_login_frame()
        self.reg_frame = self._make_register_frame()

        self._show_login()

    # ---------------- LOGIN UI ----------------
    def _make_login_frame(self):
        f = ctk.CTkFrame(self.card, fg_color="transparent")

        ctk.CTkLabel(f, text="Welcome back 👋",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT).pack(pady=20)

        self.login_user = self._entry(f, "Username")
        self.login_user.pack(padx=28, fill="x", pady=6)

        self.login_pass = self._entry(f, "Password", show="*")
        self.login_pass.pack(padx=28, fill="x", pady=6)
        self.login_pass.bind("<Return>", lambda e: self.handle_login())

        self.login_msg = ctk.CTkLabel(f, text="", text_color=ERR)
        self.login_msg.pack()

        ctk.CTkButton(
            f, text="Sign In",
            fg_color=ACCENT,
            command=self.handle_login
        ).pack(padx=28, fill="x", pady=10)

        return f

    # ---------------- REGISTER UI ----------------
    def _make_register_frame(self):
        f = ctk.CTkFrame(self.card, fg_color="transparent")

        ctk.CTkLabel(f, text="Create Account ✨",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT).pack(pady=20)

        self.reg_user = self._entry(f, "Username")
        self.reg_user.pack(padx=28, fill="x", pady=6)

        self.reg_pass = self._entry(f, "Password", show="*")
        self.reg_pass.pack(padx=28, fill="x", pady=6)

        self.reg_msg = ctk.CTkLabel(f, text="", text_color=ERR)
        self.reg_msg.pack()

        ctk.CTkButton(
            f, text="Register",
            fg_color=ACCENT2,
            command=self.handle_register
        ).pack(padx=28, fill="x", pady=10)

        return f

    # ---------------- ENTRY HELPER ----------------
    def _entry(self, parent, placeholder, show=None):
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=42,
            fg_color=INPUT_BG,
            border_color=BORDER,
            text_color=TEXT,
            show=show
        )

    # ---------------- TAB SWITCH ----------------
    def _show_login(self):
        self.reg_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

        self.login_tab.configure(fg_color=ACCENT)
        self.reg_tab.configure(fg_color=INPUT_BG)

    def _show_register(self):
        self.login_frame.pack_forget()
        self.reg_frame.pack(fill="both", expand=True)

        self.login_tab.configure(fg_color=INPUT_BG)
        self.reg_tab.configure(fg_color=ACCENT)

    # ---------------- LOGIN LOGIC ----------------
    def handle_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get()

        success, message = self.auth_controller.login(username, password)

        if success:
            self.destroy()
            self.on_login_success()
        else:
            self.login_msg.configure(text=message)

    # ---------------- REGISTER LOGIC ----------------
    def handle_register(self):
        username = self.reg_user.get().strip()
        password = self.reg_pass.get()

        if len(username) < 3:
            self.reg_msg.configure(text="Username must be at least 3 characters")
            return

        if len(password) < 6:
            self.reg_msg.configure(text="Password must be at least 6 characters")
            return

        success, message = self.auth_controller.register(username, password)

        if success:
            self.reg_msg.configure(
                text="Registered Successfully! Redirecting to login...",
                text_color=ACCENT2
            )

            # Clear fields
            self.reg_user.delete(0, "end")
            self.reg_pass.delete(0, "end")

            # Redirect after 1 second
            self.after(1000, self._redirect_to_login)

        else:
            self.reg_msg.configure(text=message, text_color=ERR)

    def _redirect_to_login(self):
        self.reg_msg.configure(text="", text_color=ERR)
        self._show_login()

    # ---------------- FOOTER ----------------
    def _build_footer(self):
        ctk.CTkLabel(self,
                     text="Smart Control  •  v1.0",
                     font=("Segoe UI", 9),
                     text_color=SUBTEXT).pack(pady=(0, 8))