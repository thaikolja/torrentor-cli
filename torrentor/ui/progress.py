"""Rich progress bar for active downloads."""

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

from torrentor.ui.theme import CYAN, DIM, SUCCESS, console

# Hint shown below the progress bar during downloads
CONTROLS_HINT = f"  [{DIM}]Ctrl+C to cancel[/]"


# Build a progress bar with spinner, name, bar, percentage, speeds, and peer count
def create_download_progress() -> Progress:
    """Return a Progress instance suited for tracking a single active download."""
    return Progress(
        SpinnerColumn(style=CYAN),
        TextColumn("[bold]{task.description}[/]", justify="left"),
        BarColumn(bar_width=30, complete_style=SUCCESS, finished_style=SUCCESS),
        TaskProgressColumn(),
        TextColumn("[speed.down]{task.fields[down]}[/] [dim]↓[/]"),
        TextColumn("[speed.up]{task.fields[up]}[/] [dim]↑[/]"),
        TextColumn("[peers]{task.fields[peers]} peers[/]"),
        console=console,
        expand=False,
    )


# Show the controls hint below the progress bar
def show_controls_hint() -> None:
    """Display keyboard shortcut hints for the active download."""
    console.print(CONTROLS_HINT)
