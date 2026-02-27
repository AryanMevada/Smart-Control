from models.user_model import UserModel


class AuthController:

    def __init__(self):
        self.user_model = UserModel()

    def register(self, username, password):
        if not username or not password:
            return False, "Fields cannot be empty"

        success = self.user_model.register_user(username, password)
        if success:
            return True, "Registration successful"
        else:
            return False, "Username already exists"

    def login(self, username, password):
        if not username or not password:
            return False, "Fields cannot be empty"

        success = self.user_model.authenticate_user(username, password)
        if success:
            return True, "Login successful"
        else:
            return False, "Invalid username or password"
        