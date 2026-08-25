---
name: documents
description: Use when working with complex file formats including Word documents (.docx), PDFs (.pdf), PowerPoint presentations (.pptx), and Excel spreadsheets (.xlsx). Handles reading, summarising, extracting data, converting, and analysing these file types.
---

You are helping the user work with document files. Follow these guidelines based on file type:

## PDF (.pdf)

Classify first, then route. Detection costs ~20ms and tells you which path is valid:

```bash
python -c "import pdf_inspector as p; r=p.detect_pdf(r'file.pdf'); print(r.pdf_type, r.confidence, r.page_count, r.pages_needing_ocr[:10])"
```

### text_based → pdf-inspector (default path)

```bash
python -c "import pdf_inspector as p; print(p.process_pdf(r'file.pdf').markdown)"
```

- 15-20x faster than markitdown and far more structurally stable (measured: 240-page TIA in 6.8s vs 105s; 190 headings recovered vs 9)
- `process_pdf(path, pages=[1,3,5])` to limit pages; `extract_pages_markdown` for per-page output
- `extract_text_with_positions(path, pages=[0])` gives x/y/font/size/bold per text item. Use this for fixed-layout reports (system exports, survey sheets) instead of parsing flattened text
- `extract_text_in_regions(path, page_regions)` for bounding-box extraction
- Check `res.has_encoding_issues` — if True the font decoding is broken, fall back to the Read tool

### scanned / image_based → Read tool (vision)

pdf-inspector has no OCR and returns `markdown = None` for these. Drawings, plans, aerials and scanned surveys all classify as `image_based`.

- Read supports `pages` (e.g. pages: "1-5"), max 20 pages per call, chunk larger documents
- Requires poppler (`pdftoppm`) on PATH. Installed on this machine via `winget install --id oschwartz10612.Poppler --scope user` (v25.07.0). Do NOT use `conda install` here: `C:\ProgramData\anaconda3` is not user-writable and it fails without admin.
- If Read errors with "pdftoppm is not installed" despite the above, Claude Code is holding a stale PATH snapshot. Restart Claude Code; the binary is at `%LOCALAPPDATA%\Microsoft\WinGet\Packages\oschwartz10612.Poppler_*\poppler-25.07.0\Library\bin`

### mixed

Extract the text pages with pdf-inspector, then Read only the page numbers listed in `pages_needing_ocr`.

### Known extraction artefacts (verified on real files)

- **Nested sub-columns collapse.** Classified count sheets (CIC) with LIGHT/RIGID/A.HEAVY/Σ under one movement come through as one cell of space-separated values, e.g. `|175 10 0 185|`. Consistent and re-splittable, but you must split it yourself. Do not read those as single figures.
- **Page-break continuation tables.** A table continuing across a page break loses its header, and the first data row is promoted to the header with a separator under it. Check row 1 of any table that starts mid-page. markitdown has the identical fault, so this is not a reason to switch back.
- Cross-check any figure that will land in a deliverable against the source page.

### markitdown

Only when pdf-inspector fails outright. It fragments tables badly (335 table starts for 1328 rows on the TIA, vs 135 starts for 1667 rows) and orphans values onto their own lines, which silently detaches numbers from their row.

## Word (.docx)
- Use the Bash tool with Python to extract content:
  ```bash
  python -c "import docx; doc=docx.Document('file.docx'); [print(p.text) for p in doc.paragraphs]"
  ```
- If python-docx is not installed: `pip install python-docx`
- For tables: iterate `doc.tables` and access `table.rows[i].cells[j].text`

## Excel (.xlsx)
- Use the Bash tool with Python and pandas or openpyxl:
  ```bash
  python -c "import pandas as pd; df=pd.read_excel('file.xlsx', sheet_name=None); print(df)"
  ```
- If not installed: `pip install pandas openpyxl`
- For multiple sheets use `sheet_name=None` to load all sheets as a dict
- For large files, read specific columns or rows to avoid memory issues

## PowerPoint (.pptx)
- Use the Bash tool with Python and python-pptx:
  ```bash
  python -c "from pptx import Presentation; prs=Presentation('file.pptx'); [print(shape.text) for slide in prs.slides for shape in slide.shapes if hasattr(shape, 'text')]"
  ```
- If not installed: `pip install python-pptx`
- Access slide notes via `slide.notes_slide.notes_text_frame.text`
- Access tables via `shape.table` when `shape.has_table` is True

## General approach
1. Identify the file type from the extension
2. Check if required Python libraries are installed before using them
3. For analysis tasks: extract content first, then analyse
4. For large files: summarise section by section
5. Always show the user extracted content before drawing conclusions
6. If the user wants to convert formats, use the appropriate library to write output

## Common tasks
- **Summarise**: Extract all text, then provide a structured summary
- **Extract tables**: Use pandas for Excel, iterate `.tables` for Word/PowerPoint
- **Compare documents**: Read both files, then diff content
- **Find specific info**: Extract full text first, then search/filter

$ARGUMENTS
