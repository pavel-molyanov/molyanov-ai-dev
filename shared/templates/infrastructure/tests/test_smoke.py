"""Infrastructure smoke test to verify test setup works."""


def test_smoke_placeholder():
    """TODO: Replace with real smoke test (app import, config load)."""
    assert True


def test_python_version():
    """Verify Python version is 3.11+."""
    import sys
    assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version}"
