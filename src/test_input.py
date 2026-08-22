import pandas as pd

file_path = "data/networkanalyzer_input.xlsx"

df = pd.read_excel(file_path)

# Clean column names
df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace("_", " ", regex=False)
)

# Possible names for important parameters
column_aliases = {
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

detected = {}

for standard_name, aliases in column_aliases.items():

    matches = [
        column for column in df.columns
        if column in aliases
    ]

    if len(matches) == 1:
        detected[standard_name] = matches[0]

    elif len(matches) > 1:
        print(f"WARNING: Multiple possible columns detected for {standard_name}:")
        print(matches)

    else:
        print(f"WARNING: Could not automatically identify {standard_name}")

for standard_name, aliases in column_aliases.items():

    matches = [
        column for column in df.columns
        if column in aliases
    ]

    if len(matches) == 1:
        detected[standard_name] = matches[0]

    elif len(matches) > 1:
        print(f"WARNING: Multiple possible columns detected for {standard_name}:")
        print(matches)

    else:
        print(f"WARNING: Could not automatically identify {standard_name}")

print("\nDetected columns:")
for standard_name, original_name in detected.items():
    print(f"✓ {standard_name} → {original_name}")

# Create standardized dataset
standardized_df = pd.DataFrame()

for standard_name, original_name in detected.items():
    standardized_df[standard_name] = df[original_name]

print("\nStandardized dataset:")
print(standardized_df.head())

print("\nStandardized columns:")
print(standardized_df.columns.tolist())

# Data-quality validation

print("\nData quality checks:")

# Check numeric columns
numeric_columns = [
    "degree",
    "bc",
    "cc",
    "clustering_coefficient",
    "neighborhood_connectivity",
    "undirected_edges",
    "radiality",
    "topological_coefficient"
]

for column in numeric_columns:
    if column in standardized_df.columns:
        standardized_df[column] = pd.to_numeric(
            standardized_df[column],
            errors="coerce"
        )

# Check missing values in essential parameters
for column in ["node", "degree", "bc"]:
    missing = standardized_df[column].isna().sum()

    if missing == 0:
        print(f"✓ {column}: no missing values")
    else:
        print(f"⚠ {column}: {missing} missing values")

# Check duplicate nodes
duplicate_nodes = standardized_df["node"].duplicated().sum()

if duplicate_nodes == 0:
    print("✓ No duplicate nodes")
else:
    print(f"⚠ Duplicate nodes detected: {duplicate_nodes}")

# Check negative Degree
negative_degree = (standardized_df["degree"] < 0).sum()

if negative_degree == 0:
    print("✓ Degree values valid")
else:
    print(f"⚠ Negative Degree values detected: {negative_degree}")

# Check negative BC
negative_bc = (standardized_df["bc"] < 0).sum()

if negative_bc == 0:
    print("✓ Betweenness Centrality values valid")
else:
    print(f"⚠ Negative BC values detected: {negative_bc}")

# Degree statistics for Hub identification

degree_mean = standardized_df["degree"].mean()
degree_sd = standardized_df["degree"].std()

degree_threshold = degree_mean + (2 * degree_sd)

print("\nDegree statistics:")
print(f"Average Degree (AD): {degree_mean:.4f}")
print(f"Standard Deviation (SD): {degree_sd:.4f}")
print(f"Hub threshold (AD + 2SD): {degree_threshold:.4f}")


# Hub classification

standardized_df["hub_status"] = standardized_df["degree"].apply(
    lambda x: "Hub" if x >= degree_threshold else "Non-Hub"
)

print("\nHub classification:")
print(
    standardized_df[
        ["node", "degree", "hub_status"]
    ].to_string(index=False)
)

print(
    f"\nTotal Hubs: "
    f"{(standardized_df['hub_status'] == 'Hub').sum()}"
)


import math

# Bottleneck identification: top 5% by Betweenness Centrality

bottleneck_percentage = 0.05

number_of_nodes = len(standardized_df)

number_of_bottlenecks = math.ceil(
    number_of_nodes * bottleneck_percentage
)

# Rank nodes by BC from highest to lowest
standardized_df["bc_rank"] = standardized_df["bc"].rank(
    method="first",
    ascending=False
)

standardized_df["bottleneck_status"] = standardized_df["bc_rank"].apply(
    lambda x: "Bottleneck"
    if x <= number_of_bottlenecks
    else "Non-Bottleneck"
)

print("\nBottleneck classification:")
print(
    standardized_df[
        ["node", "bc", "bc_rank", "bottleneck_status"]
    ]
    .sort_values("bc_rank")
    .to_string(index=False)
)

print(f"\nTotal nodes: {number_of_nodes}")
print(f"Top 5% bottleneck count: {number_of_bottlenecks}")


# Hub-Bottleneck classification

standardized_df["hb_status"] = standardized_df.apply(
    lambda row: "Hub-Bottleneck"
    if (
        row["hub_status"] == "Hub"
        and row["bottleneck_status"] == "Bottleneck"
    )
    else "Not Hub-Bottleneck",
    axis=1
)

print("\nHub-Bottleneck classification:")
print(
    standardized_df[
        ["node", "degree", "bc", "hub_status",
         "bottleneck_status", "hb_status"]
    ].to_string(index=False)
)

hb_genes = standardized_df.loc[
    standardized_df["hb_status"] == "Hub-Bottleneck",
    "node"
].tolist()

print("\nHub-Bottleneck genes:")

if hb_genes:
    for gene in hb_genes:
        print(f"✓ {gene}")
else:
    print("No Hub-Bottleneck genes identified.")
