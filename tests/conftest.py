"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def data_dir(project_root: Path) -> Path:
    """Return the data directory."""
    return project_root / "data"


@pytest.fixture
def schemas_dir(data_dir: Path) -> Path:
    """Return the schemas directory."""
    return data_dir / "schemas" / "bundle" / "schema"


@pytest.fixture
def descriptor_path(schemas_dir: Path) -> Path:
    """Return the path to the descriptor file."""
    return schemas_dir / "descriptor_blueprotobuf.pb"
