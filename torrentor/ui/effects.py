"""Terminal effects — confetti celebration when a download completes. Works on all OSes via Rich."""

import random
import time

from rich.live import Live
from rich.text import Text

from torrentor.ui.theme import ACCENT, CYAN, MAGENTA, SUCCESS, WARNING, console

# Characters that make up the confetti burst
_PARTICLES = ["✦", "✧", "◆", "◇", "★", "☆", "✶", "✷", "❖", "⬥", "⬦", "●", "◉"]

# Colours for each confetti particle
_COLORS = [CYAN, MAGENTA, SUCCESS, WARNING, ACCENT, "#ff87af", "#d7af5f", "#afafff"]


# Build a block of random confetti characters with random colours
def _confetti_block(width: int, lines: int) -> Text:
    """Generate a block of randomly coloured confetti particles."""
    block = Text()
    for row in range(lines):
        for _ in range(width):
            # Mix in gaps so it doesn't look too dense
            if random.random() < 0.35:
                char = random.choice(_PARTICLES)
                color = random.choice(_COLORS)
                block.append(f" {char}", style=f"bold {color}")
            else:
                block.append("  ")
        if row < lines - 1:
            block.append("\n")
    return block


# Run the celebration animation using Rich Live (cross-platform, no raw ANSI)
def celebrate(frames: int = 4, lines: int = 3, delay: float = 0.15) -> None:
    """Print a short burst of confetti across the terminal. Uses Rich Live for cross-platform support."""
    width = min(console.width // 2, 40)

    # Animate several frames of confetti using Rich's Live display
    with Live(console=console, refresh_per_second=10) as live:
        for _ in range(frames):
            live.update(_confetti_block(width, lines))
            time.sleep(delay)

    # Final static frame
    console.print(_confetti_block(width, lines), justify="center")
    console.print()
