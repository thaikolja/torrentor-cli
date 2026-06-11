from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from torrentor import __version__
from torrentor.ui.theme import CYAN, MAGENTA, ACCENT, DIM, console

LOGO = r"""
╺┳╸┏━┓┏━┓┏━┓┏━╸┏┓╻╺┳╸┏━┓┏━┓
 ┃ ┃ ┃┣┳┛┣┳┛┣╸ ┃┗┫ ┃ ┃ ┃┣┳┛
 ╹ ┗━┛╹┗╸╹┗╸┗━╸╹ ╹ ╹ ┗━┛╹┗╸
""".strip("\n")


def _gradient_logo() -> Text:
    text = Text()
    colors = [CYAN, CYAN, ACCENT, ACCENT, MAGENTA, MAGENTA, ACCENT, CYAN, CYAN]
    for line in LOGO.splitlines():
        chars = list(line)
        segment_len = max(1, len(chars) // len(colors))
        for i, ch in enumerate(chars):
            color_idx = min(i // segment_len, len(colors) - 1)
            text.append(ch, style=f"bold {colors[color_idx]}")
        text.append("\n")
    return text


def show_banner() -> None:
    logo = _gradient_logo()

    tagline = Text()
    tagline.append(f"v{__version__}", style=f"bold {CYAN}")
    tagline.append("  ·  ", style=DIM)
    tagline.append("Fast. Simple. Beautiful.", style=f"italic {DIM}")

    content = Text("\n")
    content.append_text(logo)
    content.append("\n")
    content.append_text(tagline)
    content.append("\n")

    panel = Panel(
        Align.center(content),
        border_style=CYAN,
        padding=(0, 2),
    )
    console.print(panel)
