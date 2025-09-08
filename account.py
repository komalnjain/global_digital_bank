# account.py

class Account:
    def __init__(self, account_number, name, age, balance, account_type, status='Active', pin=None):
        self.account_number = account_number
        self.name = name
        self.age = age
        self.balance = balance
        self.account_type = account_type
        self.status = status
        self.pin = pin

    def __repr__(self):
        return f"Account(number={self.account_number}, name='{self.name}', balance={self.balance}, status='{self.status}')"