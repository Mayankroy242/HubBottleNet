import math


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


def classify_hubs(df, degree_threshold):
    """Classify nodes as Hub or Non-Hub."""

    df = df.copy()

    df["hub_status"] = df["degree"].apply(
        lambda x: "Hub"
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
        lambda x: "Bottleneck"
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


def run_hb_analysis(df, bottleneck_percentage=0.05):
    """Run the complete Hub-Bottleneck analysis."""

    degree_mean, degree_sd, degree_threshold = (
        calculate_degree_threshold(df)
    )

    df = classify_hubs(
        df,
        degree_threshold
    )

    df, number_of_bottlenecks = classify_bottlenecks(
        df,
        percentage=bottleneck_percentage
    )

    df = classify_hub_bottlenecks(df)

    statistics = {
        "average_degree": degree_mean,
        "degree_sd": degree_sd,
        "hub_threshold": degree_threshold,
        "bottleneck_percentage": bottleneck_percentage,
        "number_of_nodes": len(df),
        "number_of_bottlenecks": number_of_bottlenecks,
        "number_of_hubs": (
            df["hub_status"] == "Hub"
        ).sum(),
        "number_of_hub_bottlenecks": (
            df["hb_status"] == "Hub-Bottleneck"
        ).sum()
    }

    return df, statistics
