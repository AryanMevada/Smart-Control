from controllers.auth_controller import AuthController
from controllers.app_controller import AppController
from views.auth_view import AuthView


# ================= START MAIN APP =================
def start_main_app():
    controller = AppController()
    controller.run()


# ================= ENTRY POINT =================
if __name__ == "__main__":

    auth_controller = AuthController()

    app = AuthView(auth_controller, start_main_app)
    app.mainloop()