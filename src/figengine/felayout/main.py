"""
CLI entrypoint for felayout.
"""

from __future__ import annotations

from importlib.util import find_spec
import json
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group

from . import __author__, __author_email__, __version__, logo as APP_LOGO
from .builder import build_and_save
from .logger import setup_logger
from .spec import dump_template, load_layout_spec, summarize_spec, validate_layout_spec

app = typer.Typer(
    name="felayout",
    help=(
        "[bold cyan]felayout[/bold cyan] - A declarative [bold]FigEngine[/bold] "
        "layout CLI based on JSON/YAML layout specs."
    ),
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
    pretty_exceptions_enable=False,
)

console = Console()


def _state(ctx: typer.Context) -> Dict[str, Any]:
    return ctx.ensure_object(dict)


def _dependency_status(module_name: str) -> str:
    """
    Return a human-readable installation status for a dependency module.
    """

    return "installed" if find_spec(module_name) is not None else "missing"


def _print_logo() -> None:
    typer.echo(APP_LOGO.rstrip())


def _print_info() -> None:
    meta = Table.grid(padding=(0, 2))
    meta.add_column(style="bold cyan", justify="right")
    meta.add_column(style="white")
    meta.add_row("Version", __version__)
    meta.add_row("Author", __author__)
    meta.add_row("Email", __author_email__)

    deps = Table(header_style="bold cyan", box=None, pad_edge=False)
    deps.add_column("Module", style="white")
    deps.add_column("Status", justify="center")

    for module_name in ("figengine", "typer", "rich", "yaml", "PIL", "matplotlib", "numpy"):
        status = _dependency_status(module_name)
        status_style = "green" if status == "installed" else "red"
        deps.add_row(module_name, f"[{status_style}]{status}[/{status_style}]")

    title = Text()
    title.append("felayout", style="bold cyan")
    title.append(" information", style="bold white")

    content = Group(
        Text(APP_LOGO.rstrip(), style="bold"),
        Text(),
        Text("Metadata", style="bold cyan"),
        meta,
        Text(),
        Text("Dependencies", style="bold cyan"),
        deps,
    )

    console.print(Panel.fit(content, title=title, border_style="cyan", padding=(1, 2)))


def _dispatch(ctx: typer.Context, command_name: str, handler, **kwargs: Any) -> None:
    state = _state(ctx)
    logger = state["logger"]
    try:
        logger.info("Running command: %s", command_name)
        handler(logger=logger, **kwargs)
        logger.info("Command finished successfully.")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Command failed: %s", exc)
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc


@app.callback(invoke_without_command=True)
def app_callback(
    ctx: typer.Context,
    info: bool = typer.Option(
        False,
        "--info",
        help="Print logo, version, author, and dependency status, then exit.",
        is_eager=True,
    ),
    log_level: str = typer.Option(
        "WARNING",
        "--log-level",
        help="Override log level (DEBUG/INFO/WARNING/ERROR).",
        show_default=True,
    ),
) -> None:
    if info:
        _print_info()
        raise typer.Exit()

    _state(ctx)["logger"] = setup_logger(level=log_level)


def _init_command(*, output: str, overwrite: bool, logger) -> None:
    path = dump_template(output, overwrite=overwrite)
    logger.info("Template written to %s", path)
    typer.echo(f"Template written: {path}")


@app.command("init", help="Write a starter layout template (.json/.yaml/.yml).")
def init_command(
    ctx: typer.Context,
    output: str = typer.Option("layout.json", "-o", "--output", help="Template output path (.json/.yaml/.yml)."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing template."),
) -> None:
    _dispatch(ctx, "init", _init_command, output=output, overwrite=overwrite)


def _validate_command(*, layout: str, logger) -> None:
    spec = load_layout_spec(layout)
    validate_layout_spec(spec)
    typer.echo(json.dumps(summarize_spec(spec), ensure_ascii=False, indent=2))
    logger.info("Layout validated: %s", layout)


@app.command("validate", help="Validate a layout spec file.")
def validate_command(
    ctx: typer.Context,
    layout: str = typer.Option(..., "--layout", help="Path to layout spec (.json/.yaml/.yml)."),
) -> None:
    _dispatch(ctx, "validate", _validate_command, layout=layout)


def _build_command(*, layout: str, output: Optional[str], overwrite: bool, logger) -> None:
    spec = load_layout_spec(layout)
    validate_layout_spec(spec)
    path = build_and_save(
        spec,
        layout_path=Path(layout).resolve(),
        output_override=output,
        overwrite=overwrite,
    )
    typer.echo(f"Saved: {path}")
    logger.info("Layout rendered to %s", path)


@app.command("build", help="Build a figure from a layout spec.")
def build_command(
    ctx: typer.Context,
    layout: str = typer.Option(..., "--layout", help="Path to layout spec (.json/.yaml/.yml)."),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Override output path."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing output."),
) -> None:
    _dispatch(ctx, "build", _build_command, layout=layout, output=output, overwrite=overwrite)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
