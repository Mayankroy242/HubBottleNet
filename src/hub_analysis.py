import math
import pandas as pd


def calculate_degree_threshold(df):
    """
    Calculate the Hub threshold using:

    AD + 2 × SD

    where AD is the average Degree.
    """

    degree_mean = df["degree"].mean()
    degree_sd = df["degree"].std()

    degree_threshold = degree_mean + (2 * degree_sd)

    return degree_mean, degree_sd, degree_threshold


def calculate_bc_cutoff(df, percentage=0.05):
    """
    Determine the Betweenness Centrality cutoff corresponding
    to the top percentage of nodes.

    This cutoff is used only for reporting/ranking.
    Bottleneck identification itself remains rank-based.
    """

    number_of_nodes = len(df)

    number_of_bottlenecks = math.ceil(
        number_of_nodes * percentage
    )

    bc_sorted = df["bc"].sort_values(
        ascending=False
    )

    cutoff_index = number_of_bottlenecks - 1

    bc_cutoff = bc_sorted.iloc[cutoff_index]

    return bc_cutoff, number_of_bottlenecks


def classify_hubs(df, degree_threshold):
    """Classify nodes as Hub or Non-Hub."""

    df = df.copy()

    df["hub_status"] = df["degree"].apply(
        lambda x:
        "Hub"
        if x >= degree_threshold
        else "Non-Hub"
    )

    return df


def classify_bottlenecks(df, percentage=0.05):
    """
    Identify bottlenecks using the top percentage
    of nodes ranked by Betweenness Centrality.
    """

    df = df.copy()

    number_of_nodes = len(df)

    number_of_bottlenecks = math.ceil(
        number_of_nodes * percentage
    )

    df["bc_rank"] = df["bc"].rank(
        method="first",
        ascending=False
    )

    df["bottleneck_status"] = df["bc_rank"].apply(
        lambda x:
        "Bottleneck"
        if x <= number_of_bottlenecks
        else "Non-Bottleneck"
    )

    return df, number_of_bottlenecks


def classify_hub_bottlenecks(df):
    """Identify nodes satisfying both Hub and Bottleneck criteria."""

    df = df.copy()

    df["hb_status"] = df.apply(
        lambda row:
        "Hub-Bottleneck"
        if (
            row["hub_status"] == "Hub"
            and row["bottleneck_status"] == "Bottleneck"
        )
        else "Not Hub-Bottleneck",
        axis=1
    )

    return df


