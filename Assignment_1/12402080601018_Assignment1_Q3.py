
"""
Q3: Recursive Expression Engine with Memoization
Python 3.10+
Supported operators: +, -, *
Supports parentheses, variables, memoization and cycle detection.
"""

import re


class InvalidExpression(Exception):
    """Raised when an expression is invalid."""


class CircularDependency(Exception):
    """Raised when variables depend on each other in a cycle."""


def tokenize(expression):
    """Convert an expression into tokens without using eval()."""
    pattern = r"\s*(\d+|[A-Za-z_]\w*|[()+*-])"
    tokens = []
    position = 0

    while position < len(expression):
        match = re.match(pattern, expression[position:])

        if not match:
            if expression[position:].strip() == "":
                break
            raise InvalidExpression("Invalid expression syntax.")

        tokens.append(match.group(1))
        position += match.end()

    if not tokens:
        raise InvalidExpression("Expression cannot be empty.")

    return tokens


class ExpressionParser:
    """Recursive-descent parser for mathematical expressions."""

    def __init__(self, expression, resolve_variable):
        self.tokens = tokenize(expression)
        self.position = 0
        self.resolve_variable = resolve_variable

    def current(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def parse(self):
        result = self.parse_expression()

        if self.current() is not None:
            raise InvalidExpression("Unexpected token.")

        return result

    def parse_expression(self):
        """Evaluate addition and subtraction."""
        result = self.parse_term()

        while self.current() in ("+", "-"):
            operator = self.current()
            self.position += 1
            right = self.parse_term()

            if operator == "+":
                result += right
            else:
                result -= right

        return result

    def parse_term(self):
        """Evaluate multiplication."""
        result = self.parse_factor()

        while self.current() == "*":
            self.position += 1
            result *= self.parse_factor()

        return result

    def parse_factor(self):
        """Evaluate numbers, variables, parentheses and unary signs."""
        token = self.current()

        if token is None:
            raise InvalidExpression("Unexpected end of expression.")

        if token == "+":
            self.position += 1
            return self.parse_factor()

        if token == "-":
            self.position += 1
            return -self.parse_factor()

        if token == "(":
            self.position += 1
            result = self.parse_expression()

            if self.current() != ")":
                raise InvalidExpression("Missing closing parenthesis.")

            self.position += 1
            return result

        if token.isdigit():
            self.position += 1
            return int(token)

        if re.fullmatch(r"[A-Za-z_]\w*", token):
            self.position += 1
            return self.resolve_variable(token)

        raise InvalidExpression("Invalid expression token.")


def main():
    print("=" * 50)
    print("       RECURSIVE EXPRESSION ENGINE")
    print("=" * 50)
    print("Supported operators: +, -, *")
    print("Use parentheses to control evaluation order.")

    try:
        while True:
            try:
                n = int(input("\nHow many variable definitions? "))
                if n < 1 or n > 200000:
                    print("Enter a number between 1 and 200000.")
                    continue
                break
            except ValueError:
                print("Please enter a valid whole number.")

        expressions = {}

        print("\nEnter definitions in the form: variable = expression")

        for i in range(1, n + 1):
            definition = input(f"Definition {i}: ").strip()

            if "=" not in definition:
                print("INVALID")
                return

            name, expression = map(str.strip, definition.split("=", 1))

            if not re.fullmatch(r"[A-Za-z_]\w*", name):
                print("INVALID")
                return

            if not expression or name in expressions:
                print("INVALID")
                return

            expressions[name] = expression

        target = input("\nExpression to evaluate: ").strip()

        if not target:
            print("INVALID")
            return

        # Cache values that have already been evaluated.
        memo = {}
        visiting = set()

        def resolve_variable(name):
            if name in memo:
                return memo[name]

            if name in visiting:
                raise CircularDependency()

            if name not in expressions:
                raise InvalidExpression("Undefined variable.")

            visiting.add(name)

            try:
                parser = ExpressionParser(expressions[name], resolve_variable)
                value = parser.parse()
                memo[name] = value
                return value
            finally:
                visiting.remove(name)

        parser = ExpressionParser(target, resolve_variable)
        result = parser.parse()

        # Assignment requires a signed 64-bit integer result.
        if not -(2**63) <= result <= 2**63 - 1:
            print("INVALID")
            return

        print("\nResult:", result)

    except CircularDependency:
        print("\nCYCLE")
    except (InvalidExpression, RecursionError, ValueError):
        print("\nINVALID")
    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped by user.")


if __name__ == "__main__":
    main()
