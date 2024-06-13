from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from click import Context, group, option
from click import Path as ClickPath
from litestar.cli._utils import (
    LitestarEnv,
    LitestarGroup,
)

if TYPE_CHECKING:
    from litestar import Litestar


@group(cls=LitestarGroup, name="assets")
def vite_group() -> None:
    """Manage Vite Tasks."""


@vite_group.command(
    name="init",
    help="Initialize vite for your project.",
)
@option(
    "--root-path",
    type=ClickPath(dir_okay=True, file_okay=False, path_type=Path),
    help="The path for the initial the Vite application.  This is the equivalent to the top-level folder in a normal Vue or React application..",
    default=None,
    required=False,
)
@option(
    "--bundle-path",
    type=ClickPath(dir_okay=True, file_okay=False, path_type=Path),
    help="The path for the built Vite assets.  This is the where the output of `npm run build` will write files.",
    default=None,
    required=False,
)
@option(
    "--resource-path",
    type=ClickPath(dir_okay=True, file_okay=False, path_type=Path),
    help="The path to your Javascript/Typescript source and associated assets.  If this were a standalone Vue or React app, this would point to your `src/` folder.",
    default=None,
    required=False,
)
@option(
    "--public-path",
    type=ClickPath(dir_okay=True, file_okay=False, path_type=Path),
    help="The optional path to your public/static JS assets.  If this were a standalone Vue or React app, this would point to your `public/` folder.",
    default=None,
    required=False,
)
@option("--asset-url", type=str, help="Base url to serve assets from.", default=None, required=False)
@option(
    "--vite-port",
    type=int,
    help="The port to run the vite server against.",
    default=None,
    is_flag=True,
    required=False,
)
@option(
    "--enable-ssr",
    type=bool,
    help="Enable SSR Support.",
    required=False,
    show_default=False,
    is_flag=True,
)
@option("--overwrite", type=bool, help="Overwrite any files in place.", default=False, is_flag=True)
@option("--verbose", type=bool, help="Enable verbose output.", default=False, is_flag=True)
@option(
    "--no-prompt",
    help="Do not prompt for confirmation and use all defaults for initializing the project.",
    type=bool,
    default=False,
    required=False,
    show_default=True,
    is_flag=True,
)
@option(
    "--no-install",
    help="Do not execute the installation commands after generating templates.",
    type=bool,
    default=False,
    required=False,
    show_default=True,
    is_flag=True,
)
def vite_init(
    ctx: Context,
    vite_port: int | None,
    enable_ssr: bool | None,
    asset_url: str | None,
    root_path: Path | None,
    bundle_path: Path | None,
    resource_path: Path | None,
    public_path: Path | None,
    overwrite: bool,
    verbose: bool,
    no_prompt: bool,
    no_install: bool,
) -> None:  # sourcery skip: low-code-quality
    """Run vite build."""
    import os
    import sys
    from importlib.util import find_spec
    from pathlib import Path

    from litestar.cli._utils import (
        console,
    )
    from rich.prompt import Confirm

    from litestar_vite.commands import execute_command, init_vite
    from litestar_vite.plugin import VitePlugin

    if callable(ctx.obj):
        ctx.obj = ctx.obj()
    elif verbose:
        ctx.obj.app.debug = True
    env: LitestarEnv = ctx.obj
    plugin = env.app.plugins.get(VitePlugin)
    config = plugin._config  # pyright: ignore[reportPrivateUsage]

    console.rule("[yellow]Initializing Vite[/]", align="left")
    resource_path = Path(resource_path or config.resource_dir)
    public_path = Path(public_path or config.public_dir)
    bundle_path = Path(bundle_path or config.bundle_dir)
    enable_ssr = enable_ssr or config.ssr_enabled
    asset_url = asset_url or config.asset_url
    vite_port = vite_port or config.port
    hot_file = Path(bundle_path / config.hot_file)
    root_path = Path(root_path or config.root_dir or resource_path.parent)

    if any(output_path.exists() for output_path in (bundle_path, resource_path)) and not any(
        [overwrite, no_prompt],
    ):
        confirm_overwrite = Confirm.ask(
            "Files were found in the paths specified.  Are you sure you wish to overwrite the contents?",
        )
        if not confirm_overwrite:
            console.print("Skipping Vite initialization")
            sys.exit(2)
    for output_path in (bundle_path, resource_path, root_path):
        if output_path.exists():
            console.print(f" * Creating {output_path!s}")
        output_path.mkdir(parents=True, exist_ok=True)

    enable_ssr = (
        True
        if enable_ssr
        else False
        if no_prompt
        else Confirm.ask(
            "Do you intend to use Litestar with any SSR framework?",
        )
    )
    init_vite(
        app=env.app,
        root_path=root_path,
        enable_ssr=enable_ssr,
        vite_port=vite_port,
        asset_url=asset_url,
        resource_path=resource_path,
        public_path=public_path,
        bundle_path=bundle_path,
        hot_file=hot_file,
        litestar_port=env.port or 8000,
    )
    if not no_install:
        if find_spec("nodeenv") is not None and plugin.config.detect_nodeenv:
            """Detect nodeenv installed in the current python env before using a global version"""
            nodeenv_command = (
                str(Path(Path(sys.executable) / "nodeenv"))
                if Path(Path(sys.executable) / "nodeenv").exists()
                else "nodeenv"
            )
            install_dir = os.environ.get("VIRTUAL_ENV", sys.prefix)
            console.rule("[yellow]Starting Nodeenv installation process[/]", align="left")
            console.print(f"Installing Node environment into {install_dir}")
            execute_command(command_to_run=[nodeenv_command, install_dir, "--force", "--quiet"], cwd=root_path)

        console.rule("[yellow]Starting package installation process[/]", align="left")

        execute_command(command_to_run=plugin.config.install_command, cwd=root_path)


