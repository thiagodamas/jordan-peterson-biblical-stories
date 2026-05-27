#!/usr/bin/env python3
"""
Generate omnibus (complete) editions containing all 16 Jordan Peterson Biblical lectures.

Produces:
  - Jordan Peterson - Biblical Stories Complete - EN.epub / .pdf / .mobi
  - Jordan Peterson - Biblical Stories Complete - PT-BR.epub / .pdf / .mobi

Usage:
    python scripts/generate_omnibus.py --lang en
    python scripts/generate_omnibus.py --lang pt
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent))
from lectures import LECTURES


def get_transcript_paths(lang: str) -> List[Path]:
    """Return ordered list of all TRANSCRIPT.md paths for a language."""
    base = Path("Biblical Stories")
    paths = []

    for lec in LECTURES:
        num = lec["number"]
        title_en = lec["title"]

        if lang == "en":
            folder = base / "EN" / f"{num:02d}. {title_en}"
        else:
            # Find the actual PT-BR folder (handles accents)
            pt_folder = None
            for candidate in (base / "PT-BR").glob(f"{num:02d}.*"):
                pt_folder = candidate
                break
            if not pt_folder:
                raise FileNotFoundError(f"PT-BR folder for lecture {num} not found")
            folder = pt_folder

        transcript = folder / "TRANSCRIPT.md"
        if not transcript.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript}")
        paths.append(transcript)

    return paths


def get_covers(lang: str) -> List[Path]:
    """Return list of cover images (empty string where missing)."""
    base = Path("Biblical Stories")
    covers = []

    for lec in LECTURES:
        num = lec["number"]
        title_en = lec["title"]

        if lang == "en":
            folder = base / "EN" / f"{num:02d}. {title_en}"
        else:
            for candidate in (base / "PT-BR").glob(f"{num:02d}.*"):
                folder = candidate
                break
            else:
                folder = None

        cover = folder / "cover.jpg" if folder else None
        covers.append(cover if cover and cover.exists() else None)

    return covers


def build_omnibus(lang: str, output_dir: Path):
    """Generate the complete omnibus edition in all three formats."""
    is_en = lang == "en"
    suffix = "EN" if is_en else "PT-BR"

    title = "Biblical Stories" if is_en else "Histórias Bíblicas"
    subtitle = "The Psychological Significance of the Biblical Stories" if is_en else \
               "O Significado Psicológico das Histórias Bíblicas"

    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"Jordan Peterson - {title} - {suffix}"
    epub_path = output_dir / f"{base_name}.epub"
    pdf_path = output_dir / f"{base_name}.pdf"
    mobi_path = output_dir / f"{base_name}.mobi"

    transcripts = get_transcript_paths(lang)
    covers = get_covers(lang)

    print(f"\n=== Building OMNIBUS ({suffix}) ===")
    print(f"Total lectures: {len(transcripts)}")

    # Create a temporary combined markdown with proper structure
    combined_md = []
    combined_md.append("---")
    combined_md.append(f"title: \"{title}\"")
    combined_md.append(f"subtitle: \"{subtitle}\"")
    combined_md.append("author: \"Dr. Jordan B. Peterson\"")
    combined_md.append(f"lang: \"{'en' if is_en else 'pt-BR'}\"")
    combined_md.append("---")
    combined_md.append("")
    combined_md.append("# Jordan B. Peterson")
    combined_md.append("")
    combined_md.append(f"## {subtitle}")
    combined_md.append("")
    combined_md.append("---")
    combined_md.append("")

    # Add each lecture as a top-level chapter
    for i, transcript in enumerate(transcripts):
        lec = LECTURES[i]
        num = lec["number"]

        # Read the original transcript
        content = transcript.read_text(encoding="utf-8")

        # Proposta 1: Título único e completo por palestra (sem duplicação)
        if is_en:
            combined_md.append(f"# Lecture {num:02d}: {lec['full_title']}")
        else:
            roman = to_roman(num)
            combined_md.append(f"# Palestra {num:02d}: Série Bíblica {roman}: {get_pt_lecture_title(num)}")

        combined_md.append("")
        combined_md.append("")

        # --- SIMPLE CONTENT EXTRACTION ---
        # We standardized that every TRANSCRIPT.md now starts its actual spoken
        # content with "## Seção I" (or "## Section I"). We just take everything
        # from that point onward, exactly as it is in the source.
        #
        # This preserves all the real sections (Seção I, II, III...) at the same
        # heading level so they all appear properly in the TOC.
        marker = "## Section I" if is_en else "## Seção I"
        idx = content.find(marker)

        if idx != -1:
            body = content[idx:]
        else:
            # Fallback — should not happen now
            body = content

        # Append the body as-is (## Seção I, ## Seção II, ## Seção III, etc.)
        combined_md.append(body)
        combined_md.append("")

        # Force each lecture to start on a new page.
        # - \newpage works excellently with pdflatex (PDF)
        # - The div works for WeasyPrint and EPUB readers
        combined_md.append('<div style="page-break-before: always;"></div>')
        combined_md.append(r"\newpage")
        combined_md.append("")
        combined_md.append("---")  # Visual separator
        combined_md.append("")

    # Write temporary combined file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write("\n".join(combined_md))
        tmp_path = Path(tmp.name)

    print(f"  Temporary combined file created: {tmp_path}")

    try:
        # 1. EPUB
        print("Generating Complete EPUB...")
        cmd = [
            "pandoc", str(tmp_path),
            "-o", str(epub_path),
            "--to", "epub3",
            "--toc",
            "--toc-depth=2",
            "--epub-chapter-level=1",
            "--css=assets/ebook-style.css",
            "--standalone",
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # 2. MOBI from EPUB (using Calibre)
        print("Generating Complete MOBI...")
        cmd = [
            "ebook-convert",
            str(epub_path),
            str(mobi_path),
            "--mobi-file-type", "both",
            "--title", f"{title} Complete - {suffix}",
            "--authors", "Jordan B. Peterson",
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # 3. PDF from EPUB (using Calibre)
        # This is more reliable in CI than Pandoc's PDF engines (pdflatex/weasyprint).
        # Calibre produces consistent results and respects our page-break rules and CSS.
        print("Generating Complete PDF from EPUB...")
        cmd = [
            "ebook-convert",
            str(epub_path),
            str(pdf_path),
            "--pdf-page-size", "A4",
            "--pdf-default-font-size", "11",
            "--pdf-mono-font-size", "10",
            "--pdf-margin-left", "1.8cm",
            "--pdf-margin-right", "1.8cm",
            "--pdf-margin-top", "1.8cm",
            "--pdf-margin-bottom", "1.8cm",
            "--title", f"{title} - {suffix}",
            "--authors", "Jordan B. Peterson",
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    finally:
        tmp_path.unlink(missing_ok=True)

    print(f"\n✓ Omnibus complete for {suffix}")
    print(f"  - {epub_path.name}")
    print(f"  - {pdf_path.name}")
    print(f"  - {mobi_path.name}")

    return epub_path, pdf_path, mobi_path


def to_roman(n: int) -> str:
    """Convert number to Roman numeral (supports 1-16)."""
    val = [10, 9, 5, 4, 1]
    syb = ["X", "IX", "V", "IV", "I"]
    roman_num = ""
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num


def get_pt_lecture_title(num: int) -> str:
    titles = {
        1: "Introdução à Ideia de Deus",
        2: "Gênesis 1: Caos e Ordem",
        3: "Deus e a Hierarquia de Autoridade",
        4: "Adão e Eva: Autoconsciência, Mal e Morte",
        5: "Caim e Abel: Os Irmãos Hostis",
        6: "A Psicologia do Dilúvio",
        7: "Andando com Deus: Noé e o Dilúvio",
        8: "A Fenomenologia do Divino",
        9: "O Chamado de Abraão",
        10: "Abraão: Pai das Nações",
        11: "Sodoma e Gomorra",
        12: "O Grande Sacrifício: Abraão e Isaque",
        13: "A Escada de Jacó",
        14: "Jacó: Lutando com Deus",
        15: "José e a Túnica de Muitas Cores",
        16: "Sobre a Morte e a Ressurreição: Uma Visão Psicológica",
    }
    return titles[num]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["en", "pt"], required=True)
    parser.add_argument("--output", type=Path, default=Path("dist/ebooks"))
    args = parser.parse_args()

    build_omnibus(args.lang, args.output)


if __name__ == "__main__":
    main()