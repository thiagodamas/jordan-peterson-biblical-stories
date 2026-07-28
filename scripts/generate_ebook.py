#!/usr/bin/env python3
"""
Generate EPUB, PDF and MOBI versions of a single Jordan Peterson Biblical lecture.

Usage:
    python scripts/generate_ebook.py --lecture 1 --lang en
    python scripts/generate_ebook.py --lecture 8 --lang pt

Requirements (in the environment):
    - pandoc
    - weasyprint (for PDF)
    - calibre (ebook-convert for MOBI)
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

# Import the single source of truth
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from lectures import LECTURES, get_lecture
except ImportError:
    print("ERROR: Could not import scripts/lectures.py", file=sys.stderr)
    sys.exit(1)


def strip_image_query_params(markdown: str) -> str:
    """Strip ?v=… (and similar) from local image URLs so Pandoc can find files.

    GitHub-friendly refs like ![Cover](cover.jpg?v=1) break EPUB embedding because
    Pandoc looks for a file literally named ``cover.jpg?v=1``.
    """
    def _repl(m: re.Match) -> str:
        alt, url = m.group(1), m.group(2)
        # Only strip query/fragment on non-http paths
        if re.match(r"https?://", url, re.I):
            return m.group(0)
        clean = re.split(r"[?#]", url, maxsplit=1)[0]
        return f"![{alt}]({clean})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _repl, markdown)


def get_transcript_path(lecture_num: int, lang: str) -> Path:
    """Return the path to the TRANSCRIPT.md for a lecture + language."""
    lec = get_lecture(lecture_num)
    base = Path("Biblical Stories")
    
    if lang == "en":
        folder = base / "EN" / f"{lecture_num:02d}. {lec['title']}"
    else:
        # PT-BR titles are in the folder names
        pt_titles = {
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
        folder = base / "PT-BR" / f"{lecture_num:02d}. {pt_titles[lecture_num]}"
    
    return folder / "TRANSCRIPT.md"


def get_cover_path(lecture_num: int, lang: str) -> Optional[Path]:
    """Return cover.jpg path if it exists."""
    lec = get_lecture(lecture_num)
    base = Path("Biblical Stories")
    
    if lang == "en":
        folder = base / "EN" / f"{lecture_num:02d}. {lec['title']}"
        cover = folder / "cover.jpg"
        return cover if cover.exists() else None
    else:
        # Search in PT-BR folders
        for candidate in (base / "PT-BR").glob(f"{lecture_num:02d}.*"):
            cover = candidate / "cover.jpg"
            if cover.exists():
                return cover
        return None


def build_metadata(lecture_num: int, lang: str) -> dict:
    """Build Pandoc metadata dictionary."""
    lec = get_lecture(lecture_num)
    is_en = lang == "en"
    
    title = lec['full_title'] if is_en else f"Série Bíblica {lecture_num}: {get_pt_title(lecture_num)}"
    
    return {
        "title": title,
        "author": "Dr. Jordan B. Peterson",
        "lang": "en" if is_en else "pt-BR",
        "date": lec.get('date', '2017'),
    }


def get_pt_title(lecture_num: int) -> str:
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
    return titles[lecture_num]


def run_pandoc(input_file: Path, output_file: Path, metadata: dict,
               extra_args: list[str], cover: Optional[Path] = None,
               resource_dir: Optional[Path] = None):
    """Run pandoc with proper arguments.

    ``input_file`` may be a temp copy with cache-busting query strings stripped
    from image paths; ``resource_dir`` should be the original transcript folder
    so relative ``cover.jpg`` resolves correctly.
    """
    cmd = [
        "pandoc",
        str(input_file),
        "-o", str(output_file),
        "--metadata", f"title={metadata['title']}",
        "--metadata", f"author={metadata['author']}",
        "--metadata", f"lang={metadata['lang']}",
        "--css=assets/ebook-style.css",
        "--standalone",
        "--toc",
        "--toc-depth=2",
    ]

    # Resource path = lecture folder (covers live next to TRANSCRIPT.md)
    res = resource_dir if resource_dir is not None else input_file.parent
    cmd += ["--resource-path", str(res)]
    if cover:
        cmd += [f"--epub-cover-image={cover}"]

    cmd += extra_args

    print(f"  → Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"Pandoc failed for {output_file.name}")


def generate_ebook(lecture_num: int, lang: str, output_dir: Path):
    """Generate EPUB, PDF and MOBI for one lecture + language."""
    lec = get_lecture(lecture_num)
    transcript = get_transcript_path(lecture_num, lang)
    cover = get_cover_path(lecture_num, lang)
    metadata = build_metadata(lecture_num, lang)
    
    if not transcript.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript}")
    
    safe_title = f"{lecture_num:02d}. {lec['title'].replace(':', ' -')}"
    lang_suffix = "EN" if lang == "en" else "PT-BR"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    epub_path = output_dir / f"{safe_title} - {lang_suffix}.epub"
    pdf_path = output_dir / f"{safe_title} - {lang_suffix}.pdf"
    mobi_path = output_dir / f"{safe_title} - {lang_suffix}.mobi"
    
    print(f"\n=== Lecture {lecture_num} ({lang.upper()}) ===")
    print(f"Source: {transcript}")

    # Strip ?v=1 (etc.) from local image paths so Pandoc embeds cover.jpg correctly.
    raw = transcript.read_text(encoding="utf-8")
    cleaned = strip_image_query_params(raw)
    tmp_path = None
    try:
        if cleaned != raw:
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            )
            tmp.write(cleaned)
            tmp.close()
            tmp_path = Path(tmp.name)
            pandoc_input = tmp_path
            print("  (normalized image URLs: stripped ?query from local media refs)")
        else:
            pandoc_input = transcript

        resource_dir = transcript.parent

        # 1. EPUB (best quality with Pandoc)
        print("Generating EPUB...")
        run_pandoc(pandoc_input, epub_path, metadata, [
            "--to", "epub3",
            "--epub-chapter-level=2",
        ], cover, resource_dir=resource_dir)

        # 2. PDF via WeasyPrint (lightweight, good typography)
        print("Generating PDF (WeasyPrint)...")
        try:
            run_pandoc(pandoc_input, pdf_path, metadata, [
                "--pdf-engine=weasyprint",
                "-V", "geometry:margin=2cm",
            ], cover, resource_dir=resource_dir)
        except RuntimeError as e:
            print(f"  ⚠️  PDF generation failed (non-fatal): {e}")

        # 3. MOBI from the EPUB we just created (best results)
        print("Generating MOBI (Calibre)...")
        cmd = [
            "ebook-convert",
            str(epub_path),
            str(mobi_path),
            "--mobi-file-type", "both",
            "--title", metadata["title"],
            "--authors", metadata["author"],
            "--language", metadata["lang"],
        ]
        if cover:
            cmd += ["--cover", str(cover)]

        print("  → Running: ebook-convert ...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr)
            print("  ⚠️  MOBI generation failed (non-fatal)")
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    print(f"✓ Done: {safe_title} ({lang_suffix})")
    return epub_path, pdf_path, mobi_path


def main():
    parser = argparse.ArgumentParser(
        description="Gera ebook de uma única palestra (útil para revisão de tradução).",
        epilog="Exemplo: python3 scripts/generate_ebook.py --lecture 2 --lang pt"
    )
    parser.add_argument("--lecture", type=int, required=True, help="Número da palestra (1-16)")
    parser.add_argument("--lang", choices=["en", "pt"], required=True, help="Idioma")
    parser.add_argument("--output", type=Path, default=Path("dist/ebooks"), help="Diretório de saída")
    
    args = parser.parse_args()
    
    generate_ebook(args.lecture, args.lang, args.output)


if __name__ == "__main__":
    main()