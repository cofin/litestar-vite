from __future__ import annotations

from pathlib import Path

import pytest

from litestar_vite.config import ViteConfig

pytestmark = pytest.mark.anyio
here = Path(__file__).parent


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


# Define a fixture for ViteConfig
@pytest.fixture
def vite_config() -> ViteConfig:
    # Mock the ViteConfig with necessary attributes for testing
    return ViteConfig(
        bundle_dir=Path(here / "test_app" / "web" / "public"),
        resource_dir=Path(here / "test_app" / "web" / "resources"),
        template_dir=Path(here / "templates"),
        hot_reload=True,
    )
