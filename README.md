# PDF Analyzer

A command-line tool to inspect PDF files for:

- **Word count**
- **Figure captions**
- **Embedded images**
- **GitHub links**
- **DOI references**

---

## 📦 Usage

```bash
python analyze.py path/to/folder_with_PDFs -o report.txt
```

For **Windows users**:  
Run the `run.bat` file located in the same folder as `analyze.py`, and make sure your PDFs are placed in the `pdf_folder` subfolder.

---

## 📁 Folder Structure

```
project_root/
├── analyze.py
├── run.bat
├── environment.yml
└── pdf_folder/
    ├── document1.pdf
    ├── document2.pdf
    ├── document3.pdf
    └── ...
```

---

## 🛠️ Installation (with Conda)

```bash
conda env create -f environment.yml
conda activate pdfenv
```

---

## ✅ Requirements

All dependencies are listed in `environment.yml`.

---

## 📄 License

This project is licensed under the MIT License.
