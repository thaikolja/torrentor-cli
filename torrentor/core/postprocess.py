import re
import shutil
import unicodedata
import zipfile
from pathlib import Path


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[-\s]+", "-", name).strip("-")
    return name or "download"


def _unique_path(path: Path) -> Path:
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


def zip_and_move(source_dir: Path, output_dir: Path) -> Path:
    items = list(source_dir.iterdir())
    items = [p for p in items if not p.name.startswith(".")]

    if not items:
        raise FileNotFoundError(f"No downloaded files found in {source_dir}")

    target = items[0] if len(items) == 1 else source_dir
    raw_name = target.stem if target.is_file() else target.name
    slug = slugify(raw_name)

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = _unique_path(output_dir / f"{slug}.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        if target.is_file():
            zf.write(target, target.name)
        else:
            for file in sorted(target.rglob("*")):
                if file.is_file() and not file.name.startswith("."):
                    zf.write(file, file.relative_to(target))

    return zip_path


def cleanup(temp_dir: Path) -> None:
    shutil.rmtree(temp_dir, ignore_errors=True)


def format_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} {unit}"
        size_bytes /= 1024  # type: ignore[assignment]
    return f"{size_bytes:.1f} PB"
