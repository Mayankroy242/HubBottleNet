import os
import math
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


# =========================================================
# Advanced Network Analysis
# =========================================================

TOPOLOGY_COLUMNS = [
    "degree",
    "bc",
    "cc",
    "clustering_coefficient",
    "neighborhood_connectivity",
    "radiality",
    "topological_coefficient",
]


# ---------------------------------------------------------
# Percentile profiling
# ---------------------------------------------------------

def calculate_percentiles(df):

    df = df.copy()

    for column in TOPOLOGY_COLUMNS:

        percentile_column = f"{column}_percentile"

        df[percentile_column] = (
            df[column]
            .rank(pct=True) * 100
        )

    return df


# ---------------------------------------------------------
# H-B topology profiles
# ---------------------------------------------------------

def extract_hb_profiles(df):

    hb = df[
        df["hb_status"] == "Hub-Bottleneck"
    ].copy()

    columns = [
        "node",
        "degree",
        "bc",
        "cc",
        "clustering_coefficient",
        "neighborhood_connectivity",
        "radiality",
        "topological_coefficient",
    ]

    return hb[columns].reset_index(drop=True)


# ---------------------------------------------------------
# H-B vs network comparison
# ---------------------------------------------------------

def compare_hb_with_network(df):

    hb = df[
        df["hb_status"] == "Hub-Bottleneck"
    ]

    records = []

    for column in TOPOLOGY_COLUMNS:

        network_mean = df[column].mean()

        hb_mean = hb[column].mean()

        if network_mean != 0:

            enrichment = (
                hb_mean / network_mean
            )

        else:

            enrichment = float("nan")

        records.append({
            "parameter": column,
            "network_mean": network_mean,
            "hb_mean": hb_mean,
            "relative_enrichment": enrichment
        })

    return pd.DataFrame(records)


# ---------------------------------------------------------
# Correlation analysis
# ---------------------------------------------------------

def calculate_topology_correlations(df):

    return df[
        TOPOLOGY_COLUMNS
    ].corr(method="pearson")


# ---------------------------------------------------------
# Sensitivity analysis
# ---------------------------------------------------------

def run_sensitivity_analysis(
    df,
    reference_hb_genes=None
):

    if reference_hb_genes is None:

        reference_hb_genes = set(
            df.loc[
                df["hb_status"] == "Hub-Bottleneck",
                "node"
            ]
        )

    degree_mean = df["degree"].mean()
    degree_sd = df["degree"].std()

    sd_multipliers = [
        1.5,
        1.75,
        2.0,
        2.25,
        2.5,
        2.75,
        3.0
    ]

    bottleneck_percentages = [
        0.03,
        0.05,
        0.07,
        0.10
    ]

    records = []

    for multiplier in sd_multipliers:

        threshold = (
            degree_mean
            + multiplier * degree_sd
        )

        for percentage in bottleneck_percentages:

            number_of_bottlenecks = math.ceil(
                len(df) * percentage
            )

            hubs = df[
                df["degree"] >= threshold
            ]

            ranked = df[
                ["node", "bc"]
            ].sort_values(
                "bc",
                ascending=False
            )

            bottlenecks = ranked.head(
                number_of_bottlenecks
            )

            bottleneck_genes = set(
                bottlenecks["node"]
            )

            hub_genes = set(
                hubs["node"]
            )

            hb_genes = (
                hub_genes
                & bottleneck_genes
            )

            if reference_hb_genes:

                overlap = (
                    len(
                        hb_genes
                        & reference_hb_genes
                    )
                    /
                    len(reference_hb_genes)
                )

            else:

                overlap = float("nan")

            records.append({

                "hub_sd_multiplier":
                    multiplier,

                "bottleneck_percentage":
                    percentage,

                "hub_threshold":
                    threshold,

                "number_of_hubs":
                    len(hub_genes),

                "number_of_bottlenecks":
                    number_of_bottlenecks,

                "number_of_hub_bottlenecks":
                    len(hb_genes),

                "overlap_with_v01_hb":
                    overlap
            })

    return pd.DataFrame(records)


# =========================================================
# Figures
# =========================================================

