from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from litestar_vite.inertia.types import InertiaHeaderType


class InertiaHeaders(str, Enum):
    """Enum for Inertia Headers"""

    ENABLED = "X-Inertia"
    VERSION = "X-Inertia-Version"
    PARTIAL_DATA = "X-Inertia-Partial-Data"
    PARTIAL_COMPONENT = "X-Inertia-Partial-Component"
    LOCATION = "X-Inertia-Location"


def get_enabled_header(enabled: bool = True) -> dict[str, Any]:
    """True if inertia is enabled."""

    return {InertiaHeaders.ENABLED.value: enabled}


def get_version_header(version: str) -> dict[str, Any]:
    """Return headers for change swap method response."""
    return {InertiaHeaders.VERSION.value: version}


def get_partial_data_header(partial: str) -> dict[str, Any]:
    """Return headers for a partial data response."""
    return {InertiaHeaders.PARTIAL_DATA.value: partial}


def get_partial_component_header(partial: str) -> dict[str, Any]:
    """Return headers for a partial data response."""
    return {InertiaHeaders.PARTIAL_COMPONENT.value: partial}


def get_headers(inertia_headers: InertiaHeaderType) -> dict[str, Any]:
    """Return headers for Inertia responses."""
    if not inertia_headers:
        msg = "Value for inertia_headers cannot be None."
        raise ValueError(msg)
    inertia_headers_dict: dict[str, Callable] = {
        "enabled": get_enabled_header,
        "partial_data": get_partial_data_header,
        "partial_component": get_partial_component_header,
        "version": get_version_header,
    }

    header: dict[str, Any] = {}
    response: dict[str, Any]
    key: str
    value: Any

    for key, value in inertia_headers.items():
        if value is not None:
            response = inertia_headers_dict[key](value)
            header.update(response)
    return header
