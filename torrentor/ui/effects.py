"""Terminal effects — confetti celebration when a download completes."""

import random
import time

from rich.text import Text

from torrentor.ui.theme import ACCENT, CYAN, MAGENTA, SUCCESS, WARNING, console

# Characters that make up the confetti burst
_PARTICLES = ["✦", "✧", "◆", "◇", "★", "☆", "✶", "✷", "❖", "⬥", "⬦", "●", "◉"]

# Colours for each confetti particle
_COLORS = [CYAN, MAGENTA, SUCCESS, WARNING, ACCENT, "#ff87af", "#d7af5f", "#afafff"]


# Build one line of random confetti characters with random colours
def _confetti_line(width: int) -> Text:
    """Generate a single line of randomly coloured confetti particles."""
    line = Text()
    for _ in range(width):
        # Mix in gaps so it doesn't look too dense
        if random.random() < 0.35:
            char = random.choice(_PARTICLES)
            color = random.choice(_COLORS)
            line.append(f" {char}", style=f"bold {color}")
        else:
            line.append("  ")
    return line


# Run the celebration animation
def celebrate(frames: int = 4, lines: int = 3, delay: float = 0.15) -> None:
    """Print a short burst of confetti across the terminal."""
    width = min(console.width // 2, 40)

    for _ in range(frames):
        # Print a few lines of confetti
        for _ in range(lines):
            console.print(_confetti_line(width), justify="center")
        time.sleep(delay)
        # Move cursor back up to overwrite on next frame
        console.file.write(f"\033[{lines}A")
        console.file.flush()

    # Final frame stays on screen
    for _ in range(lines):
        console.print(_confetti_line(width), justify="center")
    console.print()
