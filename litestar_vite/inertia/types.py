from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypedDict, TypeVar

__all__ = (
    "InertiaHeaderType",
    "PageProps",
)


T = TypeVar("T")


@dataclass
class PageProps(Generic[T]):
    """Inertia Page Props Type."""

    component: str
    url: str
    version: str
    props: T


@dataclass
class InertiaProps(Generic[T]):
    """Inertia Props Type."""

    page: PageProps[T]


class InertiaHeaderType(TypedDict, total=False):
    """Type for hx_headers parameter in get_headers()."""

    enabled: bool | None
    version: str | None
    location: str | None
    partial_data: str | None
    partial_component: str | None
