# main.py
from banking_system import BankingSystem
from data_handler import load_accounts

def main_menu():
    print("\nWelcome to Global Digital Bank")
    print("1) Create Account")
    print("2) Deposit")
    print("3) Withdraw")
    print("4) Balance Inquiry")
    print("5) Close Account")
    print("6) Search Account by Name")
    print("7) Transfer Funds")
    print("8) Transaction History")
    print("9) Exit")

def main():
    bank = BankingSystem()
    bank.accounts = load_accounts()
    if bank.accounts:
        # Find the max account number to continue auto-generation
        bank.next_account_number = max(bank.accounts.keys()) + 1
    
    while True:
        main_menu()
        try:
            choice = int(input("Enter your choice: "))
            
            if choice == 1:
                name = input("Enter name: ")
                age = int(input("Enter age: "))
                acc_type = input("Enter account type (Savings/Current): ")
                bank.create_account(name, age, acc_type)
            elif choice == 2:
                acc_num = int(input("Enter account number: "))
                amount = float(input("Enter amount to deposit: "))
                bank.deposit(acc_num, amount)
            elif choice == 3:
                acc_num = int(input("Enter account number: "))
                amount = float(input("Enter amount to withdraw: "))
                bank.withdraw(acc_num, amount)
            elif choice == 4:
                acc_num = int(input("Enter account number: "))
                bank.balance_inquiry(acc_num)
            elif choice == 5:
                acc_num = int(input("Enter account number to close: "))
                bank.close_account(acc_num)
            elif choice == 6:
                name = input("Enter name to search: ")
                bank.search_by_name(name)
            elif choice == 7:
                from_acc = int(input("Enter sender's account number: "))
                to_acc = int(input("Enter receiver's account number: "))
                amount = float(input("Enter amount to transfer: "))
                bank.transfer_funds(from_acc, to_acc, amount)
            elif choice == 8:
                acc_num = int(input("Enter account number: "))
                bank.transaction_history_viewer(acc_num)
            elif choice == 9:
                bank.system_exit_with_autosave()
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()