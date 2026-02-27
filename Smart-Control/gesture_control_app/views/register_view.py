import customtkinter as ctk

TEXT = "#e6edf3"
ERR = "#f85149"
SUCCESS = "#3fb950"


class RegisterView(ctk.CTkFrame):

    def __init__(self, parent, auth_controller):
        super().__init__(parent, fg_color="transparent")

        self.auth_controller = auth_controller

        ctk.CTkLabel(self,
                     text="Create Account ✨",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT).pack(pady=20)

        self.username = ctk.CTkEntry(
            self, placeholder_text="Username",
            height=40)
        self.username.pack(padx=30, pady=10, fill="x")

        self.password = ctk.CTkEntry(
            self, placeholder_text="Password",
            show="*", height=40)
        self.password.pack(padx=30, pady=10, fill="x")

        self.message = ctk.CTkLabel(self,
                                    text="",
                                    text_color=ERR)
        self.message.pack()

        ctk.CTkButton(self,
                      text="Register",
                      fg_color=SUCCESS,
                      command=self.handle_register).pack(
            padx=30, pady=20, fill="x")

    def handle_register(self):
        username = self.username.get()
        password = self.password.get()

        success, message = self.auth_controller.register(username, password)

        if success:
            self.message.configure(text="Registered Successfully!",
                                   text_color=SUCCESS)
        else:
            self.message.configure(text=message,
                                   text_color=ERR)