@vite_group.command(
    name="install",
    help="Install frontend packages.",
)
@option("--verbose", type=bool, help="Enable verbose output.", default=False, is_flag=True)
def vite_install(app: Litestar, verbose: bool) -> None:
    """Run vite build."""
    import os
    import sys
    from importlib.util import find_spec
    from pathlib import Path

    from litestar.cli._utils import console

    from litestar_vite.commands import execute_command
    from litestar_vite.plugin import VitePlugin

    if verbose:
        app.debug = True
    plugin = app.plugins.get(VitePlugin)

    if find_spec("nodeenv") is not None and plugin.config.detect_nodeenv:
        """Detect nodeenv installed in the current python env before using a global version"""
        nodeenv_command = (
            str(Path(Path(sys.executable) / "nodeenv"))
            if Path(Path(sys.executable) / "nodeenv").exists()
            else "nodeenv"
        )
        install_dir = os.environ.get("VIRTUAL_ENV", sys.prefix)
        console.rule("[yellow]Starting Nodeenv installation process[/]", align="left")
        console.print("Installing Node environment to %s:", install_dir)
        execute_command(command_to_run=[nodeenv_command, install_dir, "--force", "--quiet"], cwd=plugin.config.root_dir)

    console.rule("[yellow]Starting package installation process[/]", align="left")

    execute_command(command_to_run=plugin.config.install_command, cwd=plugin.config.root_dir)


@vite_group.command(
    name="build",
    help="Building frontend assets with Vite.",
)
@option("--verbose", type=bool, help="Enable verbose output.", default=False, is_flag=True)
def vite_build(app: Litestar, verbose: bool) -> None:
    """Run vite build."""
    from litestar.cli._utils import (
        console,
    )

    from litestar_vite.commands import execute_command
    from litestar_vite.plugin import VitePlugin, set_environment

    if verbose:
        app.debug = True
    console.rule("[yellow]Starting Vite build process[/]", align="left")
    plugin = app.plugins.get(VitePlugin)
    if plugin.config.set_environment:
        set_environment(config=plugin.config)
    p = execute_command(command_to_run=plugin.config.build_command, cwd=plugin.config.root_dir)
    if p.returncode == 0:
        console.print("[bold green] Assets built.[/]")
    else:
        console.print("[bold red] There was an error building the assets.[/]")


@vite_group.command(
    name="serve",
    help="Serving frontend assets with Vite.",
)
@option("--verbose", type=bool, help="Enable verbose output.", default=False, is_flag=True)
def vite_serve(app: Litestar, verbose: bool) -> None:
    """Run vite serve."""
    from litestar.cli._utils import (
        console,
    )

    from litestar_vite.commands import execute_command
    from litestar_vite.plugin import VitePlugin, set_environment

    if verbose:
        app.debug = True

    plugin = app.plugins.get(VitePlugin)
    if plugin.config.set_environment:
        set_environment(config=plugin.config)
    if plugin.config.hot_reload:
        console.rule("[yellow]Starting Vite process with HMR Enabled[/]", align="left")
    else:
        console.rule("[yellow]Starting Vite watch and build process[/]", align="left")
    command_to_run = plugin.config.run_command if plugin.config.hot_reload else plugin.config.build_watch_command
    execute_command(command_to_run=command_to_run, cwd=plugin.config.root_dir)
    console.print("[yellow]Vite process stopped.[/]")
