import customtkinter as ctk
from controllers.auth_controller import AuthController

if __name__ == "__main__":
    # Tampilannya mode terang
    ctk.set_appearance_mode("light")
    app = AuthController()
    app.run()
