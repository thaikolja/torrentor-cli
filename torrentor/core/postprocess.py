"""Zips downloaded content with light compression, slugifies the filename, and cleans up temp dirs."""

import re
import shutil
import unicodedata
import zipfile
from pathlib import Path


# Turn any string into a URL-safe slug: lowercase, hyphens instead of spaces, no special chars
def slugify(name: str) -> str:
    """Convert a human-readable name into a clean slug (e.g. 'My Movie! (2024)' → 'my-movie-2024')."""
    # Decompose unicode characters so 'é' becomes 'e' + combining accent, then strip the accent
    name = unicodedata.normalize("NFKD", name)
    # Drop everything that isn't ASCII
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    # Remove anything that's not a letter, number, whitespace, or hyphen
    name = re.sub(r"[^\w\s-]", "", name)
    # Collapse runs of whitespace and hyphens into a single hyphen
    name = re.sub(r"[-\s]+", "-", name).strip("-")
    # Edge case: if everything was stripped, return a fallback
    return name or "download"


# Preview what the zip filename will be before the download even starts
def predict_zip_filename(name: str) -> str:
    """Return the expected .zip filename for a given torrent name (e.g. 'my-movie-2024.zip')."""
    return f"{slugify(name)}.zip"


# If a zip file already exists at the target path, append -1, -2, etc.
def _unique_path(path: Path) -> Path:
    """Return a path that doesn't exist yet by appending -N suffixes if needed."""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


# Zip the downloaded content and move it to the user's output directory
def zip_and_move(source_dir: Path, output_dir: Path) -> Path:
    """Zip everything in source_dir into output_dir/<slug>.zip, using light compression (level 1)."""
    # List all files/dirs in the download dir, skipping dotfiles
    items = list(source_dir.iterdir())
    items = [p for p in items if not p.name.startswith(".")]

    # Nothing was downloaded — error out
    if not items:
        raise FileNotFoundError(f"No downloaded files found in {source_dir}")

    # If there's exactly one item use that, otherwise zip the whole directory
    target = items[0] if len(items) == 1 else source_dir
    raw_name = target.stem if target.is_file() else target.name
    slug = slugify(raw_name)

    # Make sure the output directory exists
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pick a name that doesn't clash with existing files
    zip_path = _unique_path(output_dir / f"{slug}.zip")

    # Write the zip with minimal compression (level 1 = fast, slightly smaller size)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        if target.is_file():
            zf.write(target, target.name)
        else:
            for file in sorted(target.rglob("*")):
                if file.is_file() and not file.name.startswith("."):
                    zf.write(file, file.relative_to(target))

    return zip_path


# Remove a temporary directory and everything inside it
def cleanup(temp_dir: Path) -> None:
    """Recursively delete a temp directory — safe to call on non-existent paths."""
    shutil.rmtree(temp_dir, ignore_errors=True)


# Convert raw bytes into a human-readable size string
def format_size(size_bytes: int) -> str:
    """Pretty-print a byte count (e.g. 1_234_567 → '1.2 MB')."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} {unit}"
        size_bytes //= 1024
    return f"{size_bytes:.1f} PB"
