import os
import argparse
from pathlib import Path

from input_parser import load_and_standardize
from validation import validate_dataset
from hub_analysis import run_hb_analysis
from advanced_analysis import run_advanced_analysis


# =========================================================
# Input file handling
# =========================================================

def find_default_input():

    data_dir = Path("data")

    supported_extensions = [
        ".csv",
        ".tsv",
        ".txt",
        ".xlsx",
        ".xls",
        ".xlsm",
        ".xlsb"
    ]

    candidates = []

    for extension in supported_extensions:

        candidates.extend(
            data_dir.glob(
                f"networkanalyzer_input{extension}"
            )
        )

    if not candidates:

        raise FileNotFoundError(
            "No default NetworkAnalyzer input file found.\n"
            "Expected something like:\n"
            "data/networkanalyzer_input.csv\n"
            "or\n"
            "data/networkanalyzer_input.xlsx"
        )

    if len(candidates) > 1:

        print(
            "Multiple NetworkAnalyzer input files found:"
        )

        for file in candidates:

            print(
                f"  • {file}"
            )

        print(
            f"\nUsing: {candidates[0]}"
        )

    return str(candidates[0])


# =========================================================
# Command-line arguments
# =========================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "HubBottleNet - Hub-Bottleneck "
            "Analysis"
        )
    )

    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help=(
            "Path to NetworkAnalyzer input file "
            "(CSV, XLSX, XLS, TSV, TXT, etc.)"
        )
    )

    return parser.parse_args()


# =========================================================
# Main pipeline
# =========================================================

def main():

    args = parse_arguments()

    print("=" * 60)
    print(
        "HubBottleNet - Hub-Bottleneck Analysis"
    )
    print("=" * 60)

    # -----------------------------------------------------
    # 1. Determine input file
    # -----------------------------------------------------

    if args.input:

        input_file = args.input

    else:

        input_file = find_default_input()

    print(
        f"\nInput file: {input_file}"
    )

    # -----------------------------------------------------
    # 2. Load and standardize input
    # -----------------------------------------------------

    print(
        "\n[1] Loading network data..."
    )

    df, detected_columns = load_and_standardize(
        input_file
    )

    print(
        f"\n✓ Nodes loaded: {len(df)}"
    )

    print(
        f"✓ Topology parameters detected: "
        f"{len(detected_columns)}"
    )

    # -----------------------------------------------------
    # 3. Validate dataset
    # -----------------------------------------------------

    print(
        "\n[2] Validating dataset..."
    )

    validation = validate_dataset(df)

    df = validation["data"]

    print(
        "✓ Required columns validated"
    )

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

    # -----------------------------------------------------
    # 4. Hub-Bottleneck analysis
    # -----------------------------------------------------

    print(
        "\n[3] Running Hub-Bottleneck analysis..."
    )

    results, ranked_hb, statistics = run_hb_analysis(
        df
    )

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

    # -----------------------------------------------------
    # 5. Create results directory
    # -----------------------------------------------------

    os.makedirs(
        "results",
        exist_ok=True
    )

    # -----------------------------------------------------
    # 6. Save complete H-B results
    # -----------------------------------------------------

    output_file = (
        "results/"
        "hub_bottleneck_results.csv"
    )

    results.to_csv(
        output_file,
        index=False
    )

    print(
        f"✓ Results saved to: "
        f"{output_file}"
    )

    # -----------------------------------------------------
    # 7. Save ranked H-B results
    # -----------------------------------------------------

    ranked_output_file = (
        "results/"
        "hub_bottleneck_ranked.csv"
    )

    ranked_hb.to_csv(
        ranked_output_file,
        index=False
    )

    print(
        f"✓ Ranked H-B results saved to: "
        f"{ranked_output_file}"
    )

    # -----------------------------------------------------
    # 8. Identify Hub-Bottleneck genes
    # -----------------------------------------------------

    hb_genes = results.loc[
        results["hb_status"] == "Hub-Bottleneck",
        "node"
    ].tolist()

    # -----------------------------------------------------
    # 9. Save analysis summary
    # -----------------------------------------------------

    summary_file = (
        "results/"
        "hub_bottleneck_summary.txt"
    )

    with open(
        summary_file,
        "w"
    ) as file:

        file.write(
            "HubBottleNet - Hub-Bottleneck "
            "Analysis Summary\n"
        )

        file.write(
            "=" * 50 + "\n\n"
        )

        file.write(
            f"Input file: "
            f"{input_file}\n\n"
        )

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

        file.write(
            "\nHub-Bottleneck genes:\n"
        )

        for gene in hb_genes:

            file.write(
                f"{gene}\n"
            )

    print(
        f"✓ Summary saved to: "
        f"{summary_file}"
    )

    # -----------------------------------------------------
    # 10. Display Hub-Bottlenecks
    # -----------------------------------------------------

    print(
        "\nHub-Bottleneck genes:"
    )

    if hb_genes:

        for gene in hb_genes:

            print(
                f"✓ {gene}"
            )

    else:

        print(
            "No Hub-Bottleneck genes identified."
        )

    # -----------------------------------------------------
    # 11. Display H-B ranking
    # -----------------------------------------------------

    print(
        "\nHub-Bottleneck ranking:"
    )

    if not ranked_hb.empty:

        for _, row in ranked_hb.iterrows():

            print(
                f"{int(row['hb_rank'])}. "
                f"{row['node']} "
                f"(Degree: {row['degree']}, "
                f"BC: {row['bc']:.6f}, "
                f"H-B Score: {row['hb_score']:.4f})"
            )

    else:

        print(
            "No Hub-Bottleneck genes identified."
        )

    # -----------------------------------------------------
    # 12. Optional further network analysis
    # -----------------------------------------------------

    print(
        "\nWould you like to perform further "
        "network analysis? [y/n]"
    )

    choice = input(
        "Enter choice: "
    ).strip().lower()

    if choice in ["y", "yes"]:

        print(
            "\n" + "=" * 60
        )

        print(
            "HubBottleNet - Further Network Analysis"
        )

        print(
            "=" * 60
        )

        print(
            "\nRunning additional network analyses..."
        )

        advanced = run_advanced_analysis(
            results,
            ranked_hb,
            results_directory="results"
        )

        print(
            "\n✓ Network topology profiling completed."
        )

        print(
            "✓ Hub-Bottleneck topology analysis completed."
        )

        print(
            "✓ Network comparison analysis completed."
        )

        print(
            "✓ Topology correlation analysis completed."
        )

        print(
            "✓ Sensitivity analysis completed."
        )

        print(
            "✓ Analysis figures generated."
        )

        print(
            "\nResults saved to: results/"
        )

        print(
            "Figures saved to: results/figures/"
        )

    else:

        print(
            "\nAnalysis completed."
        )


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":

    main()