def generate_comparison_plot(
    comparison,
    output_file
):

    plt.figure(
        figsize=(10, 6)
    )

    x = range(
        len(comparison)
    )

    plt.bar(
        [i - 0.2 for i in x],
        comparison["network_mean"],
        width=0.4,
        label="Network mean"
    )

    plt.bar(
        [i + 0.2 for i in x],
        comparison["hb_mean"],
        width=0.4,
        label="Hub-Bottleneck mean"
    )

    plt.xticks(
        x,
        comparison["parameter"],
        rotation=45,
        ha="right"
    )

    plt.ylabel(
        "Mean value"
    )

    plt.title(
        "Hub-Bottleneck vs Network Topology"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def generate_hb_profile_plot(
    profiles,
    output_file
):

    metrics = [
        "degree",
        "bc",
        "cc",
        "clustering_coefficient",
        "neighborhood_connectivity",
        "radiality",
        "topological_coefficient"
    ]

    hb = profiles.copy()

    # Percentile-normalized profiles
    normalized = pd.DataFrame()

    normalized["node"] = hb["node"]

    for metric in metrics:

        values = hb[metric]

        normalized[metric] = (
            values.rank(pct=True) * 100
        )

    plt.figure(
        figsize=(11, 7)
    )

    for _, row in normalized.iterrows():

        plt.plot(
            metrics,
            row[metrics],
            marker="o",
            label=row["node"]
        )

    plt.ylabel(
        "Within H-B percentile"
    )

    plt.title(
        "Hub-Bottleneck Topology Profiles"
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def generate_correlation_heatmap(
    correlations,
    output_file
):

    plt.figure(
        figsize=(9, 8)
    )

    plt.imshow(
        correlations,
        aspect="auto"
    )

    plt.colorbar(
        label="Pearson correlation"
    )

    labels = correlations.columns

    plt.xticks(
        range(len(labels)),
        labels,
        rotation=45,
        ha="right"
    )

    plt.yticks(
        range(len(labels)),
        labels
    )

    for i in range(
        len(labels)
    ):

        for j in range(
            len(labels)
        ):

            plt.text(
                j,
                i,
                f"{correlations.iloc[i, j]:.2f}",
                ha="center",
                va="center"
            )

    plt.title(
        "Topology Correlation Matrix"
    )

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def generate_sensitivity_plot(
    sensitivity,
    output_file
):

    plt.figure(
        figsize=(10, 6)
    )

    for percentage in sorted(
        sensitivity[
            "bottleneck_percentage"
        ].unique()
    ):

        subset = sensitivity[
            sensitivity[
                "bottleneck_percentage"
            ] == percentage
        ]

        plt.plot(
            subset[
                "hub_sd_multiplier"
            ],
            subset[
                "number_of_hub_bottlenecks"
            ],
            marker="o",
            label=f"Top {percentage * 100:.0f}% BC"
        )

    plt.xlabel(
        "Hub threshold SD multiplier"
    )

    plt.ylabel(
        "Number of Hub-Bottlenecks"
    )

    plt.title(
        "Hub-Bottleneck Sensitivity Analysis"
    )

    plt.legend()

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def generate_hb_ranking_plot(
    ranked_hb,
    output_file
):

    if ranked_hb.empty:

        return

    plot_data = ranked_hb.sort_values(
        "hb_score",
        ascending=True
    )

    plt.figure(
        figsize=(9, 6)
    )

    plt.barh(
        plot_data["node"],
        plot_data["hb_score"]
    )

    plt.xlabel(
        "Hub-Bottleneck Score"
    )

    plt.ylabel(
        "Node"
    )

    plt.title(
        "Hub-Bottleneck Ranking"
    )

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


# =========================================================
# Main advanced-analysis pipeline
# =========================================================

def run_advanced_analysis(
    df,
    ranked_hb,
    results_directory="results"
):

    os.makedirs(
        results_directory,
        exist_ok=True
    )

    figures_directory = os.path.join(
        results_directory,
        "figures"
    )

    os.makedirs(
        figures_directory,
        exist_ok=True
    )

    # --------------------------------------------------
    # 1. Advanced topology profiling
    # --------------------------------------------------

    advanced = calculate_percentiles(df)

    advanced_file = os.path.join(
        results_directory,
        "advanced_topology_results.csv"
    )

    advanced.to_csv(
        advanced_file,
        index=False
    )

    # --------------------------------------------------
    # 2. H-B topology profiles
    # --------------------------------------------------

    hb_profiles = extract_hb_profiles(
        advanced
    )

    hb_profiles_file = os.path.join(
        results_directory,
        "hub_bottleneck_topology_profiles.csv"
    )

    hb_profiles.to_csv(
        hb_profiles_file,
        index=False
    )

    # --------------------------------------------------
    # 3. H-B vs network
    # --------------------------------------------------

    comparison = compare_hb_with_network(
        advanced
    )

    comparison_file = os.path.join(
        results_directory,
        "hb_vs_network_comparison.csv"
    )

    comparison.to_csv(
        comparison_file,
        index=False
    )

    # --------------------------------------------------
    # 4. Correlation matrix
    # --------------------------------------------------

    correlations = calculate_topology_correlations(
        advanced
    )

    correlation_file = os.path.join(
        results_directory,
        "topology_correlations.csv"
    )

    correlations.to_csv(
        correlation_file
    )

    # --------------------------------------------------
    # 5. Sensitivity analysis
    # --------------------------------------------------

    reference_hb_genes = set(
        df.loc[
            df["hb_status"] == "Hub-Bottleneck",
            "node"
        ]
    )

    sensitivity = run_sensitivity_analysis(
        df,
        reference_hb_genes
    )

    sensitivity_file = os.path.join(
        results_directory,
        "sensitivity_analysis.csv"
    )

    sensitivity.to_csv(
        sensitivity_file,
        index=False
    )

    # ==================================================
    # Generate figures
    # ==================================================

    generate_comparison_plot(
        comparison,
        os.path.join(
            figures_directory,
            "hb_vs_network_comparison.png"
        )
    )

    generate_hb_profile_plot(
        hb_profiles,
        os.path.join(
            figures_directory,
            "hb_topology_profiles.png"
        )
    )

    generate_correlation_heatmap(
        correlations,
        os.path.join(
            figures_directory,
            "topology_correlation_heatmap.png"
        )
    )

    generate_sensitivity_plot(
        sensitivity,
        os.path.join(
            figures_directory,
            "sensitivity_analysis.png"
        )
    )

    generate_hb_ranking_plot(
        ranked_hb,
        os.path.join(
            figures_directory,
            "hb_ranking.png"
        )
    )

    return {
        "advanced": advanced,
        "hb_profiles": hb_profiles,
        "comparison": comparison,
        "correlations": correlations,
        "sensitivity": sensitivity
    }
