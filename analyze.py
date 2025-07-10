#!/usr/bin/env python3
import fitz
import re
import sys
from pathlib import Path
import argparse

def analyze(pdf_path):
    """
    Analyze PDFs for word count, figure captions, embedded images,
    GitHub links, and references.
    """
    doc = fitz.open(pdf_path)
    raw_text = ""
    image_count = 0
    doi_set = set()

    for page in doc:
        page_text = page.get_text() or ""
        raw_text += page_text
        image_count += len(page.get_images(full=True))
        # DOIs
        for link in page.get_links():
            uri = link.get('uri', '')
            if uri and 'doi.org' in uri.lower():
                doi_set.add(uri)

    # Stubborn GitHub detection
    text = re.sub(r"\s+", " ", raw_text)
    text = re.sub(r"(https?://github\.com/) ", r"\1", text, flags=re.IGNORECASE)

    # Words count
    words = len(text.split())

    # Figs captions
    figure_labels = re.findall(r'Figure\s+(\d+)', text, flags=re.IGNORECASE)
    distinct_figs = sorted(set(figure_labels), key=int)

    # GitHub links
    github_links = re.findall(r'https?://github\.com/[\w\-\./]+', text, flags=re.IGNORECASE)

    # References (via DOIs; still not that suceessful)
    reference_count = 0
    # text-based DOIs after Refs
    ref_start = re.search(r'^\s*References\s*$', raw_text, flags=re.IGNORECASE | re.MULTILINE)
    if ref_start:
        section = raw_text[ref_start.end():]
        doi_text = set(re.findall(r'doi\.org/[\w\./-]+', section, flags=re.IGNORECASE))
        # if https is missing
        doi_text = {('https://' + doi) if not doi.lower().startswith('http') else doi for doi in doi_text}
        doi_set.update(doi_text)
    reference_count = len(doi_set)

    return {
        "file": str(pdf_path),
        "word_count": words,
        "figure_caption_count": len(distinct_figs),
        "embedded_image_count": image_count,
        "reference_count": reference_count,
        "github_links": github_links,
        "figures": distinct_figs
    }


def format_results(results):
    lines = []
    for res in results:
        lines.append(f"File: {res['file']}")
        lines.append(f"  Words: {res['word_count']}")
        lines.append(f"  Figure captions: {res['figure_caption_count']} (Figures {', '.join(res['figures']) or 'None'})")
        lines.append(f"  Embedded images: {res['embedded_image_count']}")
        lines.append(f"  References (DOIs): {res['reference_count']}")
        if res['github_links']:
            lines.append("  GitHub links:")
            for link in res['github_links']:
                lines.append(f"    - {link}")
        else:
            lines.append("  GitHub links: None")
        lines.append("")
    return "\n".join(lines)


def gather_pdfs(inputs):
    pdfs = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            pdfs.extend(p.rglob("*.pdf"))
        elif p.is_file() and p.suffix.lower() == ".pdf":
            pdfs.append(p)
        else:
            print(f"Warning: {p!s} is not a PDF or directory, skipping.", file=sys.stderr)
    return sorted(set(pdfs))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze one or more PDFs or folders of PDFs.")
    parser.add_argument(
        "paths", nargs="+",
        help="PDF files or directories (scans recursively)")
    parser.add_argument(
        "-o", "--output",
        help="Write formatted report to this text file")
    args = parser.parse_args()

    pdf_files = gather_pdfs(args.paths)
    if not pdf_files:
        print("No PDFs found. Exiting.", file=sys.stderr)
        sys.exit(1)

    results = [analyze(pdf) for pdf in pdf_files]
    report = format_results(results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
