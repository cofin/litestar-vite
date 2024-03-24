from __future__ import annotations

from typing import Any, MutableMapping

from litestar import Response
from litestar.response import Template

from litestar_vite.inertia._utils import get_headers
from litestar_vite.inertia.types import InertiaHeaderType


class InertiaJSON(Response):
    """Inertia JSON Response"""

    def __init__(self, props: MutableMapping[str, Any] | None = None, **kwargs: Any) -> None:
        """Set Status code to 200 and set headers."""
        super().__init__(**kwargs)
        self._props = props
        self.headers.update(
            get_headers(InertiaHeaderType(enabled=True)),
        )


class InertiaTemplate(Template):
    """Inertia template wrapper"""

    def __init__(
        self,
        props: MutableMapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Create InertiaTemplate response.

        Args:
            props: Dictionary or Prop type to serialize to JSON
            **kwargs: Additional arguments to pass to ``Template``.
        """
        super().__init__(**kwargs)
        self._props = props
        self.headers.update(
            get_headers(InertiaHeaderType(enabled=True)),
        )


class InertiaResponse(Response):
    """Inertia Response"""

    def __init__(self, props: MutableMapping[str, Any] | None = None, **kwargs: Any) -> None:
        """Set Status code to 200 and set headers."""
        super().__init__(**kwargs)
        self._props = props
        self.headers.update(
            get_headers(InertiaHeaderType(enabled=True)),
        )
