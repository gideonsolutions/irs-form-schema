# irs-form-schema

Machine-readable field definitions for IRS tax forms, extracted from the IRS MeF (Modernized e-File) XSL stylesheets.

## What this does

The IRS publishes MeF packages containing XSL stylesheets for every tax form. These stylesheets reference XML elements with a consistent naming convention that encodes field types via suffixes (`Amt` = USD, `Ind` = boolean, `Cd` = enum, etc.). This project extracts all field definitions from these stylesheets into structured JSON.

## Quick start

```bash
pip install -r requirements.txt
python -m scraper.scrape            # TY2025 (default)
```

To scrape a different tax year:

```python
from scraper.scrape import scrape
scrape(tax_year=2024)
```

The zip filename is derived automatically as `py{tax_year+1}r1.zip`.

## Output format

Each form gets a JSON file like `data/2025/IRS1040.json`:

```json
{
  "form_id": "IRS1040",
  "tax_year": 2025,
  "fields": [
    {
      "name": "TaxableIncomeAmt",
      "path": "TaxableIncomeAmt",
      "type": "usd"
    },
    {
      "name": "Primary65OrOlderInd",
      "path": "Primary65OrOlderInd",
      "type": "bool"
    },
    {
      "name": "CityNm",
      "path": "BusinessForeignAddress/CityNm",
      "type": "string"
    }
  ]
}
```

An `_index.json` file lists all forms with their field counts.

## Type classification

| Suffix | Type | Description |
|--------|------|-------------|
| `Amt` | `usd` | Dollar amount |
| `Ind` | `bool` | Checkbox / indicator |
| `Cd` | `enum` | Code / enumeration |
| `Txt` | `string` | Free text |
| `Nm` | `string` | Name |
| `Desc` | `string` | Description |
| `Cnt` | `int` | Count |
| `Num` | `string` | Numeric identifier |
| `Dt` | `date` | Date |
| `SSN` | `tin` | Social Security Number |
| `EIN` | `ein` | Employer Identification Number |
| `PIN` | `string` | Personal Identification Number |
| `Pct` | `decimal` | Percentage |
| `Rt` | `decimal` | Rate |
| `Grp` | `group` | Nested element group |

Fields with no recognized suffix are classified as `unknown`.

## Repo structure

```
irs-form-schema/
├── scraper/
│   ├── common.py          # Constants, suffix→type mapping, download helpers
│   ├── extract.py         # Parse XSL files → extract field references per form
│   └── scrape.py          # Main entry point: download, extract, classify, write
├── data/
│   ├── 2023/              # TY2023 — 387 forms
│   ├── 2024/              # TY2024 — 398 forms
│   └── 2025/              # TY2025 — 411 forms
│       └── _index.json    # Summary of all forms (per year)
├── requirements.txt
├── LICENSE
└── README.md
```

## License

Apache-2.0
