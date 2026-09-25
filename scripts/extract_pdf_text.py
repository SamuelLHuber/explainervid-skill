#!/usr/bin/env python3
"""Best-effort PDF text extraction helper.

Usage:
  python scripts/extract_pdf_text.py paper.pdf > paper.txt

Installs no dependencies by itself. It tries pypdf first, then pdftotext if available.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: extract_pdf_text.py <pdf>", file=sys.stderr)
        return 2
    pdf = Path(sys.argv[1])
    if not pdf.is_file():
        print(f"Missing PDF: {pdf}", file=sys.stderr)
        return 1
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(str(pdf))
        for i, page in enumerate(reader.pages, 1):
            print(f"\n\n--- page {i} ---\n")
            print(page.extract_text() or "")
        return 0
    except Exception as e:
        if not shutil.which("pdftotext"):
            print(f"pypdf failed ({e}) and pdftotext is unavailable", file=sys.stderr)
            return 1
    subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
