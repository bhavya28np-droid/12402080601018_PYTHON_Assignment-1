
"""
Q2: Optimized Password Audit with Pattern Constraints
Python 3.10+
"""

import re


def classify_password(password, banned_words):
    """Classify a password according to the assignment rules."""

    # 1. Check banned words, ignoring case.
    for word in banned_words:
        if word.lower() in password.lower():
            return "COMPROMISED"

    # 2. Check for a character repeated 4 or more times consecutively.
    if re.search(r"(.)\1{3,}", password):
        return "WEAK_PATTERN"

    # 3. Check minimum length.
    if len(password) < 8:
        return "WEAK_LENGTH"

    # 4. Check required character categories.
    has_lowercase = re.search(r"[a-z]", password)
    has_uppercase = re.search(r"[A-Z]", password)
    has_digit = re.search(r"[0-9]", password)
    has_special = re.search(r"[$#@!]", password)

    if all((has_lowercase, has_uppercase, has_digit, has_special)):
        return "STRONG"

    return "WEAK_PATTERN"


def main():
    print("=" * 45)
    print("       PASSWORD AUDIT SYSTEM")
    print("=" * 45)

    try:
        # Get banned words.
        while True:
            try:
                b = int(input("\nHow many banned words do you want to enter? "))
                if b < 1 or b > 10000:
                    print("Enter a number between 1 and 10000.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a whole number.")

        banned_words = []

        print("\nEnter the banned words one by one:")
        for i in range(b):
            while True:
                word = input(f"Banned word {i + 1}: ").strip()
                if word:
                    banned_words.append(word)
                    break
                print("The banned word cannot be empty.")

        # Get candidate passwords.
        while True:
            try:
                n = int(input("\nHow many passwords do you want to check? "))
                if n < 1 or n > 100000:
                    print("Enter a number between 1 and 100000.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a whole number.")

        print("\nEnter each password when prompted.")
        print("Allowed special symbols: $, #, @, !")
        print("-" * 45)

        for i in range(1, n + 1):
            while True:
                password = input(f"Enter password {i}: ")

                if not password:
                    print("Password cannot be empty. Try again.")
                elif len(password) > 100:
                    print("Password must not exceed 100 characters.")
                else:
                    break

            result = classify_password(password, banned_words)
            print(f"Result {i}: {result}")
            print("-" * 45)

        print("\nPassword audit completed successfully!")

    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped by user.")


if __name__ == "__main__":
    main()
