#!/usr/bin/env python3
import fitz
import re
import sys
from pathlib import Path
import argparse

def analyze(pdf_path):
    """
    Analyze pdfs for:
    - Title 
    - Word count excluding first page, references section, figure captions, line numbers
    - Figure count (captions)
    - Embedded image count
    - GitHub links from entire document
    - Reference count (DOI occurrences in the References section; not that successful but still useful)
    """
    doc = fitz.open(pdf_path)
    raw_pages = []
    image_counts = []

    # Extract text and image count per page
    for i, page in enumerate(doc):
        page_text = page.get_text() or ""
        raw_pages.append(page_text)
        image_counts.append(len(page.get_images(full=True)))

    # Title: second line of first page
    title = ""
    if raw_pages:
        lines = [ln.strip() for ln in raw_pages[0].splitlines() if ln.strip()]
        if len(lines) >= 2:
            title = lines[1] + '...'

    # Detect refs
    ref_start = None
    ref_end = None
    for idx, text in enumerate(raw_pages):
        if ref_start is None and re.search(r'^\s*References\s*$', text, flags=re.IGNORECASE | re.MULTILINE):
            ref_start = idx
        elif ref_start is not None and re.match(r'^[A-Z][A-Z\s]+$', text.strip()):
            ref_end = idx
            break
    if ref_start is not None and ref_end is None:
        ref_end = len(raw_pages)

    # Body pages: exclude first page and reference pages
    body_pages = [raw_pages[i] for i in range(1, len(raw_pages))
                  if not (ref_start is not None and ref_start <= i < ref_end)]

    # Main text: no line numbers and figure caption lines
    body_text = "\n".join(body_pages)
    body_text = re.sub(r'(?m)^\s*\d+\s+', '', body_text)  # strip line numbers
    body_text = re.sub(r'(?m)^\s*(?:Figure|Fig\.)\s*\d+.*$', '', body_text)  # strip captions
    norm_text = re.sub(r"\s+", " ", body_text)  # normalize whitespace
    # Rejoin split GitHub URLs
    norm_text = re.sub(r"(https?://github\.com/) ", r"\1", norm_text, flags=re.IGNORECASE)

    # Word count
    word_count = len(norm_text.split())

    # Figure count (captions)
    figure_count = sum(
        len(re.findall(r'(?:Figure|Fig\.)\s*\d+', raw_pages[i], flags=re.IGNORECASE))
        for i in range(1, len(raw_pages))
        if not (ref_start is not None and ref_start <= i < ref_end)
    )

    # Embedded image count
    embedded_images = sum(
        image_counts[i]
        for i in range(1, len(raw_pages))
        if re.search(r'(?:Figure|Fig\.)\s*\d+', raw_pages[i], flags=re.IGNORECASE)
        and not (ref_start is not None and ref_start <= i < ref_end)
    )

    # GitHub links (full document)
    full_text = " ".join(raw_pages)
    full_text = re.sub(r"(https?://github\.com/) ", r"\1", full_text, flags=re.IGNORECASE)
    github_links = re.findall(r'https?://github\.com/[\w\-\./]+', full_text, flags=re.IGNORECASE)

    # DOI count from references section
    doi_count = 0
    if ref_start is not None:
        ref_text = "\n".join(raw_pages[ref_start:ref_end])
        dois_txt = re.findall(r'doi\.org/[\w\./-]+', ref_text, flags=re.IGNORECASE)
        doi_annot = []
        for page in doc[ref_start:ref_end]:
            for link in page.get_links():
                uri = link.get('uri', '')
                if uri and 'doi.org' in uri.lower():
                    doi_annot.append(uri)
        doi_count = len(set(dois_txt + doi_annot))

    return {
        'file': str(pdf_path),
        'title': title,
        'word_count': word_count,
        'figure_count': figure_count,
        'embedded_image_count': embedded_images,
        'reference_count': doi_count,
        'github_links': github_links
    }

def format_results(results):
    lines = []
    for res in results:
        lines.append(f"File: {res['file']}")
        lines.append(f"Title: {res['title']}")
        lines.append(f"  Words: {res['word_count']}")
        lines.append(f"  Figures: {res['figure_count']}")
        lines.append(f"  Embedded images: {res['embedded_image_count']}")
        lines.append(f"  References (DOIs): {res['reference_count']}")
        if res['github_links']:
            lines.append("  GitHub links:")
            for link in res['github_links']:
                lines.append(f"    - {link}")
        else:
            lines.append("  GitHub links: None")
        lines.append("")
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
        'paths', nargs='+',
        help='PDF files or directories (scans recursively)')
    parser.add_argument(
        '-o', '--output',
        help='Write formatted report to this text file')
    args = parser.parse_args()

    pdf_files = gather_pdfs(args.paths)
    if not pdf_files:
        print("No PDFs found. Exiting.", file=sys.stderr)
        sys.exit(1)

    results = [analyze(pdf) for pdf in pdf_files]
    report = format_results(results)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)

if __name__ == '__main__':
    main()
