from pathlib import Path
from collections import defaultdict
import hashlib
import os
import shutil

CHUNK_SIZE = 1024 * 1024
CATEGORY_MAP = {
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".java", ".c", ".cpp", ".json", ".sql", ".sh"},
}


def format_size(size):
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} TB"


def get_file_type(path):
    suffix = Path(path).suffix.lower()
    for category, extensions in CATEGORY_MAP.items():
        if suffix in extensions:
            return category
    return "Other"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_folder(folder):
    root = Path(folder).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"Folder does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a folder: {root}")

    records = []
    errors = []
    hashes = defaultdict(list)
    for current, dirs, names in os.walk(root):
        # Do not follow symlinks; avoid recursing through linked folders.
        dirs[:] = [d for d in dirs if not (Path(current) / d).is_symlink()]
        for name in names:
            path = Path(current) / name
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                stat = path.stat()
                digest = sha256_file(path)
                record = {
                    "name": path.name,
                    "path": str(path),
                    "extension": path.suffix.lower() or "",
                    "file_type": get_file_type(path),
                    "size_bytes": stat.st_size,
                    "size": format_size(stat.st_size),
                    "modified": __import__("datetime").datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "sha256": digest,
                }
                records.append(record)
                hashes[(stat.st_size, digest)].append(record)
            except (OSError, PermissionError) as exc:
                errors.append({"path": str(path), "error": str(exc)})

    duplicate_groups = []
    for (_, digest), items in hashes.items():
        if len(items) > 1:
            duplicate_groups.append({
                "hash": digest,
                "size_bytes": items[0]["size_bytes"],
                "size": format_size(items[0]["size_bytes"]),
                "total_bytes": items[0]["size_bytes"] * len(items),
                "files": [{"name": item["name"], "path": item["path"]} for item in items],
            })
    duplicate_groups.sort(key=lambda group: group["size_bytes"], reverse=True)
    records.sort(key=lambda record: record["name"].lower())
    return records, duplicate_groups, errors


def _safe_destination(destination):
    candidate = destination
    counter = 1
    while candidate.exists():
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        counter += 1
    return candidate


def organize_files(folder, dry_run=True):
    root = Path(folder).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"Folder does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a folder: {root}")

    plans = []
    # Only move files directly inside the selected folder; nested folders are left untouched.
    for path in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file() or path.is_symlink():
            continue
        category = get_file_type(path)
        destination_dir = root / category
        destination = _safe_destination(destination_dir / path.name)
        plans.append({"source": str(path), "destination": str(destination), "category": category})

    moved = 0
    if not dry_run:
        for plan in plans:
            source = Path(plan["source"])
            destination = Path(plan["destination"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Re-check to avoid overwriting a file created after preview.
            destination = _safe_destination(destination)
            shutil.move(str(source), str(destination))
            plan["destination"] = str(destination)
            moved += 1
    return {"planned": len(plans), "moved": moved, "items": plans}
