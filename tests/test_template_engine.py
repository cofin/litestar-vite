from __future__ import annotations

from typing import Any

import pytest
from jinja2 import Environment, FileSystemLoader

from litestar_vite.config import ViteConfig
from litestar_vite.template_engine import ViteTemplateEngine


# Define a fixture for Jinja Environment
@pytest.fixture
def jinja_env(vite_config: ViteConfig) -> Environment:
    # Mock the Jinja Environment with necessary attributes for testing
    loader = FileSystemLoader(searchpath=vite_config.templates_dir)
    return Environment(loader=loader, autoescape=True)


# Define a fixture for ViteTemplateEngine
@pytest.fixture
def vite_template_engine(vite_config: ViteConfig, jinja_env: Environment) -> ViteTemplateEngine:
    # Instantiate the ViteTemplateEngine with mock objects
    return ViteTemplateEngine.from_environment(config=vite_config, jinja_environment=jinja_env)


# Happy path tests for get_hmr_client
@pytest.mark.parametrize(
    "expected_output, test_id",
    [
        # Test with a context that should return a non-empty script tag
        ("<script>...</script>", "hmr_non_empty"),
        # Test with a context that should return an empty string
        ("", "hmr_empty"),
    ],
)
def test_get_hmr_client(
    vite_template_engine: ViteTemplateEngine,
    expected_output: str,
    test_id: str,
) -> None:
    # Act
    result = vite_template_engine.get_hmr_client()

    # Assert
    assert result == expected_output, f"Failed test ID: {test_id}"


# Happy path tests for get_asset_tag
@pytest.mark.parametrize(
    "path, scripts_attrs, expected_output, test_id",
    [
        # Test with realistic values for a single asset path
        ("asset.js", None, "<script src='asset.js'></script>", "asset_single"),
        # Test with realistic values for a list of asset paths
        (
            ["asset.js", "style.css"],
            None,
            "<script src='asset.js'></script><link rel='stylesheet' href='style.css'>",
            "asset_multiple",
        ),
        # Test with additional script attributes
        ("asset.js", {"async": "true"}, "<script async='true' src='asset.js'></script>", "asset_attrs"),
    ],
)
def test_get_asset_tag(
    vite_template_engine: ViteTemplateEngine,
    path: str | list[str],
    scripts_attrs: dict[str, Any] | None,
    expected_output: str,
    test_id: str,
) -> None:
    # Act
    result = vite_template_engine.get_asset_tag(path=path, scripts_attrs=scripts_attrs)

    # Assert
    assert result == expected_output, f"Failed test ID: {test_id}"


# Edge case tests for get_asset_tag
# Add more edge cases as needed
@pytest.mark.parametrize(
    "path, scripts_attrs, expected_output, test_id",
    [
        # Test with an empty path
        ("", None, "", "asset_empty_path"),
        # Test with None as path
        (None, None, "", "asset_none_path"),
        # Test with empty scripts_attrs
        ("asset.js", {}, "<script src='asset.js'></script>", "asset_empty_attrs"),
    ],
)
def test_get_asset_tag_edge_cases(
    vite_template_engine: ViteTemplateEngine,
    path: str | list[str],
    scripts_attrs: dict[str, Any] | None,
    expected_output: str,
    test_id: str,
) -> None:
    # Act
    result = vite_template_engine.get_asset_tag(path=path, scripts_attrs=scripts_attrs)

    # Assert
    assert result == expected_output, f"Failed test ID: {test_id}"


# Error case tests for get_asset_tag
# Add more error cases as needed
@pytest.mark.parametrize(
    "path, scripts_attrs, exception, test_id",
    [
        # Test with invalid path type
        (123, None, TypeError, "asset_invalid_path_type"),
        # Test with invalid scripts_attrs type
        ("asset.js", "invalid", TypeError, "asset_invalid_attrs_type"),
    ],
)
def test_get_asset_tag_error_cases(
    vite_template_engine: ViteTemplateEngine,
    path: str | list[str],
    scripts_attrs: dict[str, Any] | None,
    exception: Any,
    test_id: str,
) -> None:
    # Act / Assert
    with pytest.raises(exception) as exc_info:
        vite_template_engine.get_asset_tag(path, scripts_attrs)
    assert exc_info.type is exception, f"Failed test ID: {test_id}"
