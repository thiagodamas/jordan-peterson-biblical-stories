#!/usr/bin/env python3
"""
download_covers.py
Download official YouTube thumbnails (maxresdefault or hqdefault) for all lectures
that have a known youtube_id.

Usage:
    .venv/bin/python3 scripts/download_covers.py 1
    .venv/bin/python3 scripts/download_covers.py --all
"""

import argparse
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from lectures import LECTURES, get_lecture


THUMBNAIL_SIZES = ["maxresdefault", "hqdefault", "mqdefault"]


def download_cover(number: int, output_dir: Path | None = None, lang: str = "en") -> Path | None:
    lec = get_lecture(number)
    yt_id = lec.get("youtube_id")
    if not yt_id:
        print(f"[{number:02d}] No YouTube ID — skipping cover")
        return None

    title = lec["title"]
    folder_name = f"{number:02d}. {title}"

    # Modern structure: default to EN/ or PT-BR/ subdirectories
    if output_dir is None:
        subdir = "EN" if lang.lower() == "en" else "PT-BR"
        base = Path("Biblical Stories") / subdir
    else:
        base = output_dir

    folder = base / folder_name
    folder.mkdir(parents=True, exist_ok=True)

    cover_path = folder / "cover.jpg"

    for size in THUMBNAIL_SIZES:
        url = f"https://img.youtube.com/vi/{yt_id}/{size}.jpg"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200 and len(resp.content) > 10000:
                cover_path.write_bytes(resp.content)
                print(f"[{number:02d}] ✓ Cover saved → {cover_path} ({size})")
                return cover_path
        except Exception as e:
            print(f"[{number:02d}] Warning: failed {size}: {e}")

    print(f"[{number:02d}] ✗ Could not download cover for {yt_id}")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube thumbnail covers for lectures."
    )
    parser.add_argument("numbers", nargs="*", type=int)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Override output base directory (e.g. 'Biblical Stories/EN')")
    parser.add_argument("--lang", choices=["en", "pt"], default="en",
                        help="Language subdirectory when --output-dir is not provided (default: en)")
    args = parser.parse_args()

    numbers = list(range(1, 17)) if args.all else args.numbers
    if not numbers:
        parser.print_help()
        sys.exit(1)

    for n in numbers:
        try:
            download_cover(n, args.output_dir, args.lang)
        except Exception as e:
            print(f"[{n:02d}] ERROR: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
