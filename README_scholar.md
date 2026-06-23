# PubMed TF Mention Counter

A lightweight Python toolkit to count how often human transcription factors (TFs)
are mentioned across a set of PubMed abstracts. Useful for quickly gauging the
research landscape around any gene list in a disease or biological context.

```
PubMed search (.txt export)
        │
        ▼
  EDA_pubmed_search.py  →  pubmed_results.csv  (PMID, Title, Abstract)
        │
        ▼
  biopython_search.py   →  tf_counts.csv  (TF, Count)
```

## Example use case

> "How many schizophrenia papers from 1999–2025 mention each of the 1,472 human TFs
> from TFCheckpoint?"

## Requirements

```bash
pip install biopython pandas tqdm
```

## Usage

### Step 1 — Export your PubMed search

1. Run your search on [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
2. Click **Save** → Format: **PubMed** → **Save** (downloads a `.txt` file)

### Step 2 — Parse the export to CSV

```bash
python EDA_pubmed_search.py \
    --input  ~/Downloads/schizophrenia_brain.txt \
    --output pubmed_schizophrenia_1999_2025.csv
```

### Step 3 — Count TF mentions

```bash
python biopython_search.py \
    --tf-list  humanTF_from_tfcheckpoint_1472.csv \
    --abstracts pubmed_schizophrenia_1999_2025.csv \
    --output    tf_counts_schizophrenia.csv
```

The TF list (`humanTF_from_tfcheckpoint_1472.csv`) should have a column named
`HumanTF` containing gene symbols. Download it from
[TFCheckpoint](http://tfcheckpoint.org/). Use `--tf-col <column>` if your file
uses a different column name.

## Output

| TF | Count |
|---|---|
| TP53 | 847 |
| STAT3 | 612 |
| ... | ... |

`Count` = number of abstracts in which the TF appeared (not total mentions).

## Files

| File | Description |
|---|---|
| `EDA_pubmed_search.py` | Parse PubMed MEDLINE export → CSV |
| `biopython_search.py` | Count TF occurrences in abstracts |
| `google_scholar.ipynb` | Exploratory notebook (Google Scholar via scholarly) |

## Notes

- Matching is case-aware: detects both `TP53` (uppercase) and `Tp53` (title-case)
- Each TF is counted once per abstract regardless of how many times it appears
- For large datasets, the pre-compiled regex approach in `biopython_search.py`
  is significantly faster than the naive per-abstract compile approach
