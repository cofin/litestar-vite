from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, MutableMapping, TypeVar

from litestar.template import TemplateEngineProtocol

__all__ = ("InertiaConfig",)


if TYPE_CHECKING:
    from pathlib import Path


T = TypeVar("T", bound=TemplateEngineProtocol)


@dataclass
class InertiaConfig:
    """Configuration for InertiaJS support."""

    root_template: Path
    """Name of the root template to use.

    This must be a path that is found by the Vite Plugin template config
    """
    default_props: MutableMapping[str, Any] = field(default_factory=dict)
    """The additional default props and their types you would like to include on a response."""
    component_opt_key: str = "component"
    """An identifier to use on routes to get the inertia component to render."""
