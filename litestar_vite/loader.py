from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import urljoin

if TYPE_CHECKING:
    from litestar_vite.config import ViteConfig


class ViteAssetLoader:
    """Vite  manifest loader.

    Please see: https://vitejs.dev/guide/backend-integration.html
    """

    _instance: ClassVar[ViteAssetLoader | None] = None

    def __init__(self, config: ViteConfig) -> None:
        self._config = config
        self._manifest: dict[str, Any] = {}
        self._vite_base_path: str | None = None

    @classmethod
    def initialize_loader(cls, config: ViteConfig) -> ViteAssetLoader:
        """Singleton manifest loader."""
        if cls._instance is None:
            cls._instance = cls(config=config)
            cls._instance.parse_manifest()
        return cls._instance

    def parse_manifest(self) -> None:
        """Read and parse the Vite manifest file.

        Example manifest:
        ```json
            {
                "main.js": {
                    "file": "assets/main.4889e940.js",
                    "src": "main.js",
                    "isEntry": true,
                    "dynamicImports": ["views/foo.js"],
                    "css": ["assets/main.b82dbe22.css"],
                    "assets": ["assets/asset.0ab0f9cd.png"]
                },
                "views/foo.js": {
                    "file": "assets/foo.869aea0d.js",
                    "src": "views/foo.js",
                    "isDynamicEntry": true,
                    "imports": ["_shared.83069a53.js"]
                },
                "_shared.83069a53.js": {
                    "file": "assets/shared.83069a53.js"
                }
                }
        ```

        Raises:
            RuntimeError: if cannot load the file or JSON in file is malformed.
        """
        if self._config.hot_reload and self._config.dev_mode:
            hot_file_path = Path(
                f"{self._config.bundle_dir}/{self._config.hot_file}",
            )
            if hot_file_path.exists():
                with hot_file_path.open() as hot_file:
                    self._vite_base_path = hot_file.read()

        else:
            manifest_path = Path(f"{self._config.bundle_dir}/{self._config.manifest_name}")
            try:
                if manifest_path.exists():
                    with manifest_path.open() as manifest_file:
                        manifest_content = manifest_file.read()
                        self._manifest = json.loads(manifest_content)
                else:
                    self._manifest = {}
            except Exception as exc:
                msg = "There was an issue reading the Vite manifest file at  %s. Did you forget to build your assets?"
                raise RuntimeError(
                    msg,
                    manifest_path,
                ) from exc

    def generate_ws_client_tags(self) -> str:
        """Generate the script tag for the Vite WS client for HMR.

        Only used when hot module reloading is enabled, in production this method returns an empty string.

        Returns:
            str: The script tag or an empty string.
        """
        if self._config.hot_reload and self._config.dev_mode:
            return self._script_tag(
                self._vite_server_url("@vite/client"),
                {"type": "module"},
            )
        return ""

    def generate_react_hmr_tags(self) -> str:
        """Generate the script tag for the Vite WS client for HMR.

        Only used when hot module reloading is enabled, in production this method returns an empty string.

        Returns:
            str: The script tag or an empty string.
        """
        if self._config.is_react and self._config.hot_reload and self._config.dev_mode:
            return f"""
                <script type="module">
                import RefreshRuntime from '{self._vite_server_url()}@react-refresh'
                RefreshRuntime.injectIntoGlobalHook(window)
                window.$RefreshReg$ = () => {{}}
                window.$RefreshSig$ = () => (type) => type
                window.__vite_plugin_react_preamble_installed__=true
                </script>
                """
        return ""

    def generate_asset_tags(self, path: str | list[str], scripts_attrs: dict[str, str] | None = None) -> str:
        """Generate all assets include tags for the file in argument.

        Returns:
            str: All tags to import this asset in your HTML page.
        """
        if isinstance(path, str):
            path = [path]
        if self._config.hot_reload and self._config.dev_mode:
            return "".join(
                [
                    self._script_tag(
                        self._vite_server_url(p),
                        {"type": "module", "async": "", "defer": ""},
                    )
                    for p in path
                ],
            )

        if any(p for p in path if p not in self._manifest):
            msg = "Cannot find %s in Vite manifest at %s.  Did you forget to build your assets?"
            raise RuntimeError(
                msg,
                path,
                Path(f"{self._config.bundle_dir}/{self._config.manifest_name}"),
            )

        tags: list[str] = []
        manifest_entry: dict[str, Any] = {}
        manifest_entry.update({p: self._manifest[p] for p in path})
        if not scripts_attrs:
            scripts_attrs = {"type": "module", "async": "", "defer": ""}

        # Add dependent CSS
        if "css" in manifest_entry:
            tags.extend(
                self._style_tag(urljoin(self._config.asset_url, css_path)) for css_path in manifest_entry.get("css", {})
            )
        # Add dependent "vendor"
        if "imports" in manifest_entry:
            tags.extend(
                self.generate_asset_tags(vendor_path, scripts_attrs=scripts_attrs)
                for vendor_path in manifest_entry.get("imports", {})
            )
        # Add the script by itself
        tags.append(
            self._script_tag(
                urljoin(self._config.asset_url, manifest_entry["file"]),
                attrs=scripts_attrs,
            ),
        )

        return "".join(tags)

    def _vite_server_url(self, path: str | None = None) -> str:
        """Generate an URL to and asset served by the Vite development server.

        Keyword Arguments:
            path: Path to the asset. (default: {None})

        Returns:
            str: Full URL to the asset.
        """
        base_path = self._vite_base_path or f"{self._config.protocol}://{self._config.host}:{self._config.port}"
        return urljoin(
            base_path,
            urljoin(self._config.asset_url, path if path is not None else ""),
        )

    def _script_tag(self, src: str, attrs: dict[str, str] | None = None) -> str:
        """Generate an HTML script tag."""
        if attrs is None:
            attrs = {}
        attrs_str = " ".join([f'{key}="{value}"' for key, value in attrs.items()])
        return f'<script {attrs_str} src="{src}"></script>'

    def _style_tag(self, href: str) -> str:
        """Generate and HTML <link> stylesheet tag for CSS.

        Args:
            href: CSS file URL.

        Returns:
            str: CSS link tag.
        """
        return f'<link rel="stylesheet" href="{href}" />'
