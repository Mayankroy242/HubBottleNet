import pandas as pd
import re
from difflib import SequenceMatcher


# ---------------------------------------------------------
# Standard column names and known aliases
# ---------------------------------------------------------

COLUMN_ALIASES = {

    "node": [
        "node",
        "gene",
        "gene name",
        "gene symbol",
        "protein",
        "protein name",
        "target",
        "symbol"
    ],

    "degree": [
        "degree",
        "node degree",
        "connectivity",
        "number of neighbors",
        "number of neighbours"
    ],

    "bc": [
        "bc",
        "b c",
        "betweenness",
        "betweenness centrality",
        "betweeness centrality"
    ],

    "cc": [
        "cc",
        "c c",
        "closeness",
        "closeness centrality",
        "clossness centrality"
    ],

    "clustering_coefficient": [
        "clustering",
        "clustering coefficient",
        "clustering coefficients"
    ],

    "neighborhood_connectivity": [
        "neighborhood connectivity",
        "neighbourhood connectivity",
        "neighborhood conectivity",
        "neighbourhood conectivity",
        "connectivity"
    ],

    "undirected_edges": [
        "no of undirected edges",
        "no of undirected edge",
        "number of undirected edges",
        "undirected edges",
        "undirected edge"
    ],

    "radiality": [
        "radiality"
    ],

    "topological_coefficient": [
        "topological coefficient",
        "topological coefficients",
        "topological cefficient",
        "topological cefficients"
    ]
}


# ---------------------------------------------------------
# Column name normalization
# ---------------------------------------------------------

def normalize_column_name(name):
    """
    Normalize column names to make matching tolerant
    to capitalization, punctuation, underscores and
    repeated spaces.
    """

    name = str(name).strip().lower()

    # Replace underscores and hyphens with spaces
    name = re.sub(r"[_\-]+", " ", name)

    # Remove punctuation
    name = re.sub(r"[^a-z0-9\s]", "", name)

    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name).strip()

    return name


def clean_column_names(df):
    """Clean and normalize Excel/CSV column names."""

    df = df.copy()

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    return df


# ---------------------------------------------------------
# Similarity calculation
# ---------------------------------------------------------

def similarity(a, b):
    """Calculate similarity between two strings."""

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


# ---------------------------------------------------------
# Column detection
# ---------------------------------------------------------

def detect_columns(df, fuzzy_threshold=0.85):
    """
    Detect NetworkAnalyzer columns.

    Matching strategy:

    1. Exact alias matching
    2. Known typo/variant matching
    3. Fuzzy matching for highly similar names
    """

    detected = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

        # Normalize aliases
        normalized_aliases = [
            normalize_column_name(alias)
            for alias in aliases
        ]

        # -------------------------------------------------
        # Exact matching
        # -------------------------------------------------

        exact_matches = [
            column
            for column in df.columns
            if column in normalized_aliases
        ]

        if len(exact_matches) == 1:

            detected[standard_name] = exact_matches[0]

            print(
                f"✓ {standard_name} → "
                f"{exact_matches[0]} (exact)"
            )

            continue

        elif len(exact_matches) > 1:

            raise ValueError(
                f"Multiple possible columns detected for "
                f"{standard_name}: {exact_matches}"
            )

        # -------------------------------------------------
        # Fuzzy matching
        # -------------------------------------------------

        candidates = []

        for column in df.columns:

            best_score = max(
                similarity(column, alias)
                for alias in normalized_aliases
            )

            if best_score >= fuzzy_threshold:

                candidates.append(
                    (column, best_score)
                )

        # Sort by similarity
        candidates.sort(
            key=lambda x: x[1],
            reverse=True
        )

        if len(candidates) >= 1:

            best_column, best_score = candidates[0]

            # Check ambiguity
            if (
                len(candidates) > 1
                and candidates[1][1] >= best_score - 0.03
            ):

                raise ValueError(
                    f"Ambiguous column detection for "
                    f"{standard_name}. Candidates: "
                    f"{candidates}"
                )

            detected[standard_name] = best_column

            print(
                f"✓ {standard_name} → "
                f"{best_column} "
                f"(fuzzy: {best_score:.2f})"
            )

    return detected


# ---------------------------------------------------------
# Dataset standardization
# ---------------------------------------------------------

def standardize_dataset(df, detected):
    """Create standardized topology dataframe."""

    standardized_df = pd.DataFrame()

    for standard_name, original_name in detected.items():

        standardized_df[standard_name] = (
            df[original_name]
        )

    return standardized_df


# ---------------------------------------------------------
# File loading
# ---------------------------------------------------------

def load_file(file_path):
    """
    Load Excel or CSV input automatically.
    """

    file_path = str(file_path).lower()

    if file_path.endswith(".xlsx"):

        return pd.read_excel(file_path)

    elif file_path.endswith(".csv"):

        return pd.read_csv(file_path)

    else:

        raise ValueError(
            "Unsupported file format. "
            "Please provide a .xlsx or .csv file."
        )


def load_and_standardize(file_path):
    """
    Load Excel/CSV file, detect topology parameters,
    and return standardized dataset.
    """

    df = load_file(file_path)

    print(
        f"✓ Input file loaded: {file_path}"
    )

    df = clean_column_names(df)

    detected = detect_columns(df)

    standardized_df = standardize_dataset(
        df,
        detected
    )

    return standardized_df, detected