def rank_hub_bottlenecks(
    df,
    degree_threshold,
    bc_cutoff
):
    """
    Rank already-identified Hub-Bottleneck nodes.

    IMPORTANT:
    This ranking does NOT determine H-B membership.

    H-B membership has already been determined using:

        Hub = Degree >= AD + 2SD
        Bottleneck = Top 5% BC

    The ranking describes how strongly each H-B node
    exceeds the two existing criteria.
    """

    df = df.copy()

    hb_mask = (
        df["hb_status"] == "Hub-Bottleneck"
    )

    hb = df.loc[hb_mask].copy()

    if hb.empty:
        hb["hub_strength"] = pd.Series(
            dtype=float
        )

        hb["bottleneck_strength"] = pd.Series(
            dtype=float
        )

        hb["hb_score"] = pd.Series(
            dtype=float
        )

        hb["hb_rank"] = pd.Series(
            dtype="Int64"
        )

        return df, hb

    # --------------------------------------------------
    # Relative strength of the original Hub criterion
    # --------------------------------------------------

    hb["hub_strength"] = (
        hb["degree"] / degree_threshold
    )

    # --------------------------------------------------
    # Relative strength of the original
    # Bottleneck criterion
    # --------------------------------------------------

    if bc_cutoff > 0:

        hb["bottleneck_strength"] = (
            hb["bc"] / bc_cutoff
        )

    else:

        hb["bottleneck_strength"] = 0.0

    # --------------------------------------------------
    # Combined H-B score
    # --------------------------------------------------

    hb["hb_score"] = (
        hb["hub_strength"]
        + hb["bottleneck_strength"]
    ) / 2

    # --------------------------------------------------
    # Supporting ranks
    # --------------------------------------------------

    hb["degree_rank"] = (
        hb["degree"]
        .rank(
            method="min",
            ascending=False
        )
        .astype(int)
    )

    hb["bc_rank_hb"] = (
        hb["bc"]
        .rank(
            method="min",
            ascending=False
        )
        .astype(int)
    )

    # --------------------------------------------------
    # Final H-B ranking
    # --------------------------------------------------

    hb = hb.sort_values(
        by=[
            "hb_score",
            "degree",
            "bc"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )

    hb["hb_rank"] = range(
        1,
        len(hb) + 1
    )

    # --------------------------------------------------
    # Put ranking back into complete dataframe
    # --------------------------------------------------

    df["hb_rank"] = pd.NA
    df["hb_score"] = pd.NA
    df["hub_strength"] = pd.NA
    df["bottleneck_strength"] = pd.NA
    df["degree_rank_hb"] = pd.NA
    df["bc_rank_hb"] = pd.NA

    for index, row in hb.iterrows():

        df.loc[
            index,
            "hb_rank"
        ] = int(row["hb_rank"])

        df.loc[
            index,
            "hb_score"
        ] = row["hb_score"]

        df.loc[
            index,
            "hub_strength"
        ] = row["hub_strength"]

        df.loc[
            index,
            "bottleneck_strength"
        ] = row["bottleneck_strength"]

        df.loc[
            index,
            "degree_rank_hb"
        ] = int(row["degree_rank"])

        df.loc[
            index,
            "bc_rank_hb"
        ] = int(row["bc_rank_hb"])

    return df, hb


def run_hb_analysis(
    df,
    bottleneck_percentage=0.05
):
    """
    Run the complete Hub-Bottleneck analysis.

    V0.1 identification criteria:

        Hub:
            Degree >= AD + 2SD

        Bottleneck:
            Top 5% Betweenness Centrality

        Hub-Bottleneck:
            Hub AND Bottleneck

    Ranking is performed only after H-B identification.
    """

    # --------------------------------------------------
    # 1. Hub threshold
    # --------------------------------------------------

    (
        degree_mean,
        degree_sd,
        degree_threshold
    ) = calculate_degree_threshold(df)

    # --------------------------------------------------
    # 2. Hub classification
    # --------------------------------------------------

    df = classify_hubs(
        df,
        degree_threshold
    )

    # --------------------------------------------------
    # 3. Bottleneck classification
    # --------------------------------------------------

    df, number_of_bottlenecks = (
        classify_bottlenecks(
            df,
            percentage=bottleneck_percentage
        )
    )

    # --------------------------------------------------
    # 4. H-B classification
    # --------------------------------------------------

    df = classify_hub_bottlenecks(df)

    # --------------------------------------------------
    # 5. BC cutoff
    # --------------------------------------------------

    (
        bc_cutoff,
        _
    ) = calculate_bc_cutoff(
        df,
        percentage=bottleneck_percentage
    )

    # --------------------------------------------------
    # 6. Rank H-B nodes
    # --------------------------------------------------

    df, ranked_hb = rank_hub_bottlenecks(
        df,
        degree_threshold,
        bc_cutoff
    )

    # --------------------------------------------------
    # 7. Statistics
    # --------------------------------------------------

    statistics = {

        "average_degree":
            degree_mean,

        "degree_sd":
            degree_sd,

        "hub_threshold":
            degree_threshold,

        "bottleneck_percentage":
            bottleneck_percentage,

        "bc_cutoff":
            bc_cutoff,

        "number_of_nodes":
            len(df),

        "number_of_bottlenecks":
            number_of_bottlenecks,

        "number_of_hubs":
            (
                df["hub_status"] == "Hub"
            ).sum(),

        "number_of_hub_bottlenecks":
            (
                df["hb_status"]
                == "Hub-Bottleneck"
            ).sum()
    }

    return df, ranked_hb, statistics
