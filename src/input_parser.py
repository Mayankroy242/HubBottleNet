import pandas as pd


COLUMN_ALIASES = {
    "node": [
        "node",
        "gene",
        "gene name",
        "protein",
        "target"
    ],

    "degree": [
        "degree",
        "node degree"
    ],

    "bc": [
        "bc",
        "betweenness",
        "betweenness centrality"
    ],

    "cc": [
        "cc",
        "closeness",
        "closeness centrality"
    ],

    "clustering_coefficient": [
        "clustering coefficient",
        "clustering"
    ],

    "neighborhood_connectivity": [
        "neighborhood connectivity",
        "neighbourhood connectivity"
    ],

    "undirected_edges": [
        "no. of undirected edges",
        "number of undirected edges",
        "undirected edges"
    ],

    "radiality": [
        "radiality"
    ],

    "topological_coefficient": [
        "topological coefficient",
        "topological coefficients"
    ]
}


def clean_column_names(df):
    """Clean Excel column names."""

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace("_", " ", regex=False)
    )

    return df


def detect_columns(df):
    """Detect NetworkAnalyzer columns using predefined aliases."""

    detected = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

        matches = [
            column for column in df.columns
            if column in aliases
        ]

        if len(matches) == 1:
            detected[standard_name] = matches[0]

        elif len(matches) > 1:
            raise ValueError(
                f"Multiple possible columns detected for "
                f"{standard_name}: {matches}"
            )

    return detected


def standardize_dataset(df, detected):
    """Create standardized topology dataframe."""

    standardized_df = pd.DataFrame()

    for standard_name, original_name in detected.items():
        standardized_df[standard_name] = df[original_name]

    return standardized_df


def load_and_standardize(file_path):
    """Load Excel file and return standardized dataset."""

    df = pd.read_excel(file_path)

    df = clean_column_names(df)

    detected = detect_columns(df)

    standardized_df = standardize_dataset(
        df,
        detected
    )

    return standardized_df, detected
