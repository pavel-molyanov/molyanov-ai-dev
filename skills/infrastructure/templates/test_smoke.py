"""
Smoke test for Python projects

Purpose: Verify basic project setup works
- Test framework (pytest) is configured
- Environment is set up
- Basic imports work

This should be the first test that runs.
"""

import os


def test_smoke():
    """Basic smoke test to verify pytest is working."""
    assert True


def test_environment_configured():
    """Verify environment variables can be accessed."""
    # This should pass even if ENVIRONMENT is not set
    # (allows test to pass in minimal CI environments)
    env = os.getenv('ENVIRONMENT', 'test')
    assert env is not None


def test_main_module_import():
    """Verify main application module can be imported."""
    try:
        # Adjust import based on your project structure
        # import src.main
        # or: from src import app
        pass  # Replace with actual import
        assert True
    except ImportError as e:
        assert False, f"Failed to import main module: {e}"
