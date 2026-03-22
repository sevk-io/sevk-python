"""
Pytest configuration and fixtures for Sevk Python SDK tests
"""

import os
import pytest


# Test configuration
DEFAULT_BASE_URL = "https://api.sevk.io"


@pytest.fixture(scope="session")
def api_key():
    """Fixture to provide API key for tests from environment variable."""
    key = os.environ.get("SEVK_TEST_API_KEY")
    if not key:
        pytest.skip("SEVK_TEST_API_KEY environment variable not set, skipping integration tests")
    return key


@pytest.fixture(scope="session")
def base_url():
    """Fixture to provide base URL for tests from environment variable."""
    return os.environ.get("SEVK_TEST_BASE_URL", DEFAULT_BASE_URL)


@pytest.fixture
def sevk(api_key, base_url):
    """Create a Sevk client for testing"""
    from sevk import Sevk, SevkOptions

    options = SevkOptions(base_url=base_url)
    client = Sevk(api_key, options)
    yield client
    client.close()


@pytest.fixture
def sevk_class():
    """Fixture to provide Sevk class for authentication tests"""
    from sevk import Sevk
    return Sevk
