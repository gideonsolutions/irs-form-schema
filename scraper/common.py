"""Constants, suffix→type mapping, and download helpers."""

import io
import tempfile
import zipfile
from pathlib import Path

import requests

IRS_SCHEMA_BASE_URL = "https://www.irs.gov/pub/irs-schema"
DEFAULT_ZIP = "py2026r1.zip"

SUFFIX_TYPE_MAP = {
    "Amt": "usd",
    "Ind": "bool",
    "Cd": "enum",
    "Txt": "string",
    "Nm": "string",
    "Desc": "string",
    "Cnt": "int",
    "Num": "string",
    "Dt": "date",
    "SSN": "tin",
    "EIN": "ein",
    "PIN": "string",
    "Pct": "decimal",
    "Rt": "decimal",
    "Grp": "group",
}


def classify_field(name: str) -> str:
    """Classify a field name by its suffix. Returns the type string."""
    for suffix, field_type in SUFFIX_TYPE_MAP.items():
        if name.endswith(suffix):
            return field_type
    return "unknown"


def download_and_extract(zip_name: str = DEFAULT_ZIP, dest: Path | None = None) -> Path:
    """Download an IRS MeF schema zip and extract to a temp directory.

    Returns the path to the extraction directory.
    """
    url = f"{IRS_SCHEMA_BASE_URL}/{zip_name}"
    print(f"Downloading {url} ...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    if dest is None:
        dest = Path(tempfile.mkdtemp(prefix="irs_mef_"))

    print(f"Extracting to {dest} ...")
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        zf.extractall(dest)

    return dest
