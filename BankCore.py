class Account:
    def __init__(self, account_number, holder_name, balance=0.0):
        self._account_number = str(account_number)
        self._holder_name = holder_name
        self._balance = float(balance)
        self._transactions = []
        self._record_transaction("Account opened", self._balance)

    @property
    def account_number(self):
        return self._account_number

    @property
    def holder_name(self):
        return self._holder_name

    @property
    def balance(self):
        return self._balance

    @property
    def transactions(self):
        return self._transactions.copy()

    def _record_transaction(self, transaction_type, amount):
        self._transactions.append({
            "type": transaction_type,
            "amount": amount,
            "balance": self._balance
        })

    def deposit(self, amount):
        amount = float(amount)
        if amount <= 0:
            print("Deposit amount must be greater than zero.")
            return False

        self._balance += amount
        self._record_transaction("Deposit", amount)
        print(f"Deposit successful. New balance: PKR {self._balance:,.2f}")
        return True

    def withdraw(self, amount):
        amount = float(amount)
        if amount <= 0:
            print("Withdrawal amount must be greater than zero.")
            return False
        if amount > self._balance:
            print("Transaction declined: insufficient funds.")
            return False

        self._balance -= amount
        self._record_transaction("Withdrawal", amount)
        print(f"Withdrawal successful. New balance: PKR {self._balance:,.2f}")
        return True

    def account_type(self):
        return "Standard Account"

    def display_details(self):
        print("\n" + "-" * 48)
        print(f"Account Number : {self.account_number}")
        print(f"Account Holder : {self.holder_name}")
        print(f"Account Type   : {self.account_type()}")
        print(f"Balance        : PKR {self.balance:,.2f}")
        print("-" * 48)

    def show_transactions(self):
        print(f"\nTransaction History — {self.account_number}")
        if not self._transactions:
            print("No transactions recorded.")
            return

        print(f"{'TYPE':<20} {'AMOUNT (PKR)':>15} {'BALANCE (PKR)':>15}")
        print("-" * 54)
        for transaction in self._transactions:
            print(
                f"{transaction['type']:<20} "
                f"{transaction['amount']:>15,.2f} "
                f"{transaction['balance']:>15,.2f}"
            )


class SavingsAccount(Account):
    def __init__(self, account_number, holder_name, balance=0.0, interest_rate=3.0):
        super().__init__(account_number, holder_name, balance)
        self.interest_rate = float(interest_rate)

    def account_type(self):
        return "Savings Account"

    def apply_interest(self):
        interest = self.balance * self.interest_rate / 100
        self._balance += interest
        self._record_transaction("Interest", interest)
        print(f"Interest applied: PKR {interest:,.2f}")
        print(f"New balance: PKR {self.balance:,.2f}")


class CurrentAccount(Account):
    def __init__(self, account_number, holder_name, balance=0.0, overdraft_limit=5000.0):
        super().__init__(account_number, holder_name, balance)
        self.overdraft_limit = float(overdraft_limit)

    def account_type(self):
        return "Current Account"

    def withdraw(self, amount):
        amount = float(amount)
        if amount <= 0:
            print("Withdrawal amount must be greater than zero.")
            return False
        if amount > self.balance + self.overdraft_limit:
            print("Transaction declined: overdraft limit exceeded.")
            return False

        self._balance -= amount
        self._record_transaction("Withdrawal", amount)
        print(f"Withdrawal successful. New balance: PKR {self.balance:,.2f}")
        if self.balance < 0:
            print(f"Overdraft used: PKR {abs(self.balance):,.2f}")
        return True


def load_sample_accounts():
    return [
        SavingsAccount("BC1001", "Ayesha Khan", 25000, 3.5),
        CurrentAccount("BC1002", "Hamza Ali", 12000, 8000),
        SavingsAccount("BC1003", "Sara Ahmed", 18000, 2.5),
        CurrentAccount("BC1004", "Usman Malik", 5000, 10000),
    ]


def find_account(accounts, account_number):
    for account in accounts:
        if account.account_number.lower() == account_number.strip().lower():
            return account
    return None


def get_amount(prompt):
    while True:
        try:
            amount = float(input(prompt).strip())
            if amount > 0:
                return amount
            print("Enter an amount greater than zero.")
        except ValueError:
            print("Enter a valid numeric amount.")


def choose_account(accounts):
    account_number = input("Enter account number: ").strip()
    account = find_account(accounts, account_number)
    if account is None:
        print("Account not found.")
    return account


def show_all_accounts(accounts):
    print("\n" + "=" * 72)
    print(f"{'ACCOUNT':<12} {'HOLDER':<20} {'TYPE':<20} {'BALANCE (PKR)':>16}")
    print("=" * 72)
    for account in accounts:
        print(
            f"{account.account_number:<12} "
            f"{account.holder_name:<20} "
            f"{account.account_type():<20} "
            f"{account.balance:>16,.2f}"
        )
    print("=" * 72)


def show_menu():
    print("""
==================== BANKCORE ====================
1. View all accounts
2. View account details
3. Deposit money
4. Withdraw money
5. View transaction history
6. Apply savings interest
0. Exit
==================================================
""")


def main():
    accounts = load_sample_accounts()
    print("Welcome to BankCore — Banking System")
    print("Demo accounts are preloaded for testing.")
    print("Use account numbers BC1001, BC1002, BC1003, or BC1004.")

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Thank you for using BankCore.")
            print("Demo changes will not be saved after exit.")
            break
        elif choice == "1":
            show_all_accounts(accounts)
        elif choice == "2":
            account = choose_account(accounts)
            if account:
                account.display_details()
        elif choice == "3":
            account = choose_account(accounts)
            if account:
                account.deposit(get_amount("Deposit amount (PKR): "))
        elif choice == "4":
            account = choose_account(accounts)
            if account:
                account.withdraw(get_amount("Withdrawal amount (PKR): "))
        elif choice == "5":
            account = choose_account(accounts)
            if account:
                account.show_transactions()
        elif choice == "6":
            account = choose_account(accounts)
            if account:
                if isinstance(account, SavingsAccount):
                    account.apply_interest()
                else:
                    print("Interest can only be applied to savings accounts.")
        else:
            print("Invalid option. Choose a number from the menu.")

        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main()
