from __future__ import annotations

from pathlib import Path

from litestar import Litestar

from litestar_vite import ViteConfig, VitePlugin

here = Path(__file__).parent

vite = VitePlugin(
    config=ViteConfig(
        bundle_dir=Path(here / "public"),
        resource_dir=Path(here / "resources"),
        assets_dir=Path(here / "resources" / "assets"),
        templates_dir=Path(here / "templates"),
        hot_reload=True,
    ),
)
app = Litestar(plugins=[vite])
