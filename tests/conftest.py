import pytest

@pytest.fixture(autouse=True)
def _isolate_tests():
    yield