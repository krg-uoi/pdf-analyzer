# PDF Analyzer

CLI tool to inspect PDFs for:
- Word count
- Figure captions
- Embedded images
- GitHub links
- DOI references


## Usage

python analyze.py path/to/folder_with_PDFs -o report.txt

For windows users: Run the run.bat file located in the same folder as analyze.py, and make sure your PDFs are placed in the pdf_folder subfolder.

## Folders tree
project_root/
├── analyze.py
└── pdf_folder/
    ├── document1.pdf
    ├── document2.pdf
    ├── document3.pdf
    └── ...



## Installation (Conda)

```bash
conda env create -f environment.yml
conda activate pdfenv


