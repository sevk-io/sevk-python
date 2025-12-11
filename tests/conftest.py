"""
Pytest configuration and fixtures for Sevk Python SDK tests
"""

import os
import time
import pytest
import httpx

# Test configuration
BASE_URL = "http://localhost:4000"


def setup_test_environment():
    """
    Setup test environment by registering a new user and creating an API key.
    """
    import random

    # Register a new test user
    test_email = f"sdk-test-{int(time.time())}-{random.randint(1000, 9999)}@test.example.com"
    test_password = "TestPassword123!"

    register_res = httpx.post(
        f"{BASE_URL}/auth/register",
        json={"email": test_email, "password": test_password},
        timeout=30
    )

    if register_res.status_code != 200 and register_res.status_code != 201:
        raise Exception(f"Failed to register: {register_res.status_code} {register_res.text}")

    data = register_res.json()
    token = data.get("token")

    if not token:
        raise Exception("Failed to get authentication token")

    # Create Project
    project_res = httpx.post(
        f"{BASE_URL}/projects",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Project",
            "slug": f"test-project-{int(time.time())}",
            "supportEmail": "support@test.com"
        },
        timeout=30
    )

    if project_res.status_code != 200 and project_res.status_code != 201:
        raise Exception(f"Failed to create project: {project_res.status_code} {project_res.text}")

    project_data = project_res.json()
    project = project_data.get("project", project_data)
    project_id = project.get("id")

    # Create API Key
    api_key_res = httpx.post(
        f"{BASE_URL}/projects/{project_id}/api-keys",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={"title": "Test Key", "fullAccess": True},
        timeout=30
    )

    if api_key_res.status_code != 200 and api_key_res.status_code != 201:
        raise Exception(f"Failed to create API key: {api_key_res.status_code} {api_key_res.text}")

    api_key_data = api_key_res.json()
    api_key = api_key_data.get("apiKey", api_key_data)

    return api_key.get("key")


# Global API key (cached)
_api_key = None


def get_api_key():
    """Get or create API key for tests"""
    global _api_key
    if _api_key is None:
        _api_key = setup_test_environment()
    return _api_key


@pytest.fixture(scope="session")
def api_key():
    """Fixture to provide API key for tests"""
    return get_api_key()


@pytest.fixture(scope="session")
def base_url():
    """Fixture to provide base URL for tests"""
    return BASE_URL


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
