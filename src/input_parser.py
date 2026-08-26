import pandas as pd
import re
from pathlib import Path
from difflib import SequenceMatcher


# ---------------------------------------------------------
# Standard column names and known aliases
# ---------------------------------------------------------

COLUMN_ALIASES = {

    "node": [
    "display name",
    "gene",
    "gene name",
    "gene symbol",
    "protein name",
    "target",
    "symbol",
    "name",
    "node",
    "node name",
    "node id"

    ],

    "degree": [
        "degree",
        "node degree",
        "degree centrality",
        "connectivity",
        "number of neighbors",
        "number of neighbours",
        "number of neighbors of a node",
        "number of neighbours of a node"
    ],

    "bc": [
    "bc",
    "b c",
    "betweenness",
    "betweenness centrality",
    "betweeness centrality",
    "betweennesscentrality"

    ],

    "cc": [
        "cc",
        "c c",
        "closeness",
        "closeness centrality",
        "clossness centrality",
        "closenesscentrality"
    ],

    "clustering_coefficient": [
        "clustering",
        "clustering coefficient",
        "clustering coefficients",
        "clusteringcoefficient"
    ],

    "neighborhood_connectivity": [
        "neighborhood connectivity",
        "neighbourhood connectivity",
        "neighborhood conectivity",
        "neighbourhood conectivity",
        "neighborhoodconnectivity",
        "neighbourhoodconnectivity"
    ],

    "undirected_edges": [
        "no of undirected edges",
        "no of undirected edge",
        "number of undirected edges",
        "undirected edges",
        "undirected edge",
        "number of undirected edge"
    ],

    "radiality": [
        "radiality"
    ],

    "topological_coefficient": [
        "topological coefficient",
        "topological coefficients",
        "topological cefficient",
        "topological cefficients",
        "topologicalcoefficient"
    ],

    "protein_id": [
    "stringdb database identifier",
    "stringdbdatabase identifier",
    "database identifier",
    "protein id",
    "protein identifier",
    "ensembl protein id",
    "ensembl protein identifier"
    ],
}


# ---------------------------------------------------------# Column name normalization
# ---------------------------------------------------------

def normalize_column_name(name):
    """
    Normalize column names to make matching tolerant
    to capitalization, punctuation, underscores,
    hyphens and repeated spaces.
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
    """Clean and normalize dataframe column names."""

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
    Detect NetworkAnalyzer topology columns.

    Matching strategy:

    1. Exact alias matching
    2. Fuzzy matching
    3. Known typo/variant matching

    Unknown NetworkAnalyzer columns are ignored.
    """

    detected = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

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

            # Prefer the first exact alias rather than
            # immediately failing on redundant columns.
            detected[standard_name] = exact_matches[0]

            print(
                f"⚠ Multiple possible columns for "
                f"{standard_name}: {exact_matches}"
            )

            print(
                f"  → Using: {exact_matches[0]}"
            )

            continue

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

        candidates.sort(
            key=lambda x: x[1],
            reverse=True
        )

        if candidates:

            best_column, best_score = candidates[0]

            if (
                len(candidates) > 1
                and candidates[1][1] >= best_score - 0.03
            ):

                print(
                    f"⚠ Ambiguous detection for "
                    f"{standard_name}: {candidates}"
                )

                print(
                    f"  → Using best match: "
                    f"{best_column}"
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
    """
    Create standardized topology dataframe.

    The biological node name is retained as `node`.
    The original STRING/Ensembl identifier is retained
    as `protein_id` when available.
    """

    standardized_df = pd.DataFrame()

    # Preserve standardized columns
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
    Load common network-analysis file formats automatically.

    Supported:
        .csv
        .tsv
        .txt
        .xlsx
        .xls
        .xlsm
        .xlsb
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    extension = path.suffix.lower()

    print(
        f"✓ Detected file format: "
        f"{extension}"
    )

    # -----------------------------------------------------
    # CSV
    # -----------------------------------------------------

    if extension == ".csv":

        return pd.read_csv(
            path,
            sep=None,
            engine="python"
        )

    # -----------------------------------------------------
    # TSV
    # -----------------------------------------------------

    elif extension == ".tsv":

        return pd.read_csv(
            path,
            sep="\t"
        )

    # -----------------------------------------------------
    # TXT
    # -----------------------------------------------------

    elif extension == ".txt":

        return pd.read_csv(
            path,
            sep=None,
            engine="python"
        )

    # -----------------------------------------------------
    # Excel XLSX / XLSM
    # -----------------------------------------------------

    elif extension in [".xlsx", ".xlsm"]:

        return pd.read_excel(
            path,
            engine="openpyxl"
        )

    # -----------------------------------------------------
    # Legacy Excel XLS
    # -----------------------------------------------------

    elif extension == ".xls":

        try:

            return pd.read_excel(
                path,
                engine="xlrd"
            )

        except ImportError:

            raise ImportError(
                "Reading .xls files requires xlrd. "
                "Install it using:\n\n"
                "pip install xlrd"
            )

    # -----------------------------------------------------
    # Excel Binary XLSB
    # -----------------------------------------------------

    elif extension == ".xlsb":

        try:

            return pd.read_excel(
                path,
                engine="pyxlsb"
            )

        except ImportError:

            raise ImportError(
                "Reading .xlsb files requires pyxlsb. "
                "Install it using:\n\n"
                "pip install pyxlsb"
            )

    # -----------------------------------------------------
    # Unsupported
    # -----------------------------------------------------

    else:

        raise ValueError(
            f"Unsupported file format: {extension}\n"
            "Supported formats: "
            ".csv, .tsv, .txt, .xlsx, .xls, .xlsm, .xlsb"
        )


# ---------------------------------------------------------
# Main input pipeline
# ---------------------------------------------------------

def load_and_standardize(file_path):
    """
    Load file, detect topology parameters,
    and return standardized dataset.
    """

    df = load_file(file_path)

    print(
        f"✓ Input file loaded: {file_path}"
    )

    print(
        f"✓ Raw columns detected: {len(df.columns)}"
    )

    # Preserve raw column names for debugging
    original_columns = list(df.columns)

    df = clean_column_names(df)

    print("\nDetected input columns:")

    for column in df.columns:
        print(f"  • {column}")

    print("\nDetecting topology parameters...")

    detected = detect_columns(df)

    # -----------------------------------------------------
    # Check essential parameters
    # -----------------------------------------------------

    required = [
        "node",
        "degree",
        "bc"
    ]

    missing_required = [
        column
        for column in required
        if column not in detected
    ]

    if missing_required:

        raise ValueError(
            "\nCould not detect required topology "
            "parameters:\n"
            f"{missing_required}\n\n"
            "Detected columns were:\n"
            f"{list(df.columns)}\n\n"
            "Please check the NetworkAnalyzer output "
            "column names."
        )

    # -----------------------------------------------------
    # Standardize
    # -----------------------------------------------------

    standardized_df = standardize_dataset(
        df,
        detected
    )

    return standardized_df, detected
