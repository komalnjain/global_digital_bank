# main.py
from banking_system import BankingSystem
from data_handler import load_accounts
from account import AccountLockedError
import json

def secure_input(prompt, hide_input=False):
    """Get secure input, optionally hiding it (for PINs)."""
    if hide_input:
        import getpass
        return getpass.getpass(prompt)
    return input(prompt)

def authenticate_account(bank, account_number):
    """Helper function to authenticate an account with PIN."""
    if not account_number:
        return None
        
    account = bank.accounts.get(account_number)
    if not account:
        print("Error: Account not found.")
        return None
        
    if not account.pin_hash:
        return account  # No PIN set, no need for authentication
        
    max_attempts = 3
    for attempt in range(max_attempts):
        pin = secure_input(f"Enter PIN for account {account_number}: ", hide_input=True)
        try:
            if account.verify_pin(pin):
                return account
            else:
                remaining = max_attempts - (attempt + 1)
                if remaining > 0:
                    print(f"Incorrect PIN. {remaining} attempts remaining.")
        except AccountLockedError as e:
            print(f"Error: {e}")
            return None
            
    print("Too many failed attempts. Please try again later.")
    return None

def main_menu():
    print("\n=== Banking System Menu ===")
    print("1) Create Account")
    print("2) Deposit")
    print("3) Withdraw")
    print("4) Balance Inquiry")
    print("5) Close Account")
    print("6) Search Account by Name")
    print("7) List All Active Accounts")
    print("8) List All Closed Accounts")
    print("9) Count Active Accounts")
    print("10) Reopen Closed Account")
    print("11) Rename Account Holder")
    print("12) Set/Change PIN")
    print("13) Delete All Accounts")
    print("14) Top N Accounts by Balance")
    print("15) Calculate Average Balance")
    print("16) Show Youngest Account Holder")
    print("17) Show Oldest Account Holder")
    print("18) Calculate Simple Interest")
    print("19) Calculate Compound Interest")
    print("20) Transfer Funds")
    print("21) Transaction History")
    print("22) Generate Account Statement")
    print("23) Export Account Data")
    print("24) Upgrade Account Type")
    print("25) Import Accounts from File")
    print("26) Exit")

def set_account_pin(bank, account_number):
    """Set or change PIN for an account."""
    if not account_number:
        return
        
    account = bank.accounts.get(account_number)
    if not account:
        print("Error: Account not found.")
        return
        
    # If account has a PIN, require authentication first
    if account.pin_hash:
        print("Authentication required to change PIN.")
        if not authenticate_account(bank, account_number):
            return
    
    while True:
        pin = secure_input("Enter new 4-digit PIN: ", hide_input=True)
        confirm_pin = secure_input("Confirm new 4-digit PIN: ", hide_input=True)
        
        if pin != confirm_pin:
            print("PINs do not match. Please try again.")
            continue
            
        try:
            account.set_pin(pin)
            print("PIN set successfully!")
            break
        except ValueError as e:
            print(f"Error: {e}")
            
def export_account_data(bank, account_number=None):
    """Export account data to a file.

    Args:
        bank: The BankingSystem instance
        account_number: Optional account number to export. If None, exports all accounts.
    """
    if account_number:
        # Export a single account
        account = bank.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return

        filename = f"account_{account_number}_export.json"
        account_data = {
            'account_number': account.account_number,
            'name': account.name,
            'age': account.age,
            'balance': account.balance,
            'account_type': account.account_type,
            'status': account.status,
            'transactions': account.transactions
        }

        try:
            with open(filename, 'w') as f:
                json.dump(account_data, f, indent=4, default=str)
            print(f"Account data exported to {filename}")
        except Exception as e:
            print(f"Error exporting account data: {e}")
        return

    # Export all accounts
    if not bank.accounts:
        print("No accounts to export.")
        return

    accounts_to_export = bank.accounts.values()
    filename = "all_accounts_export.json"

    export_data = {
        'accounts': []
    }

    for account in accounts_to_export:
        account_data = {
            'account_number': account.account_number,
            'name': account.name,
            'age': account.age,
            'balance': account.balance,
            'account_type': account.account_type,
            'status': account.status,
            'transactions': account.transactions
        }

        # Add PIN if it exists
        if hasattr(account, 'pin'):
            account_data['pin'] = account.pin

        export_data['accounts'].append(account_data)

    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=4, default=str)
        print(f"Account data exported to {filename}")
    except Exception as e:
        print(f"Error exporting account data: {e}")
        return
        
    print(f"Account data exported to {filename}")
    return filename

