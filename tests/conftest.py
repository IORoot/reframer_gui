"""
Pytest configuration and common fixtures for Reframer GUI backend tests.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the python directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp(prefix="reframer_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="session")
def sample_video_path():
    """Provide path to a sample video for testing."""
    # Check if the landscape video exists in the project root
    video_path = Path(__file__).parent.parent / "landscape_10secs.mp4"
    if video_path.exists():
        return str(video_path)
    
    # If not found, return None and tests should be skipped
    return None

@pytest.fixture(scope="session")
def output_dir():
    """Provide a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp(prefix="reframer_output_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="function")
def debug_dir():
    """Provide a temporary directory for debug outputs."""
    temp_dir = tempfile.mkdtemp(prefix="reframer_debug_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="session")
def models_dir():
    """Provide the models directory path."""
    return str(Path(__file__).parent.parent / "models")

@pytest.fixture(scope="session")
def python_dir():
    """Provide the python backend directory path."""
    return str(Path(__file__).parent.parent / "python")

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "requires_video: marks tests that require a sample video file"
    ) 