
"""
Q7: Interactive Formula Validator with Custom Exceptions
Python 3.10+

Features:
- Integer and decimal operands
- Variables and assignments
- +, -, *, / and % operators
- Custom exceptions
- Input validation
- Interactive execution until 'quit'
"""

import re


# Custom exceptions
class FormulaError(Exception):
    """Base class for formula errors."""


class DivisionByZeroError(FormulaError):
    """Raised when division or modulo by zero occurs."""


class UnsupportedOperatorError(FormulaError):
    """Raised when an unsupported operator is used."""


class InvalidFormulaError(FormulaError):
    """Raised when a formula has invalid syntax."""


class FormulaCalculator:
    """Evaluates formulas and stores variable values."""

    NUMBER_PATTERN = r"(?:\d+(?:\.\d*)?|\.\d+)"
    VARIABLE_PATTERN = r"[A-Za-z_]\w*"

    def __init__(self):
        self.variables = {}

    def get_operand(self, token):
        """Return a numeric value or a stored variable value."""

        if re.fullmatch(self.NUMBER_PATTERN, token):
            if "." in token:
                return float(token)
            return int(token)

        if re.fullmatch(self.VARIABLE_PATTERN, token):
            if token not in self.variables:
                raise InvalidFormulaError(
                    f"Undefined variable: {token}"
                )
            return self.variables[token]

        raise InvalidFormulaError(f"Invalid operand: {token}")

    def evaluate(self, formula):
        """Evaluate a formula containing two operands and one operator."""

        formula = formula.strip()

        if not formula:
            raise InvalidFormulaError("Formula cannot be empty.")

        # Detect unsupported operators explicitly.
        if any(op in formula for op in ("**", "//", "&", "^")):
            raise UnsupportedOperatorError(
                "Unsupported operator."
            )

        pattern = (
            rf"({self.VARIABLE_PATTERN}|{self.NUMBER_PATTERN})"
            r"\s*([+\-*/%])\s*"
            rf"({self.VARIABLE_PATTERN}|{self.NUMBER_PATTERN})"
        )

        match = re.fullmatch(pattern, formula)

        if not match:
            # Recognize common unsupported operators.
            if re.search(r"[><=]", formula):
                raise UnsupportedOperatorError(
                    "Unsupported operator."
                )
            raise InvalidFormulaError("Invalid formula syntax.")

        left_token, operator, right_token = match.groups()

        left = self.get_operand(left_token)
        right = self.get_operand(right_token)

        if operator in ("/", "%") and right == 0:
            raise DivisionByZeroError(
                "Division or modulo by zero."
            )

        if operator == "+":
            return left + right
        elif operator == "-":
            return left - right
        elif operator == "*":
            return left * right
        elif operator == "/":
            return left / right
        elif operator == "%":
            return left % right

        raise UnsupportedOperatorError("Unsupported operator.")

    def process(self, statement):
        """Process an assignment or a formula."""

        statement = statement.strip()

        if not statement:
            raise InvalidFormulaError("Formula cannot be empty.")

        if "=" in statement:
            if statement.count("=") != 1:
                raise InvalidFormulaError(
                    "Invalid assignment syntax."
                )

            name, formula = map(
                str.strip, statement.split("=", 1)
            )

            if not re.fullmatch(self.VARIABLE_PATTERN, name):
                raise InvalidFormulaError(
                    "Invalid variable name."
                )

            if not formula:
                raise InvalidFormulaError(
                    "Assignment value cannot be empty."
                )

            # Allow direct numeric assignments, e.g. X = 10.
            if re.fullmatch(self.NUMBER_PATTERN, formula):
                value = self.get_operand(formula)
            else:
                value = self.evaluate(formula)

            self.variables[name] = value
            return value, name

        return self.evaluate(statement), None


def format_result(value):
    """Format whole-number results without a decimal suffix."""

    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    return str(value)


def main():
    calculator = FormulaCalculator()

    print("=" * 48)
    print("       INTERACTIVE FORMULA VALIDATOR")
    print("=" * 48)
    print("Supported operators: +, -, *, /, %")
    print("Assignment example: X = 10")
    print("Formula example: X + 5")
    print("Type 'quit' to exit.")
    print("-" * 48)

    while True:
        try:
            statement = input("\nEnter formula: ").strip()

            if statement.lower() == "quit":
                print("Calculator closed.")
                break

            try:
                result, assigned_variable = calculator.process(
                    statement
                )

                if assigned_variable is not None:
                    print(
                        f"{assigned_variable} = "
                        f"{format_result(result)}"
                    )
                else:
                    print(f"Result: {format_result(result)}")

            except DivisionByZeroError as error:
                print(f"DivisionByZeroError: {error}")

            except UnsupportedOperatorError as error:
                print(f"UnsupportedOperatorError: {error}")

            except InvalidFormulaError as error:
                print(f"InvalidFormulaError: {error}")

            except OverflowError:
                print("InvalidFormulaError: Result is too large.")

        except (KeyboardInterrupt, EOFError):
            print("\nCalculator closed.")
            break


if __name__ == "__main__":
    main()
