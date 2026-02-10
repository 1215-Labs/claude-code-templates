"""A well-formatted, type-correct Python module."""


def greet(name: str) -> str:
    """Return a greeting string."""
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


if __name__ == "__main__":
    print(greet("World"))
    print(add(1, 2))
