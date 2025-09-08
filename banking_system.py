# banking_system.py
import random
from account import Account
from data_handler import save_accounts, transaction_logger

class BankingSystem:
    def __init__(self):
        self.accounts = {}
        self.next_account_number = 1001

    def create_account(self, name, age, account_type):
        """Creates a new account with validation."""
        if age < 18:
            print("Account creation failed: Age must be 18 or above.")
            return None
        
        if account_type.lower() not in ["savings", "current"]:
            print("Account creation failed: Invalid account type. Must be 'Savings' or 'Current'.")
            return None
            
        initial_deposit = 0
        if account_type.lower() == "savings":
            initial_deposit = 500
        elif account_type.lower() == "current":
            initial_deposit = 1000

        account = Account(self.next_account_number, name, age, initial_deposit, account_type.capitalize())
        self.accounts[self.next_account_number] = account
        self.next_account_number += 1
        print(f"Account created successfully! Account Number: {account.account_number}")
        
        # Log the creation as a transaction
        transaction_logger.info('', extra={
            'account_number': account.account_number,
            'operation': 'Create',
            'amount': initial_deposit,
            'balance_after': initial_deposit
        })
        return account

    def deposit(self, account_number, amount):
        """Adds funds to an account."""
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return
        
        if amount <= 0:
            print("Error: Deposit amount must be a positive number.")
            return

        if amount > 100000:
            print("Error: Single deposit cannot exceed 100,000.")
            return
        
        account.balance += amount
        print(f"Deposit successful. New balance: {account.balance}")
        
        # Log the transaction
        transaction_logger.info('', extra={
            'account_number': account.account_number,
            'operation': 'Deposit',
            'amount': amount,
            'balance_after': account.balance
        })

    def withdraw(self, account_number, amount):
        """Deducts funds from an account if sufficient balance exists."""
        account = self.accounts.get(account_number)
        if not account:
            print("Error: Account not found.")
            return
        
        if amount <= 0:
            print("Error: Withdrawal amount must be a positive number.")
            return
        
        min_balance = 500 if account.account_type == "Savings" else 1000
        if account.balance - amount < min_balance:
            print("Error: Insufficient funds or withdrawal would reduce balance below minimum.")
            return

        account.balance -= amount
        print(f"Withdrawal successful. New balance: {account.balance}")
        
        # Log the transaction
        transaction_logger.info('', extra={
            'account_number': account.account_number,
            'operation': 'Withdraw',
            'amount': -amount,
            'balance_after': account.balance
        })

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
        print(f"Account {account_number} has been closed.")
        
        # Log the transaction
        transaction_logger.info('', extra={
            'account_number': account.account_number,
            'operation': 'Close',
            'amount': 0,
            'balance_after': account.balance
        })
        
    def system_exit_with_autosave(self):
        """Saves data and exits gracefully."""
        print("Saving data...")
        save_accounts(self.accounts)
        print("Goodbye!")
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

    def transaction_history_viewer(self, account_number):
        """Displays all past transactions for a given account."""
        # This requires reading and parsing the log file, which is a bit more complex.
        # A simpler approach for this example is to show the log file content for the account.
        print(f"Showing transaction history for account {account_number}:")
        try:
            with open('transactions.log', 'r') as f:
                for line in f:
                    if str(account_number) in line:
                        print(line.strip())
        except FileNotFoundError:
            print("Transaction log file not found.")

    def transfer_funds(self, from_account_num, to_account_num, amount):
        """Transfers funds between two accounts."""
        from_account = self.accounts.get(from_account_num)
        to_account = self.accounts.get(to_account_num)

        if not from_account or not to_account:
            print("Error: One or both accounts not found.")
            return
        
        if from_account.status == 'Inactive' or to_account.status == 'Inactive':
            print("Error: Both accounts must be active to transfer funds.")
            return
            
        min_balance_from = 500 if from_account.account_type == "Savings" else 1000
        if from_account.balance - amount < min_balance_from:
            print("Error: Insufficient funds or transfer would violate minimum balance for the sender.")
            return

        from_account.balance -= amount
        to_account.balance += amount
        print(f"Transfer of {amount} successful from {from_account_num} to {to_account_num}.")
        
        # Log the two separate transactions
        transaction_logger.info('', extra={
            'account_number': from_account.account_number,
            'operation': 'Transfer-Debit',
            'amount': -amount,
            'balance_after': from_account.balance
        })
        transaction_logger.info('', extra={
            'account_number': to_account.account_number,
            'operation': 'Transfer-Credit',
            'amount': amount,
            'balance_after': to_account.balance
        })