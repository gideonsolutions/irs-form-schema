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

Both abbreviated and full-word suffixes are recognized:

| Suffix | Type | Description |
|--------|------|-------------|
| `Amt`, `Amount` | `usd` | Dollar amount |
| `Ind`, `Indicator` | `bool` | Checkbox / indicator |
| `Cd`, `Typ` | `enum` | Code / enumeration |
| `Txt` | `string` | Free text |
| `Nm`, `Name` | `string` | Name |
| `Desc`, `Dsc` | `string` | Description |
| `Address` | `string` | Mailing / foreign address |
| `Num`, `Number` | `string` | Numeric identifier |
| `PIN` | `string` | Personal Identification Number |
| `Cnt`, `Qty` | `int` | Count / quantity |
| `Dt` | `date` | Date |
| `Yr` | `year` | Tax or calendar year |
| `SSN` | `tin` | Social Security Number |
| `EIN` | `ein` | Employer Identification Number |
| `Pct` | `decimal` | Percentage |
| `Rt` | `decimal` | Rate |
| `Grp`, `Dtl`, `Detail`, `Info`, `Information` | `group` | Nested element group |

Fields with no recognized suffix are classified as `unknown` (~2% of all fields). These are typically domain-specific terms like `Property`, `Partnerships`, or `Losses` where the ending is part of the tax vocabulary rather than a type indicator.

## Repo structure

```
irs-form-schema/
├── scraper/
│   ├── common.py          # Constants, suffix→type mapping, download helpers
│   ├── extract.py         # Parse XSL files → extract field references per form
│   └── scrape.py          # Main entry point: download, extract, classify, write
├── data/
│   ├── 2023/              # TY2023 — 389 forms
│   ├── 2024/              # TY2024 — 402 forms
│   └── 2025/              # TY2025 — 415 forms
│       └── _index.json    # Summary of all forms (per year)
├── requirements.txt
├── LICENSE
└── README.md
```

## License

Apache-2.0
