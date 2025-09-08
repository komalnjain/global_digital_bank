# data_handler.py
import csv
import logging

ACCOUNTS_FILE = 'accounts.csv'
TRANSACTIONS_LOG = 'transactions.log'

# Configure logging for transactions
logging.basicConfig(filename=TRANSACTIONS_LOG, level=logging.INFO,
                    format='%(asctime)s,%(account_number)s,%(operation)s,%(amount)s,%(balance_after)s')
transaction_logger = logging.getLogger('transactions')

def save_accounts(accounts):
    """Saves a list of Account objects to accounts.csv."""
    with open(ACCOUNTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['account_number', 'name', 'age', 'balance', 'account_type', 'status', 'pin'])
        for account in accounts.values():
            writer.writerow([account.account_number, account.name, account.age, account.balance,
                             account.account_type, account.status, account.pin])
    print("All accounts have been saved successfully.")

def load_accounts():
    """Loads a list of Account objects from accounts.csv."""
    from account import Account
    accounts = {}
    try:
        with open(ACCOUNTS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                account = Account(
                    account_number=int(row['account_number']),
                    name=row['name'],
                    age=int(row['age']),
                    balance=float(row['balance']),
                    account_type=row['account_type'],
                    status=row['status'],
                    pin=row['pin'] if row['pin'] != 'None' else None
                )
                accounts[account.account_number] = account
        print("Accounts loaded from file.")
    except FileNotFoundError:
        print("No existing accounts file found. Starting with an empty list.")
    return accounts