# SAR.pdf_adobeRound1a
Python-based offline PDF outline extractor that uses font size, style, and numbering patterns to generate structured outlines (Title, H1, H2, H3 with page numbers) from any PDF document. Designed for Adobe Hackathon 2025 Round 1A.

Here is a complete `README.md` content tailored for **Round 1A** (PDF Outline Extractor) of the Adobe Hackathon 2025:

---

# PDF Outline Extractor – Adobe Hackathon 2025 (Round 1A)

This project is a lightweight and offline-compatible Python tool to extract structured outlines from PDF documents. The extractor identifies the **document title** and **headings (H1, H2, H3)** using a combination of **textual features** (like numbering patterns) and **visual cues** (font size, boldness, and position).

---

## Features

* Extracts:

  * `Title`
  * `H1`, `H2`, `H3` headings
* Uses both **textual structure** (e.g., numbered headings like `2.1`) and **formatting features** (font size, bold, position).
* Ignores table content, footers, and form fields.
* Works offline under:

  * Time < 10 seconds
  * Memory < 200 MB memory
  * CPU-only environment

---

## Project Structure

```
.
├── app/
│   ├── input/                 # Input PDF files
│   ├── output/                # JSON output files
│   └── extractor.py           # Main outline extraction script
├── README.md
```

---

## Requirements

* Python 3.7+
* Libraries:

  * `PyMuPDF` (fitz)
  * `json`
  * `re`

Install dependencies:

```bash
pip install pymupdf
```

---

## How to Run

1. Place your PDF files in `app/input/`
2. Run the extractor:

```bash
python app/extractor.py
```

3. Output JSON files will be generated in `app/output/`

---

## Output Format

Each file produces a JSON of the form:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Section Title",
      "page": 2
    },
    {
      "level": "H2",
      "text": "Subsection Title",
      "page": 3
    }
  ]
}
```

---

## Logic Summary

* Extracts all text spans with metadata (size, font, bold).
* Computes dominant font sizes to identify heading levels.
* Uses regex to identify numbered headings like `2.1`, `3.2.4`, etc.
* Ignores spans with common form/table keywords (`"name"`, `"date"`, etc.).
* Title is selected based on top font sizes on the first page.

---

## Example Output

For a structured academic-style PDF:

```json
{
  "title": "Overview Foundation Level Extensions",
  "outline": [
    {
      "level": "H1",
      "text": "1. Introduction to Agile Testing",
      "page": 2
    },
    {
      "level": "H2",
      "text": "1.1 Background",
      "page": 2
    }
  ]
}
```

---

## Tested On

* `file01.pdf` – form-style with tables and fields
* `file02.pdf` – structured technical PDF with nested headings
* `file03.pdf`
* `file04.pdf`
* `file05.pdf`

---

## Contact

Built for Adobe Hackathon 2025
For queries, please reach out via GitHub issues.

---
