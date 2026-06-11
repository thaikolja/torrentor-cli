"""Color palette, Rich console with custom theme, and InquirerPy style overrides."""

from InquirerPy.utils import get_style
from rich.console import Console
from rich.theme import Theme

# Brand colours — picked to look great on a dark terminal
CYAN = "#00d7ff"
MAGENTA = "#ff5fff"
ACCENT = "#87d7ff"
DIM = "#6c6c6c"
SUCCESS = "#00ff87"
ERROR = "#ff5555"
WARNING = "#ffaf00"
TEXT = "#e4e4e4"

# Rich theme so we can use [info], [success], etc. in f-strings / markup
custom_theme = Theme(
    {
        "info": f"bold {CYAN}",
        "accent": f"{ACCENT}",
        "success": f"bold {SUCCESS}",
        "error": f"bold {ERROR}",
        "warning": f"bold {WARNING}",
        "dim": f"{DIM}",
        "heading": f"bold {MAGENTA}",
        "highlight": f"bold {CYAN}",
        "speed.down": f"bold {SUCCESS}",
        "speed.up": f"bold {MAGENTA}",
        "peers": f"{ACCENT}",
        "eta": f"{WARNING}",
    }
)

console = Console(theme=custom_theme)

# InquirerPy style — get_style() remaps keys and adds required defaults
INQUIRER_STYLE = get_style(
    {
        "questionmark": f"{CYAN} bold",
        "answermark": f"{SUCCESS} bold",
        "answer": f"{CYAN}",
        "input": f"{TEXT}",
        "question": "bold",
        "answered_question": "bold",
        "instruction": f"{DIM}",
        "long_instruction": f"{DIM}",
        "pointer": f"{CYAN} bold",
        "checkbox": f"{CYAN} bold",
        "separator": f"{DIM}",
        "skipped": f"{DIM}",
        "validator": "",
        "marker": f"{CYAN} bold",
        "fuzzy_prompt": f"{CYAN} bold",
        "fuzzy_info": f"{DIM}",
        "fuzzy_border": f"{CYAN}",
        "fuzzy_match": f"{MAGENTA} bold",
    }
)
