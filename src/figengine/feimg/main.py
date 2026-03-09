"""
CLI entrypoint for feimg.
"""

from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group

from . import __author__, __author_email__, __version__, logo as APP_LOGO
from .commands import (
    border,
    clip,
    crop,
    info,
    labeled,
    line,
    marker,
    new,
    oval,
    overlay,
    pad,
    rect,
    resize,
    rotate,
    text,
    ticks,
)
from .config import apply_cli_overrides, load_config
from .logger import setup_logger

app = typer.Typer(
    name="feimg",
    help=(
        "[bold cyan]feimg[/bold cyan] - A [bold]FigEngine[/bold] based image CLI.\n\n"
        "Use subcommands to create, inspect, annotate, and transform images."
    ),
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
    pretty_exceptions_enable=False,
)

console = Console()


def _state(ctx: typer.Context) -> Dict[str, Any]:
    """
    Get shared runtime state from Typer context.
    """

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

    for module_name in ("figengine", "typer", "rich", "PIL", "matplotlib", "numpy"):
        status = _dependency_status(module_name)
        status_style = "green" if status == "installed" else "red"
        deps.add_row(module_name, f"[{status_style}]{status}[/{status_style}]")

    title = Text()
    title.append("feimg", style="bold cyan")
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


def _dispatch(
    ctx: typer.Context,
    command_name: str,
    handler,
    **kwargs: Any,
) -> None:
    """
    Invoke command handler with shared config/logger and unified error handling.
    """

    state = _state(ctx)
    config = state["config"]
    logger = state["logger"]

    try:
        logger.info("Running command: %s", command_name)
        handler(config=config, logger=logger, **kwargs)
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
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        help="Path to JSON config file.",
        show_default=False,
    ),
    log_level: Optional[str] = typer.Option(
        None,
        "--log-level",
        help="Override log level (DEBUG/INFO/WARNING/ERROR).",
        show_default=False,
    ),
) -> None:
    """
    Initialize global config and logger before executing any subcommand.
    """

    if info:
        _print_info()
        raise typer.Exit()

    loaded = load_config(str(config_path) if config_path else None)
    merged = apply_cli_overrides(
        config=loaded,
        log_level=log_level,
    )
    logger = setup_logger(level=merged.log_level)

    state = _state(ctx)
    state["config"] = merged
    state["logger"] = logger


@app.command("new", help="Create a blank image with a solid background color.")
def new_command(
    ctx: typer.Context,
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    size: Optional[Tuple[float, float]] = typer.Option(None, "--size", help="Image size: W H."),
    width: Optional[float] = typer.Option(None, "--width", help="Image width."),
    height: Optional[float] = typer.Option(None, "--height", help="Image height."),
    facecolor: str = typer.Option("#FFFFFF", "--facecolor", help="Background color."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/inch/cm/mm."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Output image DPI."),
    label: Optional[str] = typer.Option(None, "--label", help="Image label."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "new",
        new.execute,
        output=output,
        size=size,
        width=width,
        height=height,
        facecolor=facecolor,
        unit=unit,
        dpi=dpi,
        label=label,
        overwrite=overwrite,
    )


@app.command("info", help="Print image size, DPI, and label metadata.")
def info_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
) -> None:
    _dispatch(
        ctx,
        "info",
        info.execute,
        input_path=input_path,
    )


