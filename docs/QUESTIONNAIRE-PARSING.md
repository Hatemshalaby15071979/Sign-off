# Signoff — Questionnaire Parsing

The client questionnaire (Input A) may be provided in CSV, DOCX, XLSX, or TXT format.

## Supported Formats

| Format | File | Status |
|--------|------|--------|
| CSV | `questionnaire.demo.csv` | Supported |
| DOCX | `questionnaire.demo.docx` | Supported (zipfile + xml.etree only) |
| XLSX | `questionnaire.demo.xlsx` | Supported (requires `[xlsx]` extra) |
| TXT | `questionnaire.demo.txt` | Supported |

## CSV Format

Required columns:
- `qid` — Question ID (unique)
- `exact_text` — Exact question text
- `answer_type` — Answer type
- `qid_source` — Source of question
- `source_path` — Source file path
- `order` — Question order

## DOCX Format

- Parsed via stdlib `zipfile` + `xml.etree.ElementTree`
- No external dependencies
- Extracts questions from the document body

## XLSX Format

- Requires `openpyxl==3.1.5` via `[xlsx]` extra
- Must have a sheet named "Questions"
- Uses same column structure as CSV

## TXT Format

- Plain text parsing
- Extracts questions from plain text

## CLI Usage

```bash
python -m signoff parse-questionnaire --input PATH --out PATH
```

Output format:
```
qid,exact_text,answer_type,qid_source,source_path,order
Q-101,"What is the human review process?",text,client_provided,questionnaire.csv,1
```

## Question Extraction

The parser extracts questions into a structured format with:
- Unique `qid` (e.g., `Q-101`)
- Exact text
- Answer type
- Source tracking

*End of questionnaire parsing document.*