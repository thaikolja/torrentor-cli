"""Renders the bold TORRENTOR logo inside a Rich panel."""

from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from torrentor import __author__, __version__
from torrentor.ui.theme import ACCENT, CYAN, DIM, MAGENTA, console

# The ASCII logo — heavy Unicode box-drawing glyphs
LOGO = r"""
╺┳╸┏━┓┏━┓┏━┓┏━╸┏┓╻╺┳╸┏━┓┏━┓
 ┃ ┃ ┃┣┳┛┣┳┛┣╸ ┃┗┫ ┃ ┃ ┃┣┳┛
 ╹ ┗━┛╹┗╸╹┗╸┗━╸╹ ╹ ╹ ┗━┛╹┗╸
""".strip("\n")

# Bold spaced title shown above the logo
TITLE = "T O R R E N T O R"


# Apply a cyan-to-magenta gradient to the logo characters
def _gradient_logo() -> Text:
    """Return the logo as a Rich Text object with a per-character colour gradient."""
    text = Text()
    colors = [CYAN, CYAN, ACCENT, ACCENT, MAGENTA, MAGENTA, ACCENT, CYAN, CYAN]
    for line in LOGO.splitlines():
        chars = list(line)
        # How many characters each colour segment covers
        segment_len = max(1, len(chars) // len(colors))
        for i, ch in enumerate(chars):
            color_idx = min(i // segment_len, len(colors) - 1)
            text.append(ch, style=f"bold {colors[color_idx]}")
        text.append("\n")
    return text


# Print the full banner to the console
def show_banner() -> None:
    """Draw the bold title, gradient logo, version, and author inside a styled panel."""
    # Bold spaced title at the top
    title_text = Text(TITLE, style=f"bold {CYAN}", justify="center")

    logo = _gradient_logo()

    # Tagline with version and author
    tagline = Text()
    tagline.append(f"v{__version__}", style=f"bold {CYAN}")
    tagline.append("  ·  ", style=DIM)
    tagline.append(f"by {__author__}", style=f"italic {DIM}")

    content = Text("\n")
    content.append_text(title_text)
    content.append("\n\n")
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
