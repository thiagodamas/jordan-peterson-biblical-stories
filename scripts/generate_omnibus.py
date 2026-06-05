#!/usr/bin/env python3
"""
Generate omnibus (complete) editions containing all 16 Jordan Peterson Biblical lectures.

Produces clean EPUB + MOBI (PDF is optional locally via --pdf).

Key characteristics (after simplification):
- Notes appear only as a styled section at the end of each lecture (no inline [^n] references).
- Much simpler and more reliable generation process.
- Works well in Apple Books and other readers.

Usage examples:
    python3 scripts/generate_omnibus.py --lang pt
    python3 scripts/generate_omnibus.py --lang en --pdf
"""

import argparse
import os
import re
import shutil
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


def split_lecture_content(full_content: str) -> tuple[str, str]:
    """
    Simple split: returns (spoken_body, notes_section_raw).
    Notes section is everything after the first **Notas** marker.
    This replaces the old complex footnote renumbering logic.
    """
    markers = ["**Notas**", "Notas\n", "\nNotas"]
    for marker in markers:
        if marker in full_content:
            body, notes = full_content.split(marker, 1)
            return body.rstrip(), notes.strip()
    return full_content, ""


def build_omnibus(lang: str, output_dir: Path, generate_pdf: bool = False):
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

    base = Path("Biblical Stories")
    transcripts = get_transcript_paths(lang)

    print(f"\n=== Building OMNIBUS ({suffix}) ===")
    print(f"Total lectures: {len(transcripts)}")

    # Create a temporary combined markdown with proper structure
    combined_md = []
    combined_md.append("---")
    combined_md.append(f"title: \"{title}\"")
    combined_md.append(f"subtitle: \"{subtitle}\"")
    combined_md.append("author: \"Dr. Jordan B. Peterson\"")
    combined_md.append(f"lang: \"{'en' if is_en else 'pt-BR'}\"")
    combined_md.append("source: \"Transcripts from Jordan B. Peterson's Biblical Series lectures (YouTube, 2017)\"")
    combined_md.append("repository: \"https://github.com/thiagodamas/jordan-peterson-biblical-stories\"")
    combined_md.append("original-series: \"The Psychological Significance of the Biblical Stories\"")
    combined_md.append("---")
    combined_md.append("")
    combined_md.append("# Jordan B. Peterson")
    combined_md.append("")
    combined_md.append(f"## {subtitle}")
    combined_md.append("")
    combined_md.append("---")
    combined_md.append("")

    # Introduction / Origin metadata (bilingual-aware)
    if is_en:
        combined_md.append("## About This Edition")
        combined_md.append("")
        combined_md.append("This volume brings together the complete transcripts of Jordan B. Peterson's 2017 lecture series *The Psychological Significance of the Biblical Stories*. The material is made available for educational and personal study purposes.")
        combined_md.append("")
        combined_md.append("All lectures were originally delivered and publicly recorded on YouTube. This community project provides high-quality, spoken-style transcripts in English (the original) and Brazilian Portuguese, with footnotes for technical terms and conceptual clarifications.")
        combined_md.append("")
        combined_md.append("**Original Source**: Jordan B. Peterson – \"The Psychological Significance of the Biblical Stories\" (YouTube, 2017)")
        combined_md.append("**Repository**: https://github.com/thiagodamas/jordan-peterson-biblical-stories")
        combined_md.append("")
        combined_md.append("---")
        combined_md.append("")
    else:
        combined_md.append("## Sobre Esta Edição")
        combined_md.append("")
        combined_md.append("Este volume reúne as transcrições completas da série de palestras de Jordan B. Peterson de 2017 intitulada *O Significado Psicológico das Histórias Bíblicas*. O material é disponibilizado para fins educacionais e de estudo pessoal.")
        combined_md.append("")
        combined_md.append("Todas as palestras foram originalmente proferidas e gravadas publicamente no YouTube. Este projeto comunitário oferece transcrições de alta qualidade em tom oral, em inglês (original) e português brasileiro, com notas de rodapé para termos técnicos e esclarecimentos conceituais.")
        combined_md.append("")
        combined_md.append("**Fonte original**: Palestras de Jordan B. Peterson – \"The Psychological Significance of the Biblical Stories\" (YouTube, 2017)")
        combined_md.append("**Repositório**: https://github.com/thiagodamas/jordan-peterson-biblical-stories")
        combined_md.append("")
        combined_md.append("---")
        combined_md.append("")

    # Add each lecture as a top-level chapter
    for i, transcript in enumerate(transcripts):
        lec = LECTURES[i]
        num = lec["number"]

        # Read the original transcript
        content = transcript.read_text(encoding="utf-8")

        # Consistent chapter title formatting for clean TOC in both languages
        roman = to_roman(num)
        if is_en:
            combined_md.append(f"# Lecture {num:02d}: Biblical Series {roman}: {lec['title']}")
        else:
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
        front = content[:idx] if idx != -1 else ""
        relevant = content[idx:] if idx != -1 else content

        # Include the per-lecture cover image (added for visualization) in the omnibus.
        # Extract from front matter and fix path to be relative to Biblical Stories root
        # so Pandoc can find and embed it with --resource-path.
        cover_img = ""
        m = re.search(r'!\[[^\]]*\]\(([^)]*cover\.jpg[^)]*)\)', front, re.IGNORECASE)
        if m:
            orig_ref = m.group(0)
            rel_folder = transcript.relative_to(base).parent
            cover_img = orig_ref.replace("](cover.jpg)", f"]({rel_folder}/cover.jpg)")

        # Simple split - no more renumbering or Pandoc footnote magic needed.
        # Notes are now just another section with distinct formatting.
        body, notes_raw = split_lecture_content(relevant)

        if cover_img:
            combined_md.append(cover_img)
            combined_md.append("")

        combined_md.append(body)
        combined_md.append("")

        # Render notes (if present) as a clearly styled section at the end of the lecture.
        # This is now the only way notes appear - always visible, reliable across readers.
        if notes_raw:
            combined_md.append("")
            combined_md.append("::: {.lecture-notes}")
            combined_md.append("### Notas")
            combined_md.append("")

            # Reformat the raw [^n]: lines into clean, readable paragraphs
            # while keeping the original note numbers.
            note_lines = re.findall(r'^\[\^(\d+)\]:\s*(.*?)(?=\n\[\^|\Z)', notes_raw, re.MULTILINE | re.DOTALL)
            if note_lines:
                for num, text in note_lines:
                    # Aggressive whitespace normalization to remove any leading
                    # tabs/spaces from continuation lines in the original notes.
                    clean_text = ' '.join(text.split())
                    combined_md.append(f"**{num}.** {clean_text}")
                    combined_md.append("")
            else:
                # Fallback: dump raw notes content
                combined_md.append(notes_raw)

            combined_md.append(":::")
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
            "--resource-path", str(base),
        ]
        # Note: No --epub-cover-image here — main cover is text-only (title/subtitle only),
        # as requested. Per-chapter cover images are included in the content via markdown.
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
        # No --cover here — main cover is text-only (title/subtitle only).
        # Per-chapter covers come from the EPUB content.
        subprocess.run(cmd, check=True, capture_output=True)

        # 3. PDF from EPUB (using Calibre) - only if explicitly requested
        pdf_success = False
        if generate_pdf:
            print("Generating Complete PDF from EPUB...")
            try:
                is_macos = sys.platform == "darwin"

                if is_macos:
                    print("Note: PDF generation via command line can be unreliable on macOS.")
                    print("      If it fails, we strongly recommend using the Calibre GUI instead.\n")

                # Base command (works on all platforms)
                base_cmd = [
                    "ebook-convert",
                    str(epub_path),
                    str(pdf_path),
                    "--title", f"{title} - {suffix}",
                    "--authors", "Jordan B. Peterson",
                ]
                
                # Full PDF options (work well on Linux/CI, may not exist on some macOS Calibre installs)
                full_options = [
                    "--pdf-page-size", "A4",
                    "--pdf-default-font-size", "11",
                    "--pdf-mono-font-size", "10",
                    "--pdf-margin-left", "1.8cm",
                    "--pdf-margin-right", "1.8cm",
                    "--pdf-margin-top", "1.8cm",
                    "--pdf-margin-bottom", "1.8cm",
                ]
                
                # Try full options first
                pdf_cmd = base_cmd + full_options
                
                # Use xvfb-run only in headless/CI Linux environments
                if shutil.which("xvfb-run") and (os.environ.get("CI") or not os.environ.get("DISPLAY")):
                    pdf_cmd = ["xvfb-run", "--auto-servernum", "--server-args=-screen 0 1024x768x24"] + pdf_cmd
                
                pdf_success = True
                subprocess.run(pdf_cmd, check=True, capture_output=True)
            except Exception as e:
                pdf_success = False
                stderr = getattr(e, 'stderr', None)
                if stderr and isinstance(stderr, (bytes, bytearray)):
                    stderr = stderr.decode('utf-8', errors='ignore')
                elif stderr is None:
                    stderr = str(e)
                print("WARNING: PDF generation failed (ebook-convert returned error).")
                print(f"PDF error output (stderr): {stderr if stderr else 'N/A'}")
                if is_macos:
                    print("\n" + "="*70)
                    print("PDF generation failed on macOS.")
                    print("This is a known limitation of Calibre's command-line PDF export on macOS.")
                    print("\nRecommended solution:")
                    print("  1. Open the generated .epub file in the Calibre application.")
                    print("  2. Select the book → click 'Convert books'.")
                    print("  3. Choose PDF as the output format and click OK.")
                    print("     (The GUI conversion is much more reliable on macOS.)")
                    print("="*70 + "\n")

    finally:
        tmp_path.unlink(missing_ok=True)

    print(f"\n✓ Omnibus complete for {suffix}")
    print(f"  - {epub_path.name}")
    print(f"  - {mobi_path.name}")
    if generate_pdf:
        if pdf_success:
            print(f"  - {pdf_path.name}")
        else:
            print("  - PDF generation failed")

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
    parser = argparse.ArgumentParser(
        description="Gera a edição completa (Omnibus) com todas as 16 palestras de Jordan Peterson.",
        epilog="""
Exemplos de uso:
  python3 scripts/generate_omnibus.py --lang pt
  python3 scripts/generate_omnibus.py --lang en --output dist/meus-ebooks
  python3 scripts/generate_omnibus.py --lang pt --pdf          # PDF local (requer Calibre)

Notas importantes:
- As notas agora são uma seção formatada no final de cada palestra (sem referências inline).
- PDF não é gerado no GitHub Actions (apenas localmente via --pdf).
        """.strip()
    )
    parser.add_argument("--lang", choices=["en", "pt"], required=True,
                        help="Idioma: 'en' (inglês) ou 'pt' (português brasileiro)")
    parser.add_argument("--output", type=Path, default=Path("dist/ebooks"),
                        help="Diretório de saída dos arquivos gerados")
    parser.add_argument("--pdf", action="store_true", default=False,
                        help="Gerar também PDF (apenas local, requer Calibre instalado)")
    args = parser.parse_args()

    build_omnibus(args.lang, args.output, generate_pdf=args.pdf)


if __name__ == "__main__":
    main()