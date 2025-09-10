# account.py

from datetime import datetime, timedelta
import hashlib
import secrets

class AccountLockedError(Exception):
    pass

class Account:
    # Define common transaction categories
    TRANSACTION_CATEGORIES = [
        'DEPOSIT',
        'WITHDRAWAL',
        'TRANSFER_IN',
        'TRANSFER_OUT',
        'INTEREST',
        'FEE',
        'PAYMENT',
        'REFUND',
        'SALARY',
        'BILL_PAYMENT',
        'ONLINE_PURCHASE',
        'OTHER'
    ]
    
    def __init__(self, account_number, name, age, balance=0, account_type="Savings", pin_hash=None, salt=None):
        self.account_number = account_number
        self.name = name
        self.age = age
        self.balance = balance
        self.account_type = account_type
        self.status = "Active"  # Active, Inactive, Suspended
        self.transactions = []  # Format: (datetime, type, amount, balance_after, category, description)
        self.daily_withdrawals = []  # List to track daily withdrawals
        self.daily_limit = 50000  # Default daily withdrawal limit
        self.transaction_categories = {cat: 0 for cat in self.TRANSACTION_CATEGORIES}  # Category counters
        
        # PIN/Password security
        self.pin_hash = pin_hash
        self.salt = salt or secrets.token_hex(8)
        self.login_attempts = 0
        self.last_login_attempt = None
        self.locked_until = None
        
    def set_pin(self, pin):
        """Set a new PIN for the account."""
        if not isinstance(pin, str) or not pin.isdigit() or len(pin) != 4:
            raise ValueError("PIN must be a 4-digit number")
        self.salt = secrets.token_hex(8)
        self.pin_hash = self._hash_pin(pin)
        
    def verify_pin(self, pin):
        """Verify if the provided PIN is correct."""
        if self.locked_until and datetime.now() < self.locked_until:
            remaining = (self.locked_until - datetime.now()).seconds // 60
            raise AccountLockedError(f"Account locked. Try again in {remaining} minutes.")
            
        if not self.pin_hash:
            return True  # No PIN set yet
            
        if self._hash_pin(pin) == self.pin_hash:
            self.login_attempts = 0
            return True
            
        self.login_attempts += 1
        self.last_login_attempt = datetime.now()
        
        if self.login_attempts >= 3:
            self.locked_until = datetime.now() + timedelta(minutes=30)
            raise AccountLockedError("Too many failed attempts. Account locked for 30 minutes.")
            
        return False
    
    def _hash_pin(self, pin):
        """Hash the PIN with salt."""
        return hashlib.pbkdf2_hmac('sha256', pin.encode(), self.salt.encode(), 100000).hex()
    
    def reset_login_attempts(self):
        """Reset failed login attempts."""
        self.login_attempts = 0
        self.locked_until = None

    def get_daily_withdrawal_total(self, date=None):
        """Calculate total withdrawals for the specified date (or today if not specified)."""
        if date is None:
            date = datetime.now().date()
        
        # Filter withdrawals for the specified date
        return sum(amount for d, amount in self.daily_withdrawals 
                  if d.date() == date)
    
    def can_withdraw(self, amount):
        """Check if the withdrawal is allowed based on daily limits."""
        if self.status != 'Active':
            return False, "Account is not active."
            
        if amount <= 0:
            return False, "Withdrawal amount must be positive."
            
        # Check minimum balance
        min_balance = 500 if self.account_type.lower() == 'savings' else 1000
        if self.balance - amount < min_balance:
            return False, f"Insufficient funds. Minimum balance of {min_balance} must be maintained."
            
        # Check daily limit
        today_total = self.get_daily_withdrawal_total()
        if today_total + amount > self.daily_limit:
            remaining = self.daily_limit - today_total
            return False, f"Daily withdrawal limit exceeded. You can withdraw up to {remaining} more today."
            
        return True, ""
    
    def add_withdrawal(self, amount):
        """Record a withdrawal in the daily transactions."""
        self.daily_withdrawals.append((datetime.now(), amount))
        self.balance -= amount
        
        # Clean up old records (older than 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        self.daily_withdrawals = [(d, amt) for d, amt in self.daily_withdrawals 
                                 if d > week_ago]

    def get_transaction_history(self, limit=None, category=None):
        """Get the transaction history for this account.
        
        Args:
            limit: Maximum number of transactions to return
            category: Filter transactions by category
            
        Returns:
            List of transactions, optionally filtered by category
        """
        transactions = self.transactions
        
        # Filter by category if specified
        if category and category in self.TRANSACTION_CATEGORIES:
            transactions = [t for t in transactions if t[4] == category]
            
        # Apply limit
        if limit and limit > 0:
            return transactions[-limit:]
            
        return transactions
        
    def get_transaction_summary(self):
        """Get a summary of transactions by category."""
        summary = {}
        for category in self.TRANSACTION_CATEGORIES:
            category_txns = [t for t in self.transactions if t[4] == category]
            if category_txns:
                count = len(category_txns)
                total = sum(t[2] for t in category_txns)
                summary[category] = {
                    'count': count,
                    'total': total,
                    'average': total / count if count > 0 else 0
                }
        return summary

    def add_transaction(self, transaction_type, amount, category='OTHER', description=""):
        """Add a transaction to the account's transaction history.
        
        Args:
            transaction_type: Type of transaction (e.g., 'DEPOSIT', 'WITHDRAWAL')
            amount: Transaction amount (positive for credits, negative for debits)
            category: Transaction category (must be one of TRANSACTION_CATEGORIES)
            description: Optional description of the transaction
        """
        # Validate category
        if category not in self.TRANSACTION_CATEGORIES:
            category = 'OTHER'
            
        # Update balance
        self.balance += amount
        
        # Record transaction
        transaction = (
            datetime.now(),
            transaction_type,
            amount,
            self.balance,
            category,
            description
        )
        self.transactions.append(transaction)
        
        # Update category counter
        self.transaction_categories[category] += 1
        
        return transaction

    def __repr__(self):
        return f"Account(number={self.account_number}, name='{self.name}', balance={self.balance}, status='{self.status}')"