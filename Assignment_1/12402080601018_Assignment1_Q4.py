
"""
Q4: Exception-Safe CSV Transaction Splitter
Python 3.10+
"""

import csv
import os
from decimal import Decimal, InvalidOperation
from datetime import datetime


REQUIRED_COLUMNS = [
    "transaction_id",
    "account_id",
    "type",
    "amount",
    "timestamp",
]


def validate_transaction(row, line_number):
    """Validate one transaction and return its normalized data."""

    for column in REQUIRED_COLUMNS:
        if column not in row or not str(row[column] or "").strip():
            raise ValueError(f"Missing or empty {column}")

    transaction_id = row["transaction_id"].strip()
    account_id = row["account_id"].strip()
    transaction_type = row["type"].strip().upper()
    amount_text = row["amount"].strip()
    timestamp = row["timestamp"].strip()

    if transaction_type not in ("CREDIT", "DEBIT"):
        raise ValueError("Type must be CREDIT or DEBIT")

    try:
        amount = Decimal(amount_text)
    except InvalidOperation:
        raise ValueError("Amount is not numeric") from None

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be a positive finite number")

    try:
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValueError(
            "Timestamp must use YYYY-MM-DDTHH:MM:SS format"
        ) from None

    return {
        "transaction_id": transaction_id,
        "account_id": account_id,
        "type": transaction_type,
        "amount": format(amount, "f"),
        "timestamp": timestamp,
    }, amount


def write_csv(filename, fieldnames, rows):
    """Write records to a CSV file with a header."""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_transactions(input_path):
    """Validate, split and summarize transactions."""

    credit_rows = []
    debit_rows = []
    error_rows = []
    account_balances = {}

    with open(input_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("Input CSV is empty or has no header.")

        reader.fieldnames = [
            name.strip() if name else "" for name in reader.fieldnames
        ]

        missing_columns = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
        if missing_columns:
            raise ValueError(
                "Missing CSV columns: " + ", ".join(sorted(missing_columns))
            )

        for line_number, row in enumerate(reader, start=2):
            try:
                if None in row:
                    raise ValueError("Unexpected extra CSV fields")

                transaction, amount = validate_transaction(row, line_number)

                if transaction["type"] == "CREDIT":
                    credit_rows.append(transaction)
                    signed_amount = amount
                else:
                    debit_rows.append(transaction)
                    signed_amount = -amount

                account_id = transaction["account_id"]
                account_balances[account_id] = (
                    account_balances.get(account_id, Decimal("0"))
                    + signed_amount
                )

            except (ValueError, TypeError, AttributeError) as error:
                original = {
                    column: row.get(column, "")
                    for column in REQUIRED_COLUMNS
                }
                original["error_reason"] = (
                    f"Line {line_number}: {error}"
                )
                error_rows.append(original)

    error_fields = REQUIRED_COLUMNS + ["error_reason"]

    # Create output files in the input CSV's directory.
    output_dir = os.path.dirname(os.path.abspath(input_path))

    write_csv(
        os.path.join(output_dir, "credit.csv"),
        REQUIRED_COLUMNS,
        credit_rows,
    )
    write_csv(
        os.path.join(output_dir, "debit.csv"),
        REQUIRED_COLUMNS,
        debit_rows,
    )
    write_csv(
        os.path.join(output_dir, "error.csv"),
        error_fields,
        error_rows,
    )

    print("\n" + "=" * 45)
    print("    TRANSACTION PROCESSING SUMMARY")
    print("=" * 45)
    print(f"Valid credits : {len(credit_rows)}")
    print(f"Valid debits  : {len(debit_rows)}")
    print(f"Rejected rows : {len(error_rows)}")
    print("\nFiles created: credit.csv, debit.csv, error.csv")

    print("\nAccount-wise net amounts (descending absolute value):")

    sorted_accounts = sorted(
        account_balances.items(),
        key=lambda item: (-abs(item[1]), item[0]),
    )

    if not sorted_accounts:
        print("No valid transactions to summarize.")
    else:
        for account_id, balance in sorted_accounts:
            print(f"{account_id}: {balance:.2f}")


def main():
    print("=" * 45)
    print("     CSV TRANSACTION SPLITTER")
    print("=" * 45)
    print("Required columns:")
    print(", ".join(REQUIRED_COLUMNS))

    while True:
        input_path = input(
            "\nEnter the path of your input CSV file: "
        ).strip().strip('"')

        if not input_path:
            print("File path cannot be empty.")
            continue

        if not os.path.isfile(input_path):
            print("File not found. Check the path and try again.")
            continue

        try:
            process_transactions(input_path)
            break
        except (OSError, csv.Error, ValueError) as error:
            print(f"Processing error: {error}")
            break
        except Exception as error:
            print(f"Unexpected error: {error}")
            break


if __name__ == "__main__":
    main()
