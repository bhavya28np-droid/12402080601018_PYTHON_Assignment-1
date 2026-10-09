
"""
Q6: Python Module Dependency Resolver
Python 3.10+
Uses graph traversal, topological sorting and cycle detection.
"""


def resolve_dependencies(modules, dependencies):
    """Return a valid loading order or a detected dependency cycle."""

    # Each module points to the modules it depends on.
    graph = {module: set() for module in modules}

    for module, dependency in dependencies:
        graph[module].add(dependency)

    visited = set()
    active = set()
    loading_order = []
    path = []
    cycle = []

    def dfs(module):
        nonlocal cycle

        if module in active:
            start = path.index(module)
            cycle = path[start:] + [module]
            return False

        if module in visited:
            return True

        active.add(module)
        path.append(module)

        # Sort dependencies to make the result deterministic.
        for dependency in sorted(graph[module]):
            if not dfs(dependency):
                return False

        path.pop()
        active.remove(module)
        visited.add(module)
        loading_order.append(module)
        return True

    # Preserve the order in which modules were entered.
    for module in modules:
        if module not in visited:
            if not dfs(module):
                return None, cycle

    return loading_order, None


def main():
    print("=" * 45)
    print("     PYTHON MODULE DEPENDENCY RESOLVER")
    print("=" * 45)

    try:
        while True:
            try:
                n = int(input("\nHow many modules? "))
                if 1 <= n <= 200000:
                    break
                print("Enter a number between 1 and 200000.")
            except ValueError:
                print("Please enter a valid whole number.")

        modules = []
        module_set = set()

        print("\nEnter each unique module name:")
        for i in range(n):
            while True:
                name = input(f"Module {i + 1}: ").strip()

                if not name:
                    print("Module name cannot be empty.")
                elif name in module_set:
                    print("Duplicate module name. Enter another name.")
                else:
                    modules.append(name)
                    module_set.add(name)
                    break

        while True:
            try:
                e = int(input("\nHow many dependency relationships? "))
                if 0 <= e <= 500000:
                    break
                print("Enter a number between 0 and 500000.")
            except ValueError:
                print("Please enter a valid whole number.")

        dependencies = []

        print("\nEnter dependencies as: MODULE DEPENDS_ON")
        print("Example: ui auth means ui depends on auth.")

        for i in range(e):
            while True:
                parts = input(f"Dependency {i + 1}: ").split()

                if len(parts) != 2:
                    print("Enter exactly two module names.")
                    continue

                module, dependency = parts

                if module not in module_set:
                    print(f"Unknown module: {module}")
                    continue

                if dependency not in module_set:
                    print(f"Unknown module: {dependency}")
                    continue

                dependencies.append((module, dependency))
                break

        order, cycle = resolve_dependencies(modules, dependencies)

        print("\n" + "=" * 45)
        print("RESULT")
        print("=" * 45)

        if cycle:
            print("CYCLE")
            print("Detected cycle:", " -> ".join(cycle))
        else:
            print("Valid loading order:")
            print(" ".join(order))

    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped by user.")


if __name__ == "__main__":
    main()
