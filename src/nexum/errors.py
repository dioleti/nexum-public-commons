# nexum/errors.py

class NexumError(Exception):
    prefix = "[Nexum]"

    def __init__(self, message: str):
        error_name = self.__class__.__name__.replace("Nexum", "")
        super().__init__(f"{self.prefix} {error_name}: {message}")

    def __str__(self):
        return self.args[0]


BASE_ERRORS = [
    RuntimeError,
    TypeError,
    ValueError,
    SyntaxError,
    KeyError,
    IndexError,
    AttributeError,
    FileNotFoundError,
    ZeroDivisionError,
]


def create_nexum_error(py_error):
    name = f"Nexum{py_error.__name__}"
    return type(name, (NexumError, py_error), {})

globals().update({
    f"Nexum{err.__name__}": create_nexum_error(err)
    for err in BASE_ERRORS
})

__all__ = ["NexumError"] + [
    f"Nexum{err.__name__}" for err in BASE_ERRORS
]
