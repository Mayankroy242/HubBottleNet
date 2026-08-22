import pandas as pd


REQUIRED_COLUMNS = [
    "node",
    "degree",
    "bc"
]


NUMERIC_COLUMNS = [
    "degree",
    "bc",
    "cc",
    "clustering_coefficient",
    "neighborhood_connectivity",
    "undirected_edges",
    "radiality",
    "topological_coefficient"
]


def validate_required_columns(df):
    """Check that essential H-B columns are present."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def convert_numeric_columns(df):
    """Convert topology parameters to numeric values."""

    df = df.copy()

    for column in NUMERIC_COLUMNS:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def check_missing_values(df):
    """Check missing values in essential parameters."""

    problems = {}

    for column in REQUIRED_COLUMNS:

        missing = df[column].isna().sum()

        if missing > 0:
            problems[column] = int(missing)

    return problems


def check_duplicate_nodes(df):
    """Check for duplicated node names."""

    duplicates = df["node"].duplicated().sum()

    return int(duplicates)


def check_negative_values(df):
    """Check for biologically invalid negative Degree and BC."""

    problems = {}

    negative_degree = (df["degree"] < 0).sum()
    negative_bc = (df["bc"] < 0).sum()

    if negative_degree > 0:
        problems["degree"] = int(negative_degree)

    if negative_bc > 0:
        problems["bc"] = int(negative_bc)

    return problems


def validate_dataset(df):
    """Run complete data-quality validation."""

    validate_required_columns(df)

    df = convert_numeric_columns(df)

    missing_values = check_missing_values(df)

    duplicate_nodes = check_duplicate_nodes(df)

    negative_values = check_negative_values(df)

    return {
        "data": df,
        "missing_values": missing_values,
        "duplicate_nodes": duplicate_nodes,
        "negative_values": negative_values
    }