@app.command("ticks", help="Add edge ticks or a grid overlay to an image.")
def ticks_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    step: float = typer.Option(..., "--step", help="Tick step size."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/ratio/inch/cm/mm."),
    color: str = typer.Option("black", "--color", help="Tick and text color."),
    font: str = typer.Option("sans-serif", "--font", help="Font name."),
    fontsize: float = typer.Option(6.0, "--fontsize", help="Tick label font size."),
    show_grid: bool = typer.Option(True, "--show-grid/--edge-only", help="Show inner grid."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "ticks",
        ticks.execute,
        input_path=input_path,
        output=output,
        step=step,
        unit=unit,
        color=color,
        font=font,
        fontsize=fontsize,
        show_grid=show_grid,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("text", help="Add text annotations to an image.")
def text_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    text_value: str = typer.Option(..., "--text", help="Text content."),
    x: Optional[float] = typer.Option(None, "--x", help="Text anchor X."),
    y: Optional[float] = typer.Option(None, "--y", help="Text anchor Y."),
    loc: str = typer.Option("top_left", "--loc", help="Semantic location."),
    anchor: Optional[str] = typer.Option(None, "--anchor", help="Text anchor."),
    offset: Optional[str] = typer.Option(None, "--offset", help="Offset as 'v' or 'x,y'."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/ratio/inch/cm/mm."),
    font: str = typer.Option("sans-serif", "--font", help="Font name."),
    fontsize: float = typer.Option(18.0, "--fontsize", help="Font size."),
    fontweight: str = typer.Option("normal", "--fontweight", help="Font weight."),
    rotation: float = typer.Option(0.0, "--rotation", help="Rotation angle."),
    color: str = typer.Option("black", "--color", help="Text color."),
    box_style: Optional[str] = typer.Option(None, "--box-style", help="Matplotlib bbox JSON."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "text",
        text.execute,
        input_path=input_path,
        output=output,
        text=text_value,
        x=x,
        y=y,
        loc=loc,
        anchor=anchor,
        offset=offset,
        unit=unit,
        font=font,
        fontsize=fontsize,
        fontweight=fontweight,
        rotation=rotation,
        color=color,
        box_style=box_style,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("labeled", help="Add a formatted subplot-style label to an image.")
def labeled_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    label: Optional[str] = typer.Option(None, "--label", help="Label text override."),
    loc: str = typer.Option("top_left", "--loc", help="Label location."),
    offset: Optional[str] = typer.Option(None, "--offset", help="Offset as 'v' or 'x,y'."),
    format_str: str = typer.Option("{}", "--format-str", help="Label format string."),
    case: Optional[str] = typer.Option(None, "--case", help="upper/lower."),
    fontsize: float = typer.Option(24.0, "--fontsize", help="Font size."),
    fontweight: str = typer.Option("bold", "--fontweight", help="Font weight."),
    color: str = typer.Option("black", "--color", help="Text color."),
    font: str = typer.Option("sans-serif", "--font", help="Font name."),
    box_style: Optional[str] = typer.Option(None, "--box-style", help="Matplotlib bbox JSON."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "labeled",
        labeled.execute,
        input_path=input_path,
        output=output,
        label=label,
        loc=loc,
        offset=offset,
        format_str=format_str,
        case=case,
        fontsize=fontsize,
        fontweight=fontweight,
        color=color,
        font=font,
        box_style=box_style,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("line", help="Draw a line or arrow on an image.")
def line_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    start: Tuple[float, float] = typer.Option(..., "--start", help="Start point: X Y."),
    end: Tuple[float, float] = typer.Option(..., "--end", help="End point: X Y."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/ratio/inch/cm/mm."),
    color: str = typer.Option("black", "--color", help="Line color."),
    width: float = typer.Option(0.01, "--width", help="Line width."),
    arrow: Optional[str] = typer.Option(None, "--arrow", help="start/end/both."),
    arrow_size: Optional[float] = typer.Option(None, "--arrow-size", help="Arrow size."),
    arrow_style: Optional[str] = typer.Option(None, "--arrow-style", help="Arrow style: triangle, open, bar, diamond, circle."),
    arrow_angle: Optional[float] = typer.Option(None, "--arrow-angle", help="Arrow angle."),
    arrow_shorten: Optional[float] = typer.Option(None, "--arrow-shorten", help="Line shorten."),
    arrow_fill: Optional[bool] = typer.Option(None, "--arrow-fill/--no-arrow-fill", help="Fill arrow."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "line",
        line.execute,
        input_path=input_path,
        output=output,
        start=start,
        end=end,
        unit=unit,
        color=color,
        width=width,
        arrow=arrow,
        arrow_size=arrow_size,
        arrow_style=arrow_style,
        arrow_angle=arrow_angle,
        arrow_shorten=arrow_shorten,
        arrow_fill=arrow_fill,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("rect", help="Draw a rectangle using corner or center-size mode.")
def rect_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    start: Optional[Tuple[float, float]] = typer.Option(None, "--start", help="Start point: X Y."),
    end: Optional[Tuple[float, float]] = typer.Option(None, "--end", help="End point: X Y."),
    center: Optional[Tuple[float, float]] = typer.Option(None, "--center", help="Center point: X Y."),
    size: Optional[Tuple[float, float]] = typer.Option(None, "--size", help="Rectangle size: W H."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/ratio/inch/cm/mm."),
    linewidth: float = typer.Option(0.01, "--linewidth", help="Line width."),
    color: Optional[str] = typer.Option(None, "--color", help="Base color."),
    edgecolor: Optional[str] = typer.Option(None, "--edgecolor", help="Edge color."),
    facecolor: Optional[str] = typer.Option(None, "--facecolor", help="Fill color."),
    fill: bool = typer.Option(False, "--fill/--no-fill", help="Fill the rectangle."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "rect",
        rect.execute,
        input_path=input_path,
        output=output,
        start=start,
        end=end,
        center=center,
        size=size,
        unit=unit,
        linewidth=linewidth,
        color=color,
        edgecolor=edgecolor,
        facecolor=facecolor,
        fill=fill,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("oval", help="Draw an oval or circle using bounding box or center-radius mode.")
def oval_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    start: Optional[Tuple[float, float]] = typer.Option(None, "--start", help="Start point: X Y."),
    end: Optional[Tuple[float, float]] = typer.Option(None, "--end", help="End point: X Y."),
    center: Optional[Tuple[float, float]] = typer.Option(None, "--center", help="Center point: X Y."),
    radius: Optional[float] = typer.Option(None, "--radius", help="Minor-axis radius."),
    axis_ratio: Optional[float] = typer.Option(None, "--axis-ratio", help="Major/minor ratio."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/ratio/inch/cm/mm."),
    linewidth: float = typer.Option(0.01, "--linewidth", help="Line width."),
    color: Optional[str] = typer.Option(None, "--color", help="Base color."),
    edgecolor: Optional[str] = typer.Option(None, "--edgecolor", help="Edge color."),
    facecolor: Optional[str] = typer.Option(None, "--facecolor", help="Fill color."),
    fill: bool = typer.Option(True, "--fill/--no-fill", help="Fill the oval."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "oval",
        oval.execute,
        input_path=input_path,
        output=output,
        start=start,
        end=end,
        center=center,
        radius=radius,
        axis_ratio=axis_ratio,
        unit=unit,
        linewidth=linewidth,
        color=color,
        edgecolor=edgecolor,
        facecolor=facecolor,
        fill=fill,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("marker", help="Add a marker symbol to an image.")
def marker_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    x: float = typer.Option(..., "--x", help="Marker X."),
    y: float = typer.Option(..., "--y", help="Marker Y."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/ratio/inch/cm/mm."),
    style: str = typer.Option("circle", "--style", help="Marker style: circle, square, triangle, diamond, cross, triangle_up, triangle_down, pentagon, hexagon, star, target"),
    size: float = typer.Option(0.02, "--size", help="Marker size."),
    color: str = typer.Option("red", "--color", help="Fill color."),
    outline: Optional[str] = typer.Option(None, "--outline", help="Outline color."),
    width: float = typer.Option(1.0, "--width", help="Outline/line width."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "marker",
        marker.execute,
        input_path=input_path,
        output=output,
        x=x,
        y=y,
        unit=unit,
        style=style,
        size=size,
        color=color,
        outline=outline,
        width=width,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("resize", help="Resize image dimensions with optional [bold]width/height/scale[/bold].")
def resize_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    width: Optional[float] = typer.Option(None, "--width", help="Target width."),
    height: Optional[float] = typer.Option(None, "--height", help="Target height."),
    scale: Optional[str] = typer.Option(None, "--scale", help="Scale factor like '0.5' or '0.5,0.8'."),
    ref_image: Optional[str] = typer.Option(None, "--ref-image", help="Reference image path."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/inch/cm/mm."),
    resample: Optional[str] = typer.Option(None, "--resample", help="Resample method."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "resize",
        resize.execute,
        input_path=input_path,
        output=output,
        width=width,
        height=height,
        scale=scale,
        ref_image=ref_image,
        unit=unit,
        resample=resample,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("crop", help="Crop image by [bold]--box[/bold] or trimming sides.")
def crop_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    box: Optional[Tuple[float, float, float, float]] = typer.Option(
        None,
        "--box",
        help="Box coordinates: LEFT TOP RIGHT BOTTOM.",
    ),
    left: float = typer.Option(0.0, "--left", help="Trim from left."),
    top: float = typer.Option(0.0, "--top", help="Trim from top."),
    right: float = typer.Option(0.0, "--right", help="Trim from right."),
    bottom: float = typer.Option(0.0, "--bottom", help="Trim from bottom."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/inch/cm/mm/ratio."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "crop",
        crop.execute,
        input_path=input_path,
        output=output,
        box=box,
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        unit=unit,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("clip", help="Alias of [bold]crop[/bold].")
def clip_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    box: Optional[Tuple[float, float, float, float]] = typer.Option(
        None,
        "--box",
        help="Box coordinates: LEFT TOP RIGHT BOTTOM.",
    ),
    left: float = typer.Option(0.0, "--left", help="Trim from left."),
    top: float = typer.Option(0.0, "--top", help="Trim from top."),
    right: float = typer.Option(0.0, "--right", help="Trim from right."),
    bottom: float = typer.Option(0.0, "--bottom", help="Trim from bottom."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/inch/cm/mm/ratio."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "clip",
        clip.execute,
        input_path=input_path,
        output=output,
        box=box,
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        unit=unit,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("rotate", help="Rotate image by angle with optional canvas expand.")
def rotate_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    angle: float = typer.Option(..., "--angle", help="Rotation angle in degrees."),
    expand: bool = typer.Option(False, "--expand", help="Expand canvas."),
    bg_color: Optional[str] = typer.Option(None, "--bg-color", help="Background color."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "rotate",
        rotate.execute,
        input_path=input_path,
        output=output,
        angle=angle,
        expand=expand,
        bg_color=bg_color,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("pad", help="Pad image to target width and height.")
def pad_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    target_size: Optional[Tuple[float, float]] = typer.Option(None, "--target-size", help="Target size: W H."),
    target_width: Optional[float] = typer.Option(None, "--target-width", help="Target width."),
    target_height: Optional[float] = typer.Option(None, "--target-height", help="Target height."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/inch/cm/mm."),
    loc: str = typer.Option("center", "--loc", help="Anchor location."),
    axis: Optional[str] = typer.Option(None, "--axis", help="Optional axis constraint."),
    bg_color: Optional[str] = typer.Option(None, "--bg-color", help="Background color."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "pad",
        pad.execute,
        input_path=input_path,
        output=output,
        target_size=target_size,
        target_width=target_width,
        target_height=target_height,
        unit=unit,
        loc=loc,
        axis=axis,
        bg_color=bg_color,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("border", help="Add border (padding only) around image.")
def border_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Input image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    thickness: str = typer.Option(..., "--thickness", help="Border thickness: v or left,right,top,bottom."),
    left: Optional[float] = typer.Option(None, "--left", help="Left border override."),
    top: Optional[float] = typer.Option(None, "--top", help="Top border override."),
    right: Optional[float] = typer.Option(None, "--right", help="Right border override."),
    bottom: Optional[float] = typer.Option(None, "--bottom", help="Bottom border override."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/inch/cm/mm."),
    color: str = typer.Option("#000000", "--color", help="Border color."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "border",
        border.execute,
        input_path=input_path,
        output=output,
        thickness=thickness,
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        unit=unit,
        color=color,
        dpi=dpi,
        overwrite=overwrite,
    )


@app.command("overlay", help="Overlay one image on top of another.")
def overlay_command(
    ctx: typer.Context,
    input_path: str = typer.Option(..., "-i", "--input", help="Base image path."),
    other: str = typer.Option(..., "--other", "--overlay", help="Overlay image path."),
    output: str = typer.Option(..., "-o", "--output", help="Output image path."),
    x: float = typer.Option(0.0, "--x", help="Overlay X position."),
    y: float = typer.Option(0.0, "--y", help="Overlay Y position."),
    anchor: str = typer.Option("center", "--anchor", help="Overlay anchor."),
    unit: Optional[str] = typer.Option(None, "--unit", help="pixel/inch/cm/mm."),
    scale: float = typer.Option(1.0, "--scale", help="Overlay scale."),
    expand: bool = typer.Option(False, "--expand", help="Expand base canvas."),
    bg_color: Optional[str] = typer.Option(None, "--bg-color", help="Background color."),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Input image DPI."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file."),
) -> None:
    _dispatch(
        ctx,
        "overlay",
        overlay.execute,
        input_path=input_path,
        other=other,
        output=output,
        x=x,
        y=y,
        anchor=anchor,
        unit=unit,
        scale=scale,
        expand=expand,
        bg_color=bg_color,
        dpi=dpi,
        overwrite=overwrite,
    )


def main(argv: Optional[List[str]] = None) -> None:
    """
    Script entrypoint.
    """

    if argv is None:
        app()
    else:
        app(args=argv)


if __name__ == "__main__":
    main()
