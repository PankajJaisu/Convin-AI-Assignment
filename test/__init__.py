# tests/__init__.py

"""
This module contains test cases for the Django application.

Tests are organized into unit tests and integration tests.
"""

# Optionally, you can import your test classes to make them available at the package level
from .test_views import DownloadBalanceSheetViewTests
from .test_integration import IntegrationTests