def main():
    bank = BankingSystem()
    bank.accounts = bank.load_accounts()  # Use the instance method instead of standalone function
    if bank.accounts:
        # Find the max account number to continue auto-generation
        bank.next_account_number = max(bank.accounts.keys()) + 1
    
    while True:
        main_menu()
        try:
            choice = int(input("Enter your choice: "))
            
            if choice == 1:
                name = input("Enter account holder name: ")
                age = int(input("Enter age: "))
                account_type = input("Enter account type (Savings/Current): ")
                initial_deposit = float(input("Enter initial deposit: "))
                set_pin = input("Would you like to set a 4-digit PIN for this account? (y/n): ").lower()
                pin = None
                if set_pin == 'y':
                    while True:
                        pin = secure_input("Enter 4-digit PIN: ", hide_input=True)
                        if len(pin) == 4 and pin.isdigit():
                            confirm_pin = secure_input("Confirm 4-digit PIN: ", hide_input=True)
                            if pin == confirm_pin:
                                break
                            print("PINs do not match. Please try again.")
                        else:
                            print("PIN must be exactly 4 digits.")
                
                account = bank.create_account(name, age, account_type, initial_deposit, pin)
                if account:
                    print(f"Account created successfully! Account number: {account.account_number}")
                    if pin:
                        print("Remember your PIN as it will be required for account access.")
            elif choice == 2:
                acc_num = int(input("Enter account number: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    amount = float(input("Enter amount to deposit: "))
                    bank.deposit(acc_num, amount)
            elif choice == 3:
                acc_num = int(input("Enter account number: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    amount = float(input("Enter amount to withdraw: "))
                    bank.withdraw(acc_num, amount)
            elif choice == 4:
                acc_num = int(input("Enter account number: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    bank.balance_inquiry(acc_num)
            elif choice == 5:
                acc_num = int(input("Enter account number to close: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    bank.close_account(acc_num)
            elif choice == 6:
                name = input("Enter name to search: ")
                bank.search_by_name(name)
            elif choice == 7:
                bank.list_active_accounts()
            elif choice == 8:
                bank.list_closed_accounts()
            elif choice == 9:
                bank.count_active_accounts()
            elif choice == 10:
                acc_num = int(input("Enter account number to reopen: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    bank.reopen_account(acc_num)
            elif choice == 11:
                acc_num = int(input("Enter account number: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    new_name = input("Enter new account holder name: ")
                    bank.rename_account_holder(acc_num, new_name)
            elif choice == 12:
                acc_num = int(input("Enter account number: "))
                account = bank.accounts.get(acc_num)
                if account:
                    set_account_pin(bank, acc_num)
                else:
                    print("Error: Account not found.")
            elif choice == 13:
                confirm = input("WARNING: This will delete ALL accounts. Are you sure? (yes/no): ")
                if confirm.lower() == 'yes':
                    # Require authentication for admin account if exists
                    admin_account = next((acc for acc in bank.accounts.values() if acc.name.lower() == 'admin'), None)
                    if admin_account:
                        print("Admin authentication required for this operation.")
                        if not authenticate_account(bank, admin_account.account_number):
                            print("Authentication failed. Operation cancelled.")
                            continue
                    bank.delete_all_accounts(confirmation=True)
            elif choice == 14:
                try:
                    n = int(input("Enter number of top accounts to display (default 5): ") or "5")
                    bank.get_top_accounts_by_balance(int(n))
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            elif choice == 15:
                bank.calculate_average_balance()
            elif choice == 16:
                bank.find_youngest_account_holder()
            elif choice == 17:
                bank.find_oldest_account_holder()
            elif choice == 18:  # Calculate Simple Interest
                acc_num = int(input("Enter account number: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    try:
                        rate = float(input("Enter annual interest rate (%): "))
                        years = int(input("Enter number of years: "))
                        bank.calculate_simple_interest(acc_num, rate, years)
                    except ValueError:
                        print("Error: Please enter valid numbers for rate and years.")
                        
            elif choice == 19:  # Calculate Compound Interest
                acc_num = int(input("Enter account number: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    try:
                        rate = float(input("Enter annual interest rate (%): "))
                        years = int(input("Enter number of years: "))
                        print("\nCompounding Frequency Options:")
                        print("1) Annually (1x per year)")
                        print("2) Semi-annually (2x per year)")
                        print("3) Quarterly (4x per year)")
                        print("4) Monthly (12x per year)")
                        print("5) Daily (365x per year)")
                        print("6) Custom (specify number of times per year)")
                        
                        freq_choice = input("Select compounding frequency (1-6): ")
                        
                        if freq_choice == '1':
                            bank.calculate_compound_interest(acc_num, rate, years, 1)
                        elif freq_choice == '2':
                            bank.calculate_compound_interest(acc_num, rate, years, 2)
                        elif freq_choice == '3':
                            bank.calculate_compound_interest(acc_num, rate, years, 4)
                        elif freq_choice == '4':
                            bank.calculate_compound_interest(acc_num, rate, years, 12)
                        elif freq_choice == '5':
                            bank.calculate_compound_interest(acc_num, rate, years, 365)
                        elif freq_choice == '6':
                            try:
                                custom_freq = int(input("Enter number of times to compound per year: "))
                                if custom_freq <= 0:
                                    print("Error: Compounding frequency must be positive.")
                                else:
                                    bank.calculate_compound_interest(acc_num, rate, years, custom_freq)
                            except ValueError:
                                print("Error: Please enter a valid number for compounding frequency.")
                        else:
                            print("Invalid choice. Please select a number between 1 and 6.")
                            
                    except ValueError:
                        print("Error: Please enter valid numbers for rate and years.")
            elif choice == 20:  # Transfer Funds
                from_acc = int(input("Enter sender's account number: "))
                account = authenticate_account(bank, from_acc)
                if account:
                    to_acc = int(input("Enter receiver's account number: "))
                    if to_acc not in bank.accounts:
                        print("Error: Receiver account not found.")
                        continue
                    amount = float(input("Enter amount to transfer: "))
                    bank.transfer_funds(from_acc, to_acc, amount)
                    
            elif choice == 21:  # Transaction History
                acc_num = int(input("Enter account number: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    bank.transaction_history_viewer(acc_num)
                    
            elif choice == 22:  # Generate Account Statement
                acc_num = int(input("Enter account number: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    print("\nSelect output format:")
                    print("1) Text")
                    print("2) PDF")
                    format_choice = input("Enter your choice (1-2): ")
                    
                    if format_choice not in ['1', '2']:
                        print("Invalid choice. Please try again.")
                        continue
                        
                    output_format = 'text' if format_choice == '1' else 'pdf'
                    ext = 'txt' if format_choice == '1' else 'pdf'
                    
                    filename = input(f"Enter output filename (without extension) or press Enter for default: ")
                    if not filename:
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"account_{acc_num}_statement_{timestamp}"
                    
                    # Add extension if not present
                    if not filename.lower().endswith(f'.{ext}'):
                        filename = f"{filename}.{ext}"
                    
                    bank.generate_account_statement(acc_num, output_format, filename)
                    
            elif choice == 23:  # Export Account Data
                print("\nExport Options:")
                print("1) Export a single account")
                print("2) Export all accounts")
                export_choice = input("Enter your choice (1-2): ")
                
                if export_choice == '1':
                    acc_num = int(input("Enter account number to export: "))
                    export_account_data(bank, acc_num)
                elif export_choice == '2':
                    confirm = input("This will export all accounts. Continue? (y/n): ")
                    if confirm.lower() == 'y':
                        export_account_data(bank)  # Export all accounts
                else:
                    print("Invalid choice. Please try again.")
                
            elif choice == 24:  # Upgrade Account Type
                acc_num = int(input("Enter account number: "))
                account = authenticate_account(bank, acc_num)
                if account:
                    new_type = input("Enter new account type (Savings/Current): ")
                    bank.upgrade_account_type(acc_num, new_type)
                    
            elif choice == 25:  # Import Accounts from File
                filename = input("Enter the filename to import accounts from: ")
                bank.import_accounts_from_file(filename)
                
            elif choice == 26:
                print("Saving data and exiting...")
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