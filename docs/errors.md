# Nexum Errors

## Usage

```python
from nexum import NexumTypeError


def example():
  raise NexumTypeError("error message")
```

Output

```text
[Nexum] TypeError: error message
```

Available Nexum exceptions:

- NexumRuntimeError
- NexumTypeError
- NexumValueError
- NexumSyntaxError
- NexumKeyError
- NexumIndexError
- NexumAttributeError
- NexumFileNotFoundError
- NexumZeroDivisionError