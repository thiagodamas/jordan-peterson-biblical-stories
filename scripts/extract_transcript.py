#!/usr/bin/env python3
"""
extract_transcript.py
Extracts and cleans Jordan Peterson Biblical Series transcripts from MHTML archives
into high-quality Markdown matching the style of the existing Lecture 01.

Usage:
    python3 scripts/extract_transcript.py 1                 # extract lecture 1
    python3 scripts/extract_transcript.py --all             # extract all 16
    python3 scripts/extract_transcript.py 1 --output-dir ./tmp
"""

import argparse
import email
import os
import re
import sys
from email import policy
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Tag
import markdownify
import requests

# Local import
sys.path.insert(0, str(Path(__file__).parent))
from lectures import LECTURES, get_lecture, get_mhtml_path


# ---------------------------------------------------------------------------
# MHTML / HTML extraction
# ---------------------------------------------------------------------------

def extract_html_from_mhtml(mhtml_path: str | Path) -> str:
    """Return the main text/html content from a Blink/Chromium MHTML archive."""
    with open(mhtml_path, "rb") as f:
        msg = email.message_from_bytes(f.read(), policy=policy.default)

    for part in msg.iter_parts():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            if payload:
                return payload.decode("utf-8", errors="replace")
    raise ValueError(f"No text/html part found in {mhtml_path}")


def find_main_content(soup: BeautifulSoup) -> Tag:
    """
    Locate the main transcript content container.
    The old jordanbpeterson.com used .post-content (Avada/WordPress theme).
    """
    candidates = [
        soup.select_one(".post-content"),
        soup.select_one("article"),
        soup.select_one(".entry-content"),
        soup.select_one("#main"),
        soup.select_one(".content"),
    ]
    for c in candidates:
        if c and len(c.get_text(strip=True)) > 2000:
            return c

    # Fallback: largest div with substantial text
    best = None
    best_len = 0
    for div in soup.find_all("div"):
        text_len = len(div.get_text(strip=True))
        if text_len > best_len:
            best_len = text_len
            best = div
    if best:
        return best

    # Last resort
    return soup.body or soup


def collect_all_transcript_content(soup: BeautifulSoup) -> Tag:
    """
    Enhanced collector for old jordanbpeterson.com pages.
    Some sections were hidden inside .spoiler divs. We try to gather
    the main content + any spoiler blocks that contain real transcript text.
    """
    main = find_main_content(soup)
    
    # Collect any .spoiler divs that have substantial text (these often contained
    # the actual spoken content after section headings on the old site)
    spoilers = soup.select(".spoiler")
    for sp in spoilers:
        if len(sp.get_text(strip=True)) > 300:
            # Append the spoiler content to the main container for extraction
            main.append(sp)
    
    return main


def clean_soup(soup: BeautifulSoup) -> None:
    """
    Conservative cleanup: remove only obvious non-content elements
    (navigation, sidebars, share widgets, etc.) without touching the
    actual transcript text.
    """
    # Safe selectors that usually contain junk
    junk_selectors = [
        "header", "footer", "nav", "aside",
        ".sidebar", ".menu", ".widget", ".jetpack",
        "script", "style", "noscript",
        ".fusion-header", ".avada-footer", ".elementor-location-header",
        '[class*="share-"]', '[id*="share"]',
        ".related-posts", ".post-share", ".social-links",
        ".comment", ".comments-area",
        # Do NOT remove .spoiler — the old site put real transcript content inside these
    ]
    for sel in junk_selectors:
        for el in soup.select(sel):
            el.decompose()

    # Remove small UI elements by text content (very conservative)
    for el in soup.find_all(True):
        if el.name in ("a", "button", "span"):
            txt = el.get_text(strip=True).lower()
            if txt in {"share", "tweet", "pin", "email", "print", "subscribe", "next", "previous"}:
                el.decompose()


# ---------------------------------------------------------------------------
# Markdown conversion + post-processing (Opção A - aggressive cleaning)
# ---------------------------------------------------------------------------

def html_to_markdown(html: str) -> str:
    """Convert cleaned HTML fragment to Markdown."""
    md = markdownify.markdownify(
        html,
        heading_style="ATX",
        bullets="-",
        strip=["img", "picture", "figure"],  # we'll handle images separately
    )
    return md


def normalize_sections(md: str) -> str:
    """Turn 'Section II', 'Section 2', etc. into proper ## headings."""
    def replacer(match):
        num = match.group(1)
        # Convert roman or digit to consistent format
        return f"\n## Section {num}\n"

    # Handle "Section II", "Section 2", "Section Two", etc.
    md = re.sub(
        r"(?im)^\s*(?:Section\s+)?([IVXLCDM]+|\d+)\s*[:\-]?\s*$",
        replacer,
        md,
    )
    # Also catch inline versions sometimes present
    md = re.sub(
        r"(?im)\bSection\s+([IVXLCDM]+|\d+)\s*[:\-]?\s*$",
        lambda m: f"\n## Section {m.group(1)}\n",
        md,
    )
    return md


