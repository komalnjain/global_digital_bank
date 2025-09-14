# Global Digital Bank

## Overview
Global Digital Bank is a Python-based banking system that provides various features for managing accounts, transactions, and reports. It is designed to simulate the functionalities of a digital banking platform.

## Features

### Account Management
- **Create Account**: Create new accounts with initial deposits.
- **Upgrade Account Type**: Change account type (e.g., Savings to Current).
- **Reopen Closed Account**: Reactivate previously closed accounts.
- **Rename Account Holder**: Update the name of an account holder.
- **Delete All Accounts**: Admin-only feature to clear all account data.

### Transactions
- **Deposit**: Add funds to an account.
- **Withdraw**: Deduct funds from an account with daily limits and minimum balance checks.
- **Transfer Funds**: Transfer money between accounts with PIN verification.
- **Transaction History Viewer**: View past transactions for a specific account.

### Calculations
- **Simple Interest Calculator**: Calculate interest on balance at a fixed rate.
- **Compound Interest Calculator**: Calculate compound interest based on rate, years, and frequency.
- **Average Balance Calculator**: Compute the average balance across all accounts.

### Reports
- **Export Account Data**: Save account details to a JSON file.
- **Generate Account Statement**: Create detailed account statements in text or PDF format.
- **Import Accounts from File**: Load extra accounts from a CSV file.

### Insights
- **Youngest Account Holder**: Display details of the youngest customer.
- **Oldest Account Holder**: Display details of the oldest customer.
- **Top N Accounts by Balance**: List accounts sorted by balance.

### Security
- **PIN/Password Protection**: Add PIN verification for transactions.
- **Age Verification**: Reject account creation for users under 18.

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/komalnjain/global_digital_bank.git
   ```
2. Navigate to the project directory:
   ```bash
   cd global_digital_bank
   ```
3. Run the program:
   ```bash
   python main.py
   ```

## File Structure
- `main.py`: Entry point for the application.
- `banking_system.py`: Contains the core logic for account and transaction management.
- `account.py`: Defines the `Account` class and related functionalities.
- `data_handler.py`: Handles data persistence and logging.
- `accounts.csv`: Stores account data.
- `extra_accounts.csv`: Sample file for importing additional accounts.

## Requirements
- Python 3.8 or higher
- Required libraries:
  - `fpdf` (for PDF generation)

Install dependencies using:
```bash
pip install fpdf
```

## Contributing
Feel free to fork the repository and submit pull requests for improvements or new features.

## License
This project is licensed under the MIT License.

## Author
Komal N Jain