"""
Login Form UI
-------------
Simple Tkinter interface to test the User login functionality.
"""

import tkinter as tk
from tkinter import messagebox
from kaihelper.business.service.user_service import UserService
from kaihelper.contracts.user_dto import LoginRequestDTO


class LoginForm:
    """Tkinter-based login form for KaiHelper."""

    def __init__(self, root):
        self.root = root
        self.root.title("KaiHelper - Login")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        # Service layer
        self.user_service = UserService()

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Username or Email", font=("Arial", 12)).pack(pady=(20, 5))
        self.entry_username = tk.Entry(self.root, width=30)
        self.entry_username.pack()

        tk.Label(self.root, text="Password", font=("Arial", 12)).pack(pady=(10, 5))
        self.entry_password = tk.Entry(self.root, width=30, show="*")
        self.entry_password.pack()

        tk.Button(
            self.root,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            width=15,
            command=self.login_user
        ).pack(pady=20)

    def login_user(self):
        username_or_email = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username_or_email or not password:
            messagebox.showwarning("Validation Error", "Please enter both username/email and password.")
            return

        login_dto = LoginRequestDTO(username_or_email=username_or_email, password=password)
        result = self.user_service.login_user(login_dto)

        if result.success:
            messagebox.showinfo("Login Successful", f"Welcome, {result.data.full_name or result.data.username}!")
        else:
            messagebox.showerror("Login Failed", result.message)


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginForm(root)
    root.mainloop()
