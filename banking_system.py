#import csv
import logging
import json
from datetime import datetime
from account import Account, AccountLockedError
from data_handler import save_accounts, transaction_logger

class BankingSystem:
    def __init__(self):
        self.accounts = {}
        self.next_account_number = 1001
        self.data_file = 'accounts_data.json'

    def create_account(self, name, age, account_type, initial_deposit=None, pin=None):
        """Create a new account with the given details and optional PIN."""
        if age < 18:
            print("Account creation failed: Age must be 18 or above.")
            return None
            
        if account_type.lower() not in ["savings", "current"]:
            print("Account creation failed: Invalid account type. Must be 'Savings' or 'Current'.")
            return None
            
        if initial_deposit is None:
            initial_deposit = 500 if account_type.lower() == "savings" else 1000
            
        min_deposit = 500 if account_type.lower() == "savings" else 1000
        if initial_deposit < min_deposit:
            print(f"Account creation failed: Minimum initial deposit for {account_type} account is {min_deposit}.")
            return None
            
        account = Account(self.next_account_number, name, age, initial_deposit, account_type.capitalize())
        
        # Set PIN if provided
        if pin:
            try:
                account.set_pin(pin)
            except ValueError as e:
                print(f"Account creation failed: {e}")
                return None
        
        self.accounts[self.next_account_number] = account
        self.next_account_number += 1
        
        # Log the account creation
        transaction_logger.info('', extra={
            'account_number': account.account_number,
            'operation': 'Create',
            'amount': initial_deposit,
            'balance_after': account.balance,
            'details': f"Account created for {name}"
        })
        
        # Save accounts to CSV
        if not self.save_accounts():
            print("Warning: Failed to save account data to file.")
        
        return account
        
    def authenticate_account(self, account_number, pin):
        """Authenticate an account with the given PIN."""
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return None
            
        try:
            if account.verify_pin(pin):
                return account
            else:
                print("Error: Invalid PIN.")
                return None
        except AccountLockedError as e:
            print(f"Error: {e}")
            return None

    def deposit(self, account_number, amount, category='DEPOSIT', description=""):
        """Deposits funds into an account.
        
        Args:
            account_number: The account number to deposit to
            amount: Amount to deposit (must be positive)
            category: Transaction category (default: 'DEPOSIT')
            description: Optional description of the deposit
            
        Returns:
            bool: True if deposit was successful, False otherwise
        """
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return False
            
        if amount <= 0:
            print("Error: Deposit amount must be positive.")
            return False
            
        # Check for suspiciously large deposits
        if amount > 100000:  # Example threshold
            print("Note: Large deposit detected. This transaction will be reported.")
            category = 'LARGE_DEPOSIT'  # Special category for monitoring
            
        # Add the transaction with category
        transaction = account.add_transaction('DEPOSIT', amount, category, description)
        account.balance += amount
        
        # Log the transaction
        transaction_logger.info(description or 'Deposit', extra={
            'account_number': account_number,
            'operation': 'DEPOSIT',
            'amount': amount,
            'balance_after': account.balance,
            'category': category,
            'details': description or 'Deposit to account'
        })
        
        # Save the updated accounts to CSV
        if not self.save_accounts():
            print("Warning: Failed to save account data after deposit.")
            
        return True

    def withdraw(self, account_number, amount):
        """Deducts funds from an account if sufficient balance exists and daily limits are not exceeded."""
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return
        
        # Use the Account class's validation
        can_withdraw, message = account.can_withdraw(amount)
        if not can_withdraw:
            print(f"Error: {message}")
            return
            
        # Process the withdrawal
        account.add_withdrawal(amount)
        print(f"Withdrawal successful. New balance: {account.balance}")
        
        # Log the transaction
        transaction_logger.info('', extra={
            'account_number': account.account_number,
            'operation': 'Withdraw',
            'amount': -amount,
            'balance_after': account.balance
        })
        
        # Save the updated accounts to CSV
        if not self.save_accounts():
            print("Warning: Failed to save account data after withdrawal.")
            
        return True

    def balance_inquiry(self, account_number):
        """Displays account balance and details."""
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return
        
        print("\n--- Account Details ---")
        print(f"Account Number: {account.account_number}")
        print(f"Name: {account.name}")
        print(f"Account Type: {account.account_type}")
        print(f"Status: {account.status}")
        print(f"Balance: {account.balance}\n")

    def close_account(self, account_number):
        """Marks an account as inactive."""
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return
        
        account.status = 'Inactive'
        # Save the updated accounts to CSV
        if not self.save_accounts():
            print("Warning: Failed to save account data after closing account.")
            
        print(f"Account {account_number} has been closed.")
        
        # Log the transaction
        transaction_logger.info('', extra={
            'account_number': account.account_number,
            'operation': 'Close',
            'amount': 0,
            'balance_after': account.balance
        })
        
        return True

    def export_account_data(self, account_number, filename=None):
        """Export account data to a JSON file.
        
        Args:
            account_number: The account number to export
            filename: Optional custom filename (default: account_<number>_export.json)
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return False
            
        if not filename:
            filename = f"account_{account_number}_export.json"
            
        try:
            # Prepare account data for export
            account_data = {
                'account_number': account.account_number,
                'name': account.name,
                'age': account.age,
                'balance': account.balance,
                'account_type': account.account_type,
                'status': account.status,
                'transactions': [{
                    'date': t[0].isoformat(),
                    'type': t[1],
                    'amount': t[2],
                    'balance_after': t[3]
                } for t in account.transactions]
            }
            
            with open(filename, 'w') as f:
                json.dump(account_data, f, indent=2)
                
            print(f"Account data exported to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting account data: {e}")
            return False
            
    def import_account_data(self, filename):
        """Import account data from a JSON file.
        
        Args:
            filename: The JSON file to import from
            
        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            # Validate required fields
            required_fields = ['account_number', 'name', 'account_type', 'balance']
            if not all(field in data for field in required_fields):
                print("Error: Invalid data format in import file.")
                return False
                
            account_number = data['account_number']
            
            # Check if account already exists
            if account_number in self.accounts:
                print(f"Account {account_number} already exists. Updating...")
                account = self.accounts[account_number]
                account.name = data['name']
                account.balance = data['balance']
                account.account_type = data['account_type']
                account.status = data.get('status', 'Active')
                
                # Only update transactions if they exist in import
                if 'transactions' in data and isinstance(data['transactions'], list):
                    account.transactions = [(
                        datetime.fromisoformat(t['date']),
                        t['type'],
                        t['amount'],
                        t['balance_after']
                    ) for t in data['transactions']]
            else:
                # Create new account
                account = Account(
                    account_number=account_number,
                    name=data['name'],
                    age=data.get('age', 18),  # Default age if not provided
                    balance=data['balance'],
                    account_type=data['account_type']
                )
                account.status = data.get('status', 'Active')
                self.accounts[account_number] = account
                
                # Update next account number if needed
                if account_number >= self.next_account_number:
                    self.next_account_number = account_number + 1
                    
            print(f"Successfully imported data for account {account_number}")
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in import file.")
        except Exception as e:
            print(f"Error during import: {e}")
            
        return False
            
    def load_accounts(self):
        """Load accounts from the CSV file."""
        import csv
        try:
            self.accounts = {}
            with open('accounts.csv', 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Convert data types
                        account_number = int(row['account_number'])
                        age = int(row['age'])
                        balance = float(row['balance'])
                        
                        # Create account
                        account = Account(
                            account_number=account_number,
                            name=row['name'],
                            age=age,
                            balance=balance,
                            account_type=row['account_type']
                        )
                        
                        # Set additional attributes
                        account.status = row.get('status', 'Active')
                        if 'pin' in row and row['pin']:  # Only set PIN if it exists and is not empty
                            account.pin = row['pin']
                        
                        self.accounts[account_number] = account
                        
                        # Update next account number if needed
                        if account_number >= self.next_account_number:
                            self.next_account_number = account_number + 1
                            
                    except (ValueError, KeyError) as e:
                        print(f"Error loading account data: {e}")
                        continue
            
            if self.accounts:
                print(f"Loaded {len(self.accounts)} accounts from accounts.csv")
            return self.accounts
            
        except FileNotFoundError:
            print("No accounts.csv file found. Starting with empty account list.")
            return {}
        except Exception as e:
            print(f"Error loading accounts from CSV: {e}")
            return {}

    def save_accounts(self):
        """Save accounts to the CSV file."""
        import csv
        try:
            with open('accounts.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['account_number', 'name', 'age', 'balance', 'account_type', 'status', 'pin'])
                
                # Write account data
                for account in self.accounts.values():
                    writer.writerow([
                        account.account_number,
                        account.name,
                        account.age,
                        f"{account.balance:.2f}",
                        account.account_type,
                        getattr(account, 'status', 'Active'),
                        getattr(account, 'pin', '')
                    ])
            return True
            
        except Exception as e:
            print(f"Error saving accounts to CSV: {e}")
            return False

    def system_exit_with_autosave(self):
        """Save all data and exit the system."""
        self.save_accounts()
        print("Data saved. Goodbye!")
        exit()

    def search_by_name(self, name):
        """Finds accounts by customer name."""
        found_accounts = [acc for acc in self.accounts.values() if acc.name.lower() == name.lower()]
        if not found_accounts:
            print("No accounts found with that name.")
            return
        
        print(f"Found {len(found_accounts)} account(s) for '{name}':")
        for acc in found_accounts:
            self.balance_inquiry(acc.account_number)

    def transaction_history_viewer(self, account_number, limit=10, category=None):
        """Displays the transaction history for an account with optional category filter.
        
        Args:
            account_number: The account number to view history for
            limit: Maximum number of transactions to display
            category: Optional category to filter by
        """
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return
            
        # Get transaction summary
        summary = account.get_transaction_summary()
        
        print(f"\n=== Transaction History for Account {account_number} ===")
        print(f"Current Balance: {account.balance}")
        
        # Display category summary if no specific category is selected
        if not category and summary:
            print("\nTransaction Summary by Category:")
            print("-" * 60)
            print(f"{'Category':<20} {'Count':>10} {'Total':>15} {'Average':>15}")
            print("-" * 60)
            for cat, data in summary.items():
                if data['count'] > 0:
                    print(f"{cat:<20} {data['count']:>10} {data['total']:>15.2f} {data['average']:>15.2f}")
            print("\n")
        
        # Display transactions
        print(f"\n{'Recent Transactions':^60}")
        print("-" * 80)
        print(f"{'Date':<20} {'Type':<15} {'Category':<15} {'Amount':>12} {'Balance':>12} {'Description'}")
        print("-" * 80)
        
        # Get transactions with optional category filter
        transactions = account.get_transaction_history(limit=limit, category=category)
        
        if not transactions:
            msg = f"No transactions found{f' in category: {category}' if category else ''}."
            print(msg)
            return
            
        for t in reversed(transactions):
            date_str = t[0].strftime("%Y-%m-%d %H:%M:%S")
            txn_type = t[1]
            amount = t[2]
            balance = t[3]
            txn_category = t[4] if len(t) > 4 else 'UNKNOWN'
            txn_desc = t[5] if len(t) > 5 else ''
            
            # Color code amounts for better readability
            amount_str = f"{amount:>12.2f}"
            if amount > 0:
                amount_str = f"\033[92m{amount_str}\\033[0m"  # Green for credits
            else:
                amount_str = f"\033[91m{amount_str}\\033[0m"  # Red for debits
                
            print(f"{date_str:<20} {txn_type:<15} {txn_category:<15} {amount_str} {balance:>12.2f} {txn_desc}")
        
        # Display filter info if applicable
        if category:
            print(f"\nShowing transactions in category: {category}")
            print("To view all transactions, run without a category filter.")
        
        # Log the transaction
        transaction_logger.info('', extra={
            'account_number': account.account_number,
            'operation': 'Close',
            'amount': 0,
            'balance_after': 0,
            'details': f"Deleted all {len(self.accounts)} accounts"
        })
        
    def list_active_accounts(self):
        """Lists all active accounts."""
        active_accounts = [acc for acc in self.accounts.values() if acc.status == 'Active']
        if not active_accounts:
            print("No active accounts found.")
            return
            
        print("\n--- Active Accounts ---")
        for acc in active_accounts:
            print(f"Account: {acc.account_number}, Name: {acc.name}, Type: {acc.account_type}, Balance: {acc.balance}")
    
    def list_closed_accounts(self):
        """Lists all closed (inactive) accounts."""
        closed_accounts = [acc for acc in self.accounts.values() if acc.status == 'Inactive']
        if not closed_accounts:
            print("No closed accounts found.")
            return
            
        print("\n--- Closed Accounts ---")
        for acc in closed_accounts:
            print(f"Account: {acc.account_number}, Name: {acc.name}, Type: {acc.account_type}")
            
    def count_active_accounts(self):
        """Returns the count of active accounts."""
        count = sum(1 for acc in self.accounts.values() if acc.status == 'Active')
        print(f"\nNumber of active accounts: {count}")
        return count
        
    def reopen_account(self, account_number):
        """Reopens a previously closed account."""
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return False
            
        if account.status == 'Active':
            print("Account is already active.")
            return False
            
        account.status = 'Active'
        # Save the updated accounts to CSV
        if not self.save_accounts():
            print("Warning: Failed to save account data after reopening account.")
            
        print(f"Account {account_number} has been successfully reopened.")
        
        # Log the transaction
        transaction_logger.info('', extra={
            'account_number': account_number,
            'operation': 'Reopen',
            'amount': 0,
            'balance_after': account.balance
        })
        return True
        
    def rename_account_holder(self, account_number, new_name):
        """Changes the name of an account holder."""
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return False
            
        if not new_name.strip():
            print("Error: Name cannot be empty.")
            return False
            
        old_name = account.name
        account.name = new_name.strip()
        # Save the updated accounts to CSV
        if not self.save_accounts():
            print("Warning: Failed to save account data after renaming account holder.")
            
        print(f"Account holder name changed from '{old_name}' to '{account.name}'.")
        
        # Log the transaction
        transaction_logger.info('', extra={
            'account_number': account_number,
            'operation': 'Rename',
            'amount': 0,
            'balance_after': account.balance,
            'details': f"Name changed from '{old_name}' to '{account.name}'"
        })
        return True
        
    def find_youngest_account_holder(self):
        """Finds and displays the youngest account holder."""
        if not self.accounts:
            print("No accounts found.")
            return None
            
        youngest = max(self.accounts.values(), key=lambda acc: acc.age)
        print("\n--- Youngest Account Holder ---")
        print(f"Name: {youngest.name}")
        print(f"Age: {youngest.age}")
        print(f"Account Number: {youngest.account_number}")
        print(f"Account Type: {youngest.account_type}")
        print(f"Balance: {youngest.balance}")
        return youngest
        
    def find_oldest_account_holder(self):
        """Finds and displays the oldest account holder."""
        if not self.accounts:
            print("No accounts found.")
            return None
            
        oldest = min(self.accounts.values(), key=lambda acc: acc.age)
        print("\n--- Oldest Account Holder ---")
        print(f"Name: {oldest.name}")
        print(f"Age: {oldest.age}")
        print(f"Account Number: {oldest.account_number}")
        print(f"Account Type: {oldest.account_type}")
        print(f"Balance: {oldest.balance}")
        return oldest
        
    def calculate_compound_interest(self, account_number, rate, years, compounding_frequency=1):
        """Calculates compound interest for an account.
        
        Args:
            account_number: The account number to calculate interest for
            rate: Annual interest rate (as a percentage, e.g., 5 for 5%)
            years: Number of years to calculate interest for
            compounding_frequency: Number of times interest is compounded per year (default: 1 for annually)
            
        Returns:
            tuple: (interest_earned, total_amount) or None if calculation fails
        """
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return None
            
        if rate <= 0 or years <= 0 or compounding_frequency <= 0:
            print("Error: Rate, years, and compounding frequency must be positive values.")
            return None
            
        principal = account.balance
        if principal <= 0:
            print("Error: Account balance must be positive to calculate interest.")
            return None
            
        # Convert rate from percentage to decimal
        rate_decimal = rate / 100
        
        # Calculate compound interest: A = P(1 + r/n)^(nt)
        amount = principal * (1 + (rate_decimal / compounding_frequency)) ** (compounding_frequency * years)
        interest_earned = amount - principal
        
        # Get compounding period name for display
        period_name = {
            1: 'annually',
            2: 'semi-annually',
            4: 'quarterly',
            12: 'monthly',
            365: 'daily'
        }.get(compounding_frequency, f'{compounding_frequency} times per year')
        
        print("\n=== Compound Interest Calculation ===")
        print(f"Account Number: {account_number}")
        print(f"Principal Amount: {principal:.2f}")
        print(f"Annual Interest Rate: {rate:.2f}%")
        print(f"Compounding: {period_name} ({compounding_frequency}x per year)")
        print(f"Time Period: {years} years")
        print(f"Interest Earned: {interest_earned:.2f}")
        print(f"Total Amount: {amount:.2f}")
        
        # Log the interest calculation
        transaction_logger.info('', extra={
            'account_number': account_number,
            'operation': 'Interest_Calculation',
            'amount': interest_earned,
            'balance_after': account.balance,
            'details': f"Compound interest at {rate}% for {years} years, compounded {period_name}"
        })
        
        return interest_earned, amount
        
    def calculate_simple_interest(self, account_number, rate, years):
        """Calculates simple interest for an account.
        
        Args:
            account_number: The account number to calculate interest for
            rate: Annual interest rate (as a percentage, e.g., 5 for 5%)
            years: Number of years to calculate interest for
            
        Returns:
            tuple: (interest_earned, total_amount) or None if calculation fails
        """
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return None
            
        if rate <= 0 or years <= 0:
            print("Error: Rate and years must be positive values.")
            return None
            
        principal = account.balance
        if principal <= 0:
            print("Error: Account balance must be positive to calculate interest.")
            return None
            
        interest = (principal * rate * years) / 100
        total = principal + interest
        
        print("\n--- Simple Interest Calculation ---")
        print(f"Account Number: {account_number}")
        print(f"Principal Amount: {principal:.2f}")
        print(f"Annual Interest Rate: {rate:.2f}%")
        print(f"Time Period: {years} years")
        print(f"Interest Earned: {interest:.2f}")
        print(f"Total Amount: {total:.2f}")
        
        # Log the interest calculation
        transaction_logger.info('', extra={
            'account_number': account_number,
            'operation': 'Interest_Calculation',
            'amount': interest,
            'balance_after': account.balance,
            'details': f"Simple interest at {rate}% for {years} years"
        })
        
        return interest, total
        
    def get_top_accounts_by_balance(self, n=5):
        """Returns the top N accounts with the highest balances."""
        if not self.accounts:
            print("No accounts found.")
            return []
            
        # Sort accounts by balance in descending order
        sorted_accounts = sorted(self.accounts.values(), 
                               key=lambda acc: acc.balance, 
                               reverse=True)
        
        # Take top N accounts
        top_accounts = sorted_accounts[:min(n, len(sorted_accounts))]
        
        print(f"\n--- Top {len(top_accounts)} Accounts by Balance ---")
        for i, account in enumerate(top_accounts, 1):
            print(f"{i}. Account: {account.account_number}, "
                  f"Name: {account.name}, "
                  f"Type: {account.account_type}, "
                  f"Balance: {account.balance}")
        
        return top_accounts
        
    def delete_all_accounts(self, confirmation=False):
        """Deletes all accounts after confirmation."""
        if not self.accounts:
            print("No accounts to delete.")
            return False
            
        if not confirmation:
            confirm = input("WARNING: This will delete ALL accounts. Are you sure? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Operation cancelled.")
                return False
                
        count = len(self.accounts)
        self.accounts.clear()
        print(f"Successfully deleted all {count} accounts.")
        
        # Log the action
        transaction_logger.info('', extra={
            'account_number': 'SYSTEM',
            'operation': 'DeleteAll',
            'amount': 0,
            'balance_after': 0,
            'details': f"Deleted all {count} accounts"
        })
        return True

    def transfer_funds(self, from_account_num, to_account_num, amount, category='TRANSFER', description=""):
        """Transfers funds between two accounts.
        
        Args:
            from_account_num: Source account number
            to_account_num: Destination account number
            amount: Amount to transfer (must be positive)
            category: Transaction category (default: 'TRANSFER')
            description: Optional description of the transfer
            
        Returns:
            bool: True if transfer was successful, False otherwise
        """
        from_account = self.accounts.get(from_account_num)
        to_account = self.accounts.get(to_account_num)

        if not from_account or not to_account:
            print("Error: One or both accounts not found.")
            return False
        
        if from_account.status == 'Inactive' or to_account.status == 'Inactive':
            print("Error: Both accounts must be active to transfer funds.")
            return False
            
        # Use the Account class's validation for the withdrawal part of the transfer
        can_withdraw, message = from_account.can_withdraw(amount)
        if not can_withdraw:
            print(f"Error: {message}")
            return False
            
        # Process the transfer with categories
        from_category = f"{category}_OUT" if not category.endswith('_OUT') else category
        to_category = f"{category}_IN" if not category.endswith('_IN') else category
        
        # Record the transactions
        from_txn = from_account.add_transaction(
            'TRANSFER_OUT', 
            -amount, 
            from_category,
            f"Transfer to account {to_account_num}: {description}"
        )
        
        to_txn = to_account.add_transaction(
            'TRANSFER_IN',
            amount,
            to_category,
            f"Transfer from account {from_account_num}: {description}"
        )
        
        # Log the transactions
        transaction_logger.info(f'Transfer to {to_account_num}', extra={
            'account_number': from_account_num,
            'operation': 'TRANSFER_OUT',
            'amount': -amount,
            'balance_after': from_account.balance,
            'category': from_category,
            'description': description,
            'related_transaction': to_txn[0].isoformat()
        })
        
        transaction_logger.info(f'Transfer from {from_account_num}', extra={
            'account_number': to_account_num,
            'operation': 'TRANSFER_IN',
            'amount': amount,
            'balance_after': to_account.balance,
            'category': to_category,
            'description': description,
            'related_transaction': from_txn[0].isoformat()
        })
        
        # Save the updated accounts to CSV
        if not self.save_accounts():
            print("Warning: Failed to save account data after transfer.")
            
        print(f"Transfer of {amount} successful from {from_account_num} to {to_account_num}.")
        return True
        
    def generate_account_statement(self, account_number, output_format='text', filename=None):
        """Generates an account statement in the specified format.
        
        Args:
            account_number: The account number to generate statement for
            output_format: Output format ('text' or 'pdf')
            filename: Optional filename to save the statement (default: account_<number>_statement.<ext>)
            
        Returns:
            str: Path to the generated statement file or None if failed
        """
        import os
        from datetime import datetime
        
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return None
            
        # Set default filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = 'txt' if output_format == 'text' else 'pdf'
            filename = f"account_{account_number}_statement_{timestamp}.{ext}"
            
        try:
            if output_format.lower() == 'text':
                return self._generate_text_statement(account, filename)
            elif output_format.lower() == 'pdf':
                return self._generate_pdf_statement(account, filename)
            else:
                print("Error: Unsupported output format. Use 'text' or 'pdf'.")
                return None
                
        except Exception as e:
            print(f"Error generating statement: {e}")
            return None
            
    def _generate_text_statement(self, account, filename):
        """Generate a text format account statement."""
        from datetime import datetime
        
        # Get transaction summary
        summary = account.get_transaction_summary()
        
        # Prepare statement content
        lines = []
        lines.append("=" * 60)
        lines.append(f"{'BANK STATEMENT':^60}")
        lines.append("=" * 60)
        lines.append(f"Account Number: {account.account_number}")
        lines.append(f"Account Holder: {account.name}")
        lines.append(f"Account Type: {account.account_type}")
        lines.append(f"Statement Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Current Balance: {account.balance:.2f}")
        lines.append("-" * 60)
        
        # Add summary by category
        lines.append("\nTRANSACTION SUMMARY BY CATEGORY")
        lines.append("-" * 60)
        lines.append(f"{'Category':<20} {'Count':>10} {'Total':>15} {'Average':>15}")
        lines.append("-" * 60)
        
        for category, data in summary.items():
            if data['count'] > 0:
                lines.append(f"{category:<20} {data['count']:>10} {data['total']:>15.2f} {data['average']:>15.2f}")
        
        # Add recent transactions
        transactions = account.get_transaction_history(limit=50)  # Last 50 transactions
        lines.append("\n" + "=" * 60)
        lines.append(f"{'RECENT TRANSACTIONS':^60}")
        lines.append("=" * 60)
        lines.append(f"{'Date':<20} {'Type':<15} {'Category':<15} {'Amount':>15} {'Balance':>15}")
        lines.append("-" * 60)
        
        for t in reversed(transactions):
            date_str = t[0].strftime("%Y-%m-%d %H:%M")
            txn_type = t[1]
            amount = t[2]
            balance = t[3]
            category = t[4] if len(t) > 4 else 'UNKNOWN'
            
            lines.append(f"{date_str:<20} {txn_type:<15} {category:<15} {amount:>15.2f} {balance:>15.2f}")
        
        # Add footer
        lines.append("\n" + "=" * 60)
        lines.append(f"{'END OF STATEMENT':^60}")
        lines.append("=" * 60)
        
        # Write to file
        with open(filename, 'w') as f:
            f.write("\n".join(lines))
            
        print(f"Statement generated: {os.path.abspath(filename)}")
        return os.path.abspath(filename)
        
    def _generate_pdf_statement(self, account, filename):
        """Generate a PDF format account statement."""
        from fpdf import FPDF
        from datetime import datetime
        import os
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Set font for the entire document
        pdf.set_font('Arial', '', 10)
        
        # Add header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'BANK STATEMENT', 0, 1, 'C')
        
        # Add account information
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f'Account Number: {account.account_number}', 0, 1)
        pdf.cell(0, 10, f'Account Holder: {account.name}', 0, 1)
        pdf.cell(0, 10, f'Account Type: {account.account_type}', 0, 1)
        pdf.cell(0, 10, f'Statement Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
        pdf.cell(0, 10, f'Current Balance: {account.balance:.2f}', 0, 1)
        
        # Add transaction summary
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'TRANSACTION SUMMARY', 0, 1)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(90, 10, 'Category', 1, 0, 'C')
        pdf.cell(30, 10, 'Count', 1, 0, 'C')
        pdf.cell(35, 10, 'Total', 1, 0, 'C')
        pdf.cell(35, 10, 'Average', 1, 1, 'C')
        
        pdf.set_font('Arial', '', 10)
        summary = account.get_transaction_summary()
        for category, data in summary.items():
            if data['count'] > 0:
                pdf.cell(90, 10, category, 1, 0)
                pdf.cell(30, 10, str(data['count']), 1, 0, 'C')
                pdf.cell(35, 10, f"{data['total']:.2f}", 1, 0, 'R')
                pdf.cell(35, 10, f"{data['average']:.2f}", 1, 1, 'R')
        
        # Add recent transactions
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'RECENT TRANSACTIONS', 0, 1)
        
        # Table header
        pdf.set_font('Arial', 'B', 10)
        col_widths = [35, 25, 25, 30, 30, 45]
        headers = ['Date', 'Type', 'Category', 'Amount', 'Balance', 'Description']
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
        pdf.ln()
        
        # Table rows
        pdf.set_font('Arial', '', 8)
        transactions = account.get_transaction_history(limit=50)
        
        for t in reversed(transactions):
            date_str = t[0].strftime("%Y-%m-%d\n%H:%M")
            txn_type = t[1]
            amount = t[2]
            balance = t[3]
            category = t[4] if len(t) > 4 else 'UNKNOWN'
            description = t[5] if len(t) > 5 else ''
            
            # Wrap long descriptions
            description = '\n'.join([description[i:i+20] for i in range(0, len(description), 20)]) if description else ''
            
            # Add cells with multi_cell for wrapping
            pdf.cell(col_widths[0], 10, date_str, 1, 0, 'C')
            pdf.cell(col_widths[1], 10, txn_type, 1, 0, 'C')
            pdf.cell(col_widths[2], 10, category, 1, 0, 'C')
            pdf.cell(col_widths[3], 10, f"{amount:.2f}", 1, 0, 'R')
            pdf.cell(col_widths[4], 10, f"{balance:.2f}", 1, 0, 'R')
            
            # Handle multi-line descriptions
            if '\n' in description:
                lines = description.split('\n')
                pdf.cell(col_widths[5], 10, lines[0] if lines else '', 1, 1, 'L')
                for line in lines[1:]:
                    pdf.cell(sum(col_widths[:5]), 10, '', 0, 1)
                    pdf.cell(sum(col_widths[:5]), 0, '', 0, 0)
                    pdf.cell(col_widths[5], 10, line, 1, 1, 'L')
            else:
                pdf.cell(col_widths[5], 10, description, 1, 1, 'L')
        
        # Add footer
        pdf.set_y(-15)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, 'End of Statement', 0, 0, 'C')
        
        # Save the PDF
        pdf.output(filename)
        print(f"PDF statement generated: {os.path.abspath(filename)}")
        return os.path.abspath(filename)