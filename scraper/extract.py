"""Parse a single XSL stylesheet and extract field references."""

from __future__ import annotations

import re
from pathlib import Path

from lxml import etree

from .common import classify_field

XSL_NS = "http://www.w3.org/1999/XSL/Transform"
NAMESPACES = {"xsl": XSL_NS}


def _find_root_variable(tree: etree._ElementTree) -> str | None:
    """Find the variable/param name that selects from $RtnDoc/.

    Looks for patterns like:
      <xsl:param name="FormData" select="$RtnDoc/IRS1040"/>
    Returns the variable name (e.g. "FormData") or None.
    """
    for tag in ("param", "variable"):
        for elem in tree.iter(f"{{{XSL_NS}}}{tag}"):
            select = elem.get("select", "")
            if "$RtnDoc/" in select:
                return elem.get("name")
    return None


def _extract_select_paths(tree: etree._ElementTree, var_name: str) -> list[str]:
    """Extract all TargetNode select= paths referencing the given variable.

    Collects the raw XPath strings from attributes like:
      select="$FormData/TaxableIncomeAmt"
      select="$FormData/BusinessForeignAddress/CityNm"
    """
    prefix = f"${var_name}/"
    paths: set[str] = set()

    for elem in tree.iter():
        select = elem.get("select") or ""
        if select.startswith(prefix):
            raw = select[len(prefix) :]
            # Strip any trailing predicates like [1] or position qualifiers
            raw = re.sub(r"\[.*?\]", "", raw)
            # Strip any trailing /text() or /count() etc.
            raw = re.sub(r"/(text|count|number|string)\(\)$", "", raw)
            # Strip trailing arithmetic/comparison expressions (e.g. " * -1", " = ''")
            raw = re.sub(r"\s*[*+=<>!].*$", "", raw)
            # Strip leading/trailing whitespace
            raw = raw.strip()
            # Strip @ prefix (XPath attribute selectors)
            raw = raw.lstrip("@")
            if raw and not raw.startswith("$") and raw != "child::*":
                paths.add(raw)

    return sorted(paths)


def _path_to_field(path: str) -> dict:
    """Convert a dotted XPath to a field dict."""
    name = path.rsplit("/", 1)[-1]
    return {
        "name": name,
        "path": path,
        "type": classify_field(name),
    }


def extract_form(xsl_path: Path) -> dict | None:
    """Parse an XSL file and return structured form data.

    Returns a dict like:
      {"form_id": "IRS1040", "tax_year": 2025, "fields": [...]}
    or None if the file cannot be parsed.
    """
    try:
        tree = etree.parse(str(xsl_path))
    except etree.XMLSyntaxError:
        return None

    var_name = _find_root_variable(tree)
    if var_name is None:
        return None

    # Derive form_id from the $RtnDoc/XXX select
    form_id = None
    for tag in ("param", "variable"):
        for elem in tree.iter(f"{{{XSL_NS}}}{tag}"):
            select = elem.get("select", "")
            if "$RtnDoc/" in select:
                form_id = select.split("$RtnDoc/")[-1]
                # Strip any trailing predicates
                form_id = re.sub(r"\[.*", "", form_id)
                break
        if form_id:
            break

    if not form_id:
        return None

    # Derive tax_year from parent directory name
    tax_year = None
    for part in xsl_path.parts:
        if re.match(r"^20\d{2}$", part):
            tax_year = int(part)
            break
    if tax_year is None:
        tax_year = 2025

    paths = _extract_select_paths(tree, var_name)
    fields = [_path_to_field(p) for p in paths]

    return {
        "form_id": form_id,
        "tax_year": tax_year,
        "fields": fields,
    }
