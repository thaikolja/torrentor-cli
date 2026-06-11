from rich.console import Console
from rich.theme import Theme

CYAN = "#00d7ff"
MAGENTA = "#ff5fff"
ACCENT = "#87d7ff"
DIM = "#6c6c6c"
SUCCESS = "#00ff87"
ERROR = "#ff5555"
WARNING = "#ffaf00"
TEXT = "#e4e4e4"

custom_theme = Theme({
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
})

console = Console(theme=custom_theme)

INQUIRER_STYLE = {
    "questionmark": f"{CYAN} bold",
    "answermark": f"{SUCCESS} bold",
    "answer": f"{CYAN}",
    "input": f"{TEXT}",
    "question": f"bold",
    "answered_question": f"bold",
    "instruction": f"{DIM}",
    "long_instruction": f"{DIM}",
    "pointer": f"{CYAN} bold",
    "checkbox": f"{CYAN} bold",
    "separator": f"{DIM}",
    "skipped": f"{DIM}",
    "validator": f"",
    "marker": f"{CYAN} bold",
    "fuzzy_prompt": f"{CYAN} bold",
    "fuzzy_info": f"{DIM}",
    "fuzzy_border": f"{CYAN}",
    "fuzzy_match": f"{MAGENTA} bold",
}
