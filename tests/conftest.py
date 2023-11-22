from __future__ import annotations

from pathlib import Path

import pytest

from litestar_vite.config import ViteConfig

here = Path(__file__).parent


# Define a fixture for ViteConfig
@pytest.fixture
def vite_config() -> ViteConfig:
    # Mock the ViteConfig with necessary attributes for testing
    return ViteConfig(
        bundle_dir=Path(here / "test_app" / "web" / "public"),
        resource_dir=Path(here / "test_app" / "web" / "resources"),
        assets_dir=Path(here / "test_app" / "web" / "resources" / "assets"),
        templates_dir=Path(here / "test_app" / "web" / "templates"),
        hot_reload=True,
    )
