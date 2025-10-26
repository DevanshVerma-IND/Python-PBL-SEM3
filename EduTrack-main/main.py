import os
import sys
import login

APP_TITLE = "EduTrack"

def clear_screen():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

def prompt(msg: str) -> str:
    try:
        return input(msg)
    except (EOFError, KeyboardInterrupt):
        print("\nExiting…")
        sys.exit(0)

def main():
    users = login.load_users()

    while True:
        print(f"\n===== {APP_TITLE} Main Menu =====")
        print("1. Create account")
        print("2. Login")
        print("3. Forgot password")
        print("4. Repair user data (one-time migration)")
        print("5. Clear screen")
        print("6. Exit")

        choice = prompt("Enter your choice (1-6): ").strip().lower()

        if choice in ("6", "q", "quit", "exit"):
            print(f"Thank you for using {APP_TITLE}! Goodbye.")
            break

        if choice == "1":
            login.create_account(users)

        elif choice == "2":
            login.login(users)

        elif choice == "3":
            login.forgot_password(users)

        elif choice == "4":
            login.migrate_userdata_interactive()
            users = login.load_users()

        elif choice == "5":
            clear_screen()

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()