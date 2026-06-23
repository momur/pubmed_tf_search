"""
EDA_pubmed_search.py
--------------------
Parse a PubMed search result saved in MEDLINE (.txt) format and extract
PMID, Title, and Abstract into a CSV file.

Usage:
    1. Run your search on https://pubmed.ncbi.nlm.nih.gov/
    2. Click "Save" → Format: PubMed → "Save" (downloads a .txt file)
    3. Set INPUT_FILE and OUTPUT_CSV below, then run:
           python EDA_pubmed_search.py

The output CSV is used by biopython_search.py to count TF occurrences.
"""

import argparse
import pandas as pd
from Bio import Medline
from tqdm import tqdm


def parse_pubmed_file(input_file: str) -> list[dict]:
    """
    Parse a PubMed MEDLINE export file and return a list of dicts
    with keys: PMID, Title, Abstract.

    Args:
        input_file: Path to the .txt file downloaded from PubMed.

    Returns:
        List of dicts, one per record.
    """
    records = []
    with open(input_file, encoding="utf-8") as f:
        for pmid in tqdm(Medline.parse(f), desc="Parsing records"):
            records.append({
                "PMID":     pmid.get("PMID", ""),
                "Title":    pmid.get("TI", ""),
                "Abstract": pmid.get("AB", ""),
            })
    return records


def main():
    parser = argparse.ArgumentParser(
        description="Parse a PubMed MEDLINE export and save PMID/Title/Abstract to CSV."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to PubMed .txt export (MEDLINE format)",
    )
    parser.add_argument(
        "--output", "-o",
        default="pubmed_results.csv",
        help="Output CSV file path (default: pubmed_results.csv)",
    )
    args = parser.parse_args()

    records = parse_pubmed_file(args.input)
    df = pd.DataFrame(records)
    df.to_csv(args.output, index=False)

    print(f"Saved {len(df)} records to {args.output}")
    print(df.head())


if __name__ == "__main__":
    main()