def clean_markdown(md: str) -> str:
    """Aggressive post-processing to reach near the quality of the reference Lecture 01."""
    # Remove Wayback Machine archive.org pollution
    md = re.sub(r"https://web\.archive\.org/web/\d+/", "", md)
    md = re.sub(r"\(https://web\.archive\.org[^)]+\)", "", md)
    md = re.sub(r"\[([^\]]+)\]\(https://web\.archive\.org[^)]+\)", r"\1", md)

    # Remove old site navigation / meta junk
    md = re.sub(r"(?im)^\s*(?:Share your thoughts|Leave a comment|Click to share|Tweet|Pin|Email|Print)\b.*$", "", md)
    md = re.sub(r"(?im)^\s*Sections?:\s*\[.*$", "", md)
    md = re.sub(r"(?im)^\s*Keywords?:\s*.*$", "", md)
    md = re.sub(r"(?im)^\s*Biblical Series [IVXLCDM]+:.*$", "", md)
    md = re.sub(r"(?im)^\s*by Dr\. Jordan Peterson\s*$", "", md)

    # Remove duplicate YouTube / Podcast lines that leak from the page
    md = re.sub(r"(?im)^\s*\[YouTube Video\].*$", "", md)
    md = re.sub(r"(?im)^\s*\[Podcast Episode\].*$", "", md)

    # Remove common UI leftovers
    artifacts = [
        r"^\s*Share\s*$", r"^\s*Tweet\s*$", r"^\s*Pin\s*$",
        r"^\s*Email\s*$", r"^\s*Print\s*$", r"^\s*Related\s*$",
        r"^\s*Comments?\s*$", r"^\s*\d+\s+shares?\s*$",
        r"^\s*Podcast Episode\s*$",
    ]
    for pat in artifacts:
        md = re.sub(pat, "", md, flags=re.IGNORECASE | re.MULTILINE)

    # Collapse excessive whitespace
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = md.strip()

    return md


# ---------------------------------------------------------------------------
# Front matter generation (matching existing style)
# ---------------------------------------------------------------------------

def generate_front_matter(lecture: dict, cover_path: Optional[str] = None) -> str:
    title = lecture["full_title"]
    yt = lecture.get("youtube_id")
    keywords = lecture.get("keywords", [])

    lines = [f"# **{title}**  ", "", "by Dr. Jordan Peterson", ""]

    if cover_path:
        lines.append(f"![Picture](./{cover_path})")
        lines.append("")

    if yt:
        lines.append(f"YouTube Video (https://www.youtube.com/watch?v={yt})")
        lines.append("")

    if keywords:
        lines.append("*Keywords: " + ", ".join(keywords) + "*")
        lines.append("")

    # Placeholder for section navigation (filled later during review)
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main extraction pipeline
# ---------------------------------------------------------------------------

def extract_lecture(number: int, output_dir: Optional[Path] = None) -> Path:
    lec = get_lecture(number)
    mhtml_path = get_mhtml_path(number)

    if not os.path.exists(mhtml_path):
        raise FileNotFoundError(f"MHTML not found: {mhtml_path}")

    print(f"[{number:02d}] Extracting: {lec['title']}")

    raw_html = extract_html_from_mhtml(mhtml_path)
    soup = BeautifulSoup(raw_html, "html.parser")

    # Use the enhanced collector that also pulls in .spoiler content
    # (the old site hid large parts of the transcript inside these)
    main = collect_all_transcript_content(soup)
    clean_soup(main)

    # Convert to markdown
    md = html_to_markdown(str(main))
    md = normalize_sections(md)
    md = clean_markdown(md)

    # Generate output
    folder_name = f"{number:02d}. {lec['title']}"
    if output_dir is None:
        base = Path("Biblical Stories") / folder_name
    else:
        base = output_dir / folder_name
    base.mkdir(parents=True, exist_ok=True)

    # For now we don't have the cover yet; will be added by download step
    front = generate_front_matter(lec, cover_path=None)
    final = front + md

    out_path = base / "TRANSCRIPT.md"
    out_path.write_text(final, encoding="utf-8")
    print(f"      → {out_path}")

    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers", nargs="*", type=int, help="Lecture numbers (1-16)")
    parser.add_argument("--all", action="store_true", help="Extract all 16 lectures")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override output base dir")
    args = parser.parse_args()

    if args.all:
        numbers = list(range(1, 17))
    elif args.numbers:
        numbers = args.numbers
    else:
        parser.print_help()
        sys.exit(1)

    for n in numbers:
        try:
            extract_lecture(n, args.output_dir)
        except Exception as e:
            print(f"[{n:02d}] ERROR: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
