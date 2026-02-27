import customtkinter as ctk
import subprocess
import sys
import os


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SmartControlLauncher:

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Smart Control - Launcher")
        self.root.geometry("600x450")

        self.current_process = None

        self.build_ui()
        self.root.mainloop()

    def build_ui(self):

        title = ctk.CTkLabel(
            self.root,
            text="SMART CONTROL",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=30)

        self.create_button("🖱 Mouse Control", "Mouse")
        self.create_button("🎵 Media Controller", "Media Controller")
        self.create_button("🔊 Volume Control", "Volume")
        self.create_button("⌨ Keyboard Control", "keyboard")

        stop_btn = ctk.CTkButton(
            self.root,
            text="Stop Current Module",
            fg_color="red",
            hover_color="#aa0000",
            command=self.stop_module
        )
        stop_btn.pack(pady=25)

    def create_button(self, text, folder_name):

        btn = ctk.CTkButton(
            self.root,
            text=text,
            width=300,
            height=50,
            command=lambda: self.run_module(folder_name)
        )
        btn.pack(pady=10)

    def run_module(self, folder_name):

        self.stop_module()

        module_path = os.path.join(folder_name, "main.py")

        if os.path.exists(module_path):
            self.current_process = subprocess.Popen(
                [sys.executable, module_path]
            )
        else:
            print(f"{module_path} not found")

    def stop_module(self):

        if self.current_process:
            self.current_process.terminate()
            self.current_process = None


if __name__ == "__main__":
    SmartControlLauncher()
