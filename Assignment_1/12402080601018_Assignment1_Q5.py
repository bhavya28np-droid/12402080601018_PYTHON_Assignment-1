
"""
Q5: Object-Oriented Bank Settlement System
Python 3.10+
"""

from copy import deepcopy


class BankError(Exception):
    """Base exception for banking operations."""


class AccountNotFoundError(BankError):
    """Raised when an account does not exist."""


class InvalidAmountError(BankError):
    """Raised when an amount is invalid."""


class InsufficientFundsError(BankError):
    """Raised when a withdrawal or transfer exceeds the balance."""


class Account:
    """Represents a bank account."""

    def __init__(self, account_id, balance):
        if balance < 0:
            raise InvalidAmountError("Initial balance cannot be negative.")

        self.account_id = account_id
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Amount must be positive.")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Amount must be positive.")
        if amount > self._balance:
            raise InsufficientFundsError("Insufficient funds.")
        self._balance -= amount


class Transaction:
    """Stores details of a banking transaction."""

    def __init__(self, operation, details):
        self.operation = operation
        self.details = details


class Bank:
    """Manages accounts, transactions and batch rollback."""

    def __init__(self):
        self.accounts = {}
        self.history = []
        self.failed_batches = []
        self.batch_number = 0
        self.batch_active = False
        self.batch_failed = False
        self.batch_snapshot = None
        self.batch_history_length = 0

    def add_account(self, account_id, balance):
        if account_id in self.accounts:
            raise BankError(f"Duplicate account: {account_id}")
        self.accounts[account_id] = Account(account_id, balance)

    def get_account(self, account_id):
        if account_id not in self.accounts:
            raise AccountNotFoundError(
                f"Account {account_id} does not exist."
            )
        return self.accounts[account_id]

    def execute(self, operation, *args):
        """Execute an operation and record successful transactions."""

        operation = operation.upper()

        if operation == "DEPOSIT":
            account_id, amount = args
            self.get_account(account_id).deposit(amount)

        elif operation == "WITHDRAW":
            account_id, amount = args
            self.get_account(account_id).withdraw(amount)

        elif operation == "TRANSFER":
            source_id, target_id, amount = args

            if amount <= 0:
                raise InvalidAmountError("Amount must be positive.")

            source = self.get_account(source_id)
            target = self.get_account(target_id)

            # Validate before changing either account.
            if amount > source.balance:
                raise InsufficientFundsError("Insufficient funds.")

            source.withdraw(amount)
            target.deposit(amount)

        else:
            raise BankError(f"Unsupported operation: {operation}")

        self.history.append(Transaction(operation, args))

    def begin_batch(self):
        if self.batch_active:
            raise BankError("A batch is already active.")

        self.batch_number += 1
        self.batch_active = True
        self.batch_failed = False
        self.batch_snapshot = {
            account_id: account.balance
            for account_id, account in self.accounts.items()
        }
        self.batch_history_length = len(self.history)

    def end_batch(self):
        if not self.batch_active:
            raise BankError("No batch is active.")

        if self.batch_failed:
            for account_id, balance in self.batch_snapshot.items():
                self.accounts[account_id]._balance = balance

            del self.history[self.batch_history_length:]
            self.failed_batches.append(self.batch_number)

        self.batch_active = False
        self.batch_failed = False
        self.batch_snapshot = None

    def print_report(self):
        print("\n" + "=" * 40)
        print("       BANK SETTLEMENT REPORT")
        print("=" * 40)

        print("Final account balances:")
        for account_id in sorted(self.accounts):
            print(f"{account_id} {self.accounts[account_id].balance}")

        if self.failed_batches:
            print("FAILED " + " ".join(map(str, self.failed_batches)))
        else:
            print("FAILED NONE")


def main():
    print("=" * 40)
    print("    BANK SETTLEMENT SYSTEM")
    print("=" * 40)

    bank = Bank()

    try:
        while True:
            try:
                count = int(input("\nHow many accounts? "))
                if count < 1 or count > 100000:
                    print("Enter a number from 1 to 100000.")
                    continue
                break
            except ValueError:
                print("Enter a valid whole number.")

        print("\nEnter each account as: ACCOUNT_ID BALANCE")
        for i in range(count):
            while True:
                try:
                    parts = input(f"Account {i + 1}: ").split()

                    if len(parts) != 2:
                        raise ValueError("Enter an ID and a balance.")

                    account_id = parts[0]
                    balance = int(parts[1])

                    bank.add_account(account_id, balance)
                    break

                except (ValueError, BankError) as error:
                    print(f"Invalid account: {error}")

        while True:
            try:
                operation_count = int(
                    input("\nHow many operations will you enter? ")
                )
                if 1 <= operation_count <= 300000:
                    break
                print("Enter a number from 1 to 300000.")
            except ValueError:
                print("Enter a valid whole number.")

        print("\nAvailable operations:")
        print("DEPOSIT account amount")
        print("WITHDRAW account amount")
        print("TRANSFER source target amount")
        print("BATCH_BEGIN")
        print("BATCH_END")

        for i in range(operation_count):
            command = input(f"\nOperation {i + 1}: ").split()

            if not command:
                print("Empty operation.")
                continue

            operation = command[0].upper()

            if bank.batch_failed and bank.batch_active:
                if operation == "BATCH_END" and len(command) == 1:
                    bank.end_batch()
                else:
                    print("Batch already failed; operation skipped.")
                continue

            try:
                if operation == "BATCH_BEGIN" and len(command) == 1:
                    bank.begin_batch()
                    print("Batch started.")

                elif operation == "BATCH_END" and len(command) == 1:
                    bank.end_batch()
                    print("Batch ended.")

                elif operation == "DEPOSIT" and len(command) == 3:
                    bank.execute(
                        operation, command[1], int(command[2])
                    )
                    print("Deposit successful.")

                elif operation == "WITHDRAW" and len(command) == 3:
                    bank.execute(
                        operation, command[1], int(command[2])
                    )
                    print("Withdrawal successful.")

                elif operation == "TRANSFER" and len(command) == 4:
                    bank.execute(
                        operation,
                        command[1],
                        command[2],
                        int(command[3]),
                    )
                    print("Transfer successful.")

                else:
                    raise BankError("Invalid operation format.")

            except (ValueError, BankError) as error:
                print(f"Transaction failed: {error}")

                if bank.batch_active:
                    bank.batch_failed = True

        # Safely roll back an unfinished batch.
        if bank.batch_active:
            bank.end_batch()

        bank.print_report()

    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped by user.")


if __name__ == "__main__":
    main()
