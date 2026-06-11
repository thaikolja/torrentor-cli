import time

from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    SpinnerColumn,
    TaskProgressColumn,
)

from torrentor.ui.theme import CYAN, SUCCESS, console


def create_download_progress() -> Progress:
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


def create_progress() -> Progress:
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


MOCK_TORRENTS = [
    {
        "name": "Ubuntu 24.04 LTS",
        "total": 4_800_000,
        "start": 0.72,
        "speed": 0.045,
        "down": "2.4 MB/s",
        "up": "312 KB/s",
        "peers": 12,
    },
    {
        "name": "Arch Linux 2024.06",
        "total": 900_000,
        "start": 0.38,
        "speed": 0.065,
        "down": "1.8 MB/s",
        "up": "156 KB/s",
        "peers": 8,
    },
    {
        "name": "Debian 12.5 netinst",
        "total": 650_000,
        "start": 0.10,
        "speed": 0.035,
        "down": "3.1 MB/s",
        "up": "89 KB/s",
        "peers": 21,
    },
]


def show_mock_progress(duration: float = 4.0) -> None:
    progress = create_progress()

    tasks = []
    with progress:
        for t in MOCK_TORRENTS:
            task_id = progress.add_task(
                t["name"],
                total=t["total"],
                completed=int(t["total"] * t["start"]),
                down=t["down"],
                up=t["up"],
                peers=t["peers"],
            )
            tasks.append((task_id, t))

        steps = int(duration / 0.05)
        for _ in range(steps):
            for task_id, t in tasks:
                advance = int(t["total"] * t["speed"] * 0.05)
                progress.advance(task_id, advance)
            time.sleep(0.05)

    console.print()
