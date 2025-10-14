"""
KaiHelper Service Console
-------------------------
Directly calls the Service Layer (not the API) to test the core logic.
"""

from kaihelper.business.service.service_installer import ServiceInstaller
from kaihelper.domain.domain_installer import DomainInstaller
from kaihelper.contracts.user_dto import RegisterUserDTO, LoginRequestDTO


def print_menu():
    print("\n=== KaiHelper Service Console ===")
    print("1. Register User")
    print("2. Login User")
    print("3. Get User Profile")
    print("4. Exit")


def main():
    # Initialize Dependency Injection manually
    domain = DomainInstaller()
    services = ServiceInstaller(domain)
    user_service = services.get_user_service()

    print("[KaiHelper Console] Dependency Injection initialized.")
    print("Ready to call service layer directly.\n")

    while True:
        print_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            username = input("Username: ")
            email = input("Email: ")
            password = input("Password: ")
    
            dto = RegisterUserDTO(username=username, email=email, full_name=username, password=password, confirm_password = password)
            result = user_service.register_user(dto)
            print(f"\nResult: {result.message}")
            if hasattr(result, "data") or hasattr(result, "user"):
                data = getattr(result, "data", None) or getattr(result, "user", None)
                print(f"User: {data}\n")

        elif choice == "2":
            email = input("Email: ")
            password = input("Password: ")

            dto = LoginRequestDTO(email=email, password=password)
            result = user_service.login_user(dto)
            print(f"\nResult: {result.message}")
            if hasattr(result, "data") or hasattr(result, "user"):
                data = getattr(result, "data", None) or getattr(result, "user", None)
                print(f"User: {data}\n")

        elif choice == "3":
            user_id = int(input("User ID: "))
            result = user_service.get_user_profile(user_id)
            print(f"\nResult: {result.message}")
            if hasattr(result, "data") or hasattr(result, "user"):
                data = getattr(result, "data", None) or getattr(result, "user", None)
                print(f"User: {data}\n")

        elif choice == "4":
            print("👋 Exiting KaiHelper Service Console.")
            break

        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
