"""
KaiHelper Application Entry Point
---------------------------------
Initializes repositories, services, and launches the main application UI.
"""

from kaihelper.business.service.service_installer import ServiceInstaller
from kaihelper.domain.domain_installer import DomainInstaller
from kaihelper.ui.login_form import LoginForm
import tkinter as tk


class KaiHelperApp:
    """Main application class responsible for startup and dependency setup."""

    def __init__(self):
        # Initialize installers
        self.domain_installer = DomainInstaller()
        self.service_installer = ServiceInstaller()

        # You can share them globally if needed
        self._register_globals()

        # Start UI
        self._launch_ui()

    def _register_globals(self):
        """Optional: Register installers as globals for easy access across modules."""
        global SERVICES, DOMAIN
        SERVICES = self.service_installer
        DOMAIN = self.domain_installer

    def _launch_ui(self):
        """Starts the main Tkinter UI."""
        root = tk.Tk()
        app = LoginForm(root)  # Start with login form
        root.mainloop()


if __name__ == "__main__":
    app = KaiHelperApp()
