# PDF Analyzer

CLI tool to inspect PDFs for:
- Word count
- Figure captions
- Embedded images
- GitHub links
- DOI references

## Installation (Conda)

```bash
conda env create -f environment.yml
conda activate pdfenv

## Usage
python analyze.py path/to/folder_or_file -o report.txt
