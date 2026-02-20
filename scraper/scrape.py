"""Main entry point: download MeF package, extract fields, write JSON."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from .common import DEFAULT_ZIP, download_and_extract
from .extract import extract_form

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def scrape(
    zip_name: str = DEFAULT_ZIP,
    tax_year: int = 2025,
    output_dir: Path | None = None,
) -> None:
    """Download the IRS MeF zip, extract all form schemas, and write JSON."""
    if output_dir is None:
        output_dir = DATA_DIR / str(tax_year)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download and extract
    tmp_dir = download_and_extract(zip_name)

    try:
        _process(tmp_dir, tax_year, output_dir)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _process(tmp_dir: Path, tax_year: int, output_dir: Path) -> None:
    """Process extracted files and write JSON output."""
    # Find XSL files for the target tax year only
    # Structure: PY2026R8/mef/Stylesheets/<year>/IRS*.xsl
    xsl_files: list[Path] = []
    for pattern_dir in tmp_dir.rglob(f"{tax_year}/IRS*.xsl"):
        if not pattern_dir.name.endswith("Style.xsl"):
            xsl_files.append(pattern_dir)

    print(f"Found {len(xsl_files)} IRS XSL files")

    index: dict[str, dict] = {}
    forms_written = 0

    for xsl_path in sorted(xsl_files):
        result = extract_form(xsl_path)
        if result is None:
            continue

        form_id = result["form_id"]
        field_count = len(result["fields"])

        # Write per-form JSON
        out_path = output_dir / f"{form_id}.json"
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)

        index[form_id] = {"field_count": field_count, "file": f"{form_id}.json"}
        forms_written += 1

    # Write index
    index_data = {
        "tax_year": tax_year,
        "form_count": len(index),
        "forms": dict(sorted(index.items())),
    }
    with open(output_dir / "_index.json", "w") as f:
        json.dump(index_data, f, indent=2)

    print(f"Wrote {forms_written} form JSONs to {output_dir}")
    print(f"Index written to {output_dir / '_index.json'}")


if __name__ == "__main__":
    scrape()
