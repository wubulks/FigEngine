"""
Read and print image metadata.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ._utils import require_figengine

console = Console()


def execute(
    *,
    input_path: str,
    config,
    logger,
) -> None:
    fe = require_figengine()

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path)

    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold cyan", justify="right")
    table.add_column(style="white")
    table.add_row("Path", input_path)
    table.add_row("Size", str(list(img.size)))
    table.add_row("Size (pixel)", str(list(img.get_size("pixel"))))
    table.add_row("Size (inch)", str(list(img.get_size("inch"))))
    table.add_row("Size (cm)", str(list(img.get_size("cm"))))
    table.add_row("Size (mm)", str(list(img.get_size("mm"))))
    table.add_row("DPI", str(img.dpi))
    table.add_row("Label", str(getattr(img, "label", None)))

    console.print(Panel.fit(table, title="Image Info", border_style="cyan"))
