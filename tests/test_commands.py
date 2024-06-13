from __future__ import annotations

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from litestar_vite.commands import VITE_INIT_TEMPLATES, get_template

pytestmark = pytest.mark.anyio
here = Path(__file__).parent


@pytest.fixture
def vite_template_env() -> Environment:
    return Environment(
        loader=FileSystemLoader([Path(here.parent / "litestar_vite" / "templates")]),
        autoescape=select_autoescape(),
    )


def test_get_template(vite_template_env: Environment) -> None:
    init_templates = {
        template_name: get_template(environment=vite_template_env, name=template_name)
        for template_name in VITE_INIT_TEMPLATES
    }
    assert len(init_templates.keys()) == len(VITE_INIT_TEMPLATES)
