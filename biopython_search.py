"""
biopython_search.py
-------------------
Count how often each human transcription factor (TF) is mentioned in a
set of PubMed abstracts.

Usage:
    python biopython_search.py \
        --tf-list  humanTF_from_tfcheckpoint_1472.csv \
        --abstracts pubmed_results.csv \
        --output    tf_counts.csv

Input files:
    --tf-list   CSV with a column named 'HumanTF' listing TF gene symbols
                (e.g. from TFCheckpoint: http://tfcheckpoint.org/)
    --abstracts CSV produced by EDA_pubmed_search.py, with an 'Abstract' column

Output:
    CSV with columns [TF, Count] sorted by Count descending.
"""

import argparse
import csv
import re
from collections import Counter

import pandas as pd
from tqdm import tqdm


def build_tf_patterns(tfs: list[str]) -> dict[str, re.Pattern]:
    """
    Pre-compile one regex pattern per TF (matches uppercase or title-case).
    Compiling once up-front is much faster than recompiling per abstract.

    Args:
        tfs: List of TF gene symbols.

    Returns:
        Dict mapping each TF symbol to its compiled pattern.
    """
    patterns = {}
    for tf in tfs:
        pattern = r"\b(?:" + re.escape(tf.upper()) + r"|" + re.escape(tf.capitalize()) + r")\b"
        patterns[tf] = re.compile(pattern)
    return patterns


def find_tfs_in_abstract(abstract: str, patterns: dict[str, re.Pattern]) -> set[str]:
    """
    Return the set of TF names found in a single abstract.

    Args:
        abstract: Abstract text.
        patterns: Pre-compiled TF regex patterns from build_tf_patterns().

    Returns:
        Set of TF names that appear in the abstract.
    """
    if not isinstance(abstract, str) or not abstract.strip():
        return set()
    return {tf for tf, pat in patterns.items() if pat.search(abstract)}


def count_tfs(abstracts: pd.Series, patterns: dict[str, re.Pattern]) -> Counter:
    """
    Count TF occurrences across all abstracts (1 count per abstract per TF).

    Args:
        abstracts: Pandas Series of abstract strings.
        patterns:  Pre-compiled TF patterns.

    Returns:
        Counter mapping TF name → number of abstracts it appeared in.
    """
    tf_counts: Counter = Counter()
    for abstract in tqdm(abstracts.fillna("").astype(str), desc="Scanning abstracts"):
        tf_counts.update(find_tfs_in_abstract(abstract, patterns))
    return tf_counts


def main():
    parser = argparse.ArgumentParser(
        description="Count TF mentions across PubMed abstracts."
    )
    parser.add_argument(
        "--tf-list", "-t",
        required=True,
        help="CSV file with a 'HumanTF' column listing TF gene symbols",
    )
    parser.add_argument(
        "--abstracts", "-a",
        required=True,
        help="CSV file with an 'Abstract' column (output of EDA_pubmed_search.py)",
    )
    parser.add_argument(
        "--output", "-o",
        default="tf_counts.csv",
        help="Output CSV file path (default: tf_counts.csv)",
    )
    parser.add_argument(
        "--tf-col",
        default="HumanTF",
        help="Column name in --tf-list that contains TF symbols (default: HumanTF)",
    )
    args = parser.parse_args()

    # Load TF list
    tf_df = pd.read_csv(args.tf_list)
    tfs = tf_df[args.tf_col].dropna().tolist()
    print(f"Loaded {len(tfs)} TFs from {args.tf_list}")

    # Load abstracts
    df = pd.read_csv(args.abstracts)
    print(f"Loaded {len(df)} records from {args.abstracts}")

    # Build patterns once, then scan
    patterns = build_tf_patterns(tfs)
    tf_counts = count_tfs(df["Abstract"], patterns)

    # Save results sorted by count descending
    with open(args.output, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["TF", "Count"])
        for tf, count in sorted(tf_counts.items(), key=lambda x: -x[1]):
            writer.writerow([tf, count])

    print(f"Saved TF counts to {args.output}")
    print(f"Top 10 TFs:\n{pd.read_csv(args.output).head(10).to_string(index=False)}")


if __name__ == "__main__":
    main()
