from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.plugins import InitPluginProtocol

from litestar_vite.inertia.request import InertiaRequest

if TYPE_CHECKING:
    from litestar.config.app import AppConfig

    from litestar_vite.inertia.config import InertiaConfig


class InertiaPlugin(InitPluginProtocol):
    """Inertia plugin."""

    __slots__ = ("_config",)

    def __init__(self, config: InertiaConfig) -> None:
        """Initialize ``Inertia``.

        Args:
            config: configure and start Vite.
        """
        self._config = config

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Configure application for use with Vite.

        Args:
            app_config: The :class:`AppConfig <.config.app.AppConfig>` instance.
        """
        app_config.request_class = InertiaRequest
        # app_config.response_class = InertiaResponse  # noqa: ERA001
        return app_config
