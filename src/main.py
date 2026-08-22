import os

from input_parser import load_and_standardize
from validation import validate_dataset
from hub_analysis import run_hb_analysis


INPUT_FILE = "data/networkanalyzer_input.xlsx"


def main():

    print("=" * 60)
    print("HubBottleNet - Hub-Bottleneck Analysis")
    print("=" * 60)

    # --------------------------------------------------
    # 1. Load and standardize input
    # --------------------------------------------------

    print("\n[1] Loading network data...")

    df, detected_columns = load_and_standardize(
        INPUT_FILE
    )

    print(f"✓ Nodes loaded: {len(df)}")
    print(
        f"✓ Topology parameters detected: "
        f"{len(detected_columns)}"
    )

    # --------------------------------------------------
    # 2. Validate dataset
    # --------------------------------------------------

    print("\n[2] Validating dataset...")

    validation = validate_dataset(df)

    df = validation["data"]

    print("✓ Required columns validated")
    print(
        f"✓ Missing values: "
        f"{validation['missing_values']}"
    )
    print(
        f"✓ Duplicate nodes: "
        f"{validation['duplicate_nodes']}"
    )
    print(
        f"✓ Negative values: "
        f"{validation['negative_values']}"
    )

    # --------------------------------------------------
    # 3. Run Hub-Bottleneck analysis
    # --------------------------------------------------

    print("\n[3] Running Hub-Bottleneck analysis...")

    results, statistics = run_hb_analysis(df)

    print(
        f"✓ Average Degree: "
        f"{statistics['average_degree']:.4f}"
    )

    print(
        f"✓ Degree SD: "
        f"{statistics['degree_sd']:.4f}"
    )

    print(
        f"✓ Hub threshold: "
        f"{statistics['hub_threshold']:.4f}"
    )

    print(
        f"✓ Hubs identified: "
        f"{statistics['number_of_hubs']}"
    )

    print(
        f"✓ Bottlenecks identified: "
        f"{statistics['number_of_bottlenecks']}"
    )

    print(
        f"✓ Hub-Bottlenecks identified: "
        f"{statistics['number_of_hub_bottlenecks']}"
    )

    # --------------------------------------------------
    # 4. Save analysis results
    # --------------------------------------------------

    os.makedirs("results", exist_ok=True)

    output_file = "results/hub_bottleneck_results.csv"

    results.to_csv(
        output_file,
        index=False
    )

    print(
        f"✓ Results saved to: {output_file}"
    )

    # --------------------------------------------------
    # 5. Display H-B genes
    # --------------------------------------------------

    hb_genes = results.loc[
        results["hb_status"] == "Hub-Bottleneck",
        "node"
    ].tolist()

    # --------------------------------------------------
    # Save analysis summary
    # --------------------------------------------------

    summary_file = "results/hub_bottleneck_summary.txt"

    with open(summary_file, "w") as file:

        file.write(
            "HubBottleNet - Hub-Bottleneck Analysis Summary\n"
        )

        file.write("=" * 50 + "\n\n")

        file.write(
            f"Number of nodes: "
            f"{statistics['number_of_nodes']}\n"
        )

        file.write(
            f"Average Degree: "
            f"{statistics['average_degree']:.4f}\n"
        )

        file.write(
            f"Degree SD: "
            f"{statistics['degree_sd']:.4f}\n"
        )

        file.write(
            f"Hub threshold (AD + 2SD): "
            f"{statistics['hub_threshold']:.4f}\n"
        )

        file.write(
            "Hub criterion: Degree >= AD + 2SD\n"
        )

        file.write(
            "Bottleneck criterion: Top 5% "
            "Betweenness Centrality\n"
        )

        file.write(
            f"Number of Hubs: "
            f"{statistics['number_of_hubs']}\n"
        )

        file.write(
            f"Number of Bottlenecks: "
            f"{statistics['number_of_bottlenecks']}\n"
        )

        file.write(
            f"Number of Hub-Bottlenecks: "
            f"{statistics['number_of_hub_bottlenecks']}\n"
        )

        file.write("\nHub-Bottleneck genes:\n")

        for gene in hb_genes:
            file.write(f"{gene}\n")

    print(
        f"✓ Summary saved to: {summary_file}"
    )

    print("\nHub-Bottleneck genes:")

    if hb_genes:
        for gene in hb_genes:
            print(f"✓ {gene}")
    else:
        print("No Hub-Bottleneck genes identified.")


if __name__ == "__main__":
    main()
