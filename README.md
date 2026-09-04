# HubBottleNet

HubBottleNet is a Python-based network analysis tool for systematic
identification and ranking of hub, bottleneck, and hub-bottleneck genes
from Cytoscape NetworkAnalyzer topology data.

The software provides a reproducible workflow that combines classical
hub-bottleneck identification with advanced network-topology profiling,
comparative analysis, correlation analysis, sensitivity analysis, and
automated visualization.

## Current Version

**Version 0.2.0 — Advanced Network Analysis**

Version 0.2.0 extends the original HubBottleNet v0.1 hub-bottleneck
identification workflow with additional topology analysis and automated
figure generation.

---

## Pipeline

HubBottleNet performs the following analysis workflow:

    Cytoscape NetworkAnalyzer Input
                    |
                    v
        Input Detection & Standardization
                    |
                    v
             Dataset Validation
                    |
                    v
             Hub Identification
             Degree >= AD + 2SD
                    |
                    v
          Bottleneck Identification
              Top 5% BC
                    |
                    v
        Hub-Bottleneck Identification
             Hub AND Bottleneck
                    |
                    v
          Hub-Bottleneck Ranking
                    |
                    v
       Advanced Network Topology Analysis
                    |
        +-----------+-----------+-----------+
        |           |           |           |
        v           v           v           v
    Topology     H-B vs      Correlation  Sensitivity
    Profiling    Network      Analysis     Analysis
                 Comparison
        |
        v
    Automated Figure Generation
        |
        v
       CSV + TXT + PNG Results

---

## Core Methodology

### Hub identification

The average degree (AD) and standard deviation (SD) of network nodes
are calculated.

A node is classified as a hub when:

    Degree >= AD + 2 × SD

### Bottleneck identification

Nodes are ranked according to betweenness centrality (BC).

The top 5% of nodes with the highest BC values are classified as
bottlenecks.

### Hub-Bottleneck identification

A node is classified as a Hub-Bottleneck only when it satisfies both:

1. Degree >= AD + 2 × SD
2. Belongs to the top 5% of BC

Thus:

    Hub-Bottleneck = Hub AND Bottleneck

### Hub-Bottleneck ranking

After Hub-Bottleneck identification, the identified H-B nodes are
ranked using a combined score derived from their relative strength
against the two original criteria.

The ranking does not determine H-B membership.

H-B membership is established first using the predefined hub and
bottleneck criteria.

---

# Advanced Network Analysis

Version 0.2.0 adds an automated advanced-analysis layer after the
primary Hub-Bottleneck analysis.

## 1. Network topology profiling

The network is profiled using the available topology parameters:

- Degree
- Betweenness centrality
- Closeness centrality
- Clustering coefficient
- Neighborhood connectivity
- Radiality
- Topological coefficient

Percentile profiles are calculated for the topology parameters to
provide relative positioning of nodes within the complete network.

## 2. Hub-Bottleneck topology profiles

The topology of identified Hub-Bottleneck nodes is extracted into a
dedicated profile table.

This allows the structural characteristics of H-B nodes to be examined
independently from the complete network.

## 3. Hub-Bottleneck vs network comparison

Mean topology values of Hub-Bottleneck nodes are compared with the
corresponding network-wide means.

A relative enrichment ratio is calculated as:

    H-B mean / Network mean

This provides a quantitative description of how strongly the identified
Hub-Bottleneck population differs from the overall network.

## 4. Topology correlation analysis

Pairwise correlations between the major topology parameters are
calculated.

The resulting correlation matrix can be used to examine relationships
between:

- Degree
- Betweenness centrality
- Closeness centrality
- Clustering coefficient
- Neighborhood connectivity
- Radiality
- Topological coefficient

## 5. Sensitivity analysis

The Hub-Bottleneck identification procedure is evaluated across
different hub threshold multipliers and bottleneck percentages.

The sensitivity analysis examines combinations of:

- Hub threshold multiplier
- Bottleneck percentage
- Number of identified hubs
- Number of identified bottlenecks
- Number of identified Hub-Bottlenecks
- Overlap with the default v0.1 Hub-Bottleneck set

The default HubBottleNet criterion remains:

    Hub threshold = AD + 2SD
    Bottleneck threshold = Top 5% BC

Sensitivity analysis is provided as an additional robustness assessment
and does not replace the default identification criteria.

## 6. Automated visualization

Version 0.2.0 automatically generates graphical summaries of the advanced
analysis.

Generated figures include:

    results/figures/
    ├── hb_ranking.png
    ├── hb_topology_profiles.png
    ├── hb_vs_network_comparison.png
    ├── sensitivity_analysis.png
    └── topology_correlation_heatmap.png

These figures provide visual summaries of Hub-Bottleneck ranking,
topological profiles, network-level comparisons, sensitivity behavior,
and topology correlations.

---

# Input

HubBottleNet accepts topology data exported from Cytoscape
NetworkAnalyzer.

The input parser automatically detects common variations in column
names and standardizes them for analysis.

### Required parameters

- Node
- Degree
- Betweenness centrality

### Additional topology parameters

When available, the following parameters are retained and analyzed:

- Closeness centrality
- Clustering coefficient
- Neighborhood connectivity
- Number of undirected edges
- Radiality
- Topological coefficient
- STRING protein identifier

Additional NetworkAnalyzer metadata can also be retained by the input
parser.

---

# Input Formats

HubBottleNet supports commonly used tabular formats including:

- CSV
- TSV
- TXT
- XLSX
- XLS
- XLSM
- XLSB

The default input location is:

    data/networkanalyzer_input.csv

A different input file can be supplied using:

    python src/main.py --input path/to/input.csv

or:

    python src/main.py -i path/to/input.xlsx

---

# Installation

Clone the repository:

    git clone https://github.com/Mayankroy242/HubBottleNet.git

    cd HubBottleNet

Create the Conda environment:

    conda env create -f environment.yml

Activate the environment:

    conda activate hubbottlenet

---

# Usage

Place the Cytoscape NetworkAnalyzer topology file in the `data/`
directory.

For the default input filename:

    data/networkanalyzer_input.csv

Run:

    python src/main.py

HubBottleNet automatically performs the complete workflow, including:

1. Input detection and standardization
2. Dataset validation
3. Hub identification
4. Bottleneck identification
5. Hub-Bottleneck identification
6. Hub-Bottleneck ranking
7. Advanced topology analysis
8. Network comparison
9. Topology correlation analysis
10. Sensitivity analysis
11. Automated figure generation

No separate interactive selection of analysis stages is required.

---

# Output

HubBottleNet stores generated analysis results in:

    results/

The primary outputs include:

    results/hub_bottleneck_results.csv
    results/hub_bottleneck_ranked.csv
    results/hub_bottleneck_summary.txt

Advanced analysis outputs include:

    results/advanced_topology_results.csv
    results/hub_bottleneck_topology_profiles.csv
    results/hb_vs_network_comparison.csv
    results/topology_correlations.csv
    results/sensitivity_analysis.csv

Figures are generated in:

    results/figures/

with:

    hb_ranking.png
    hb_topology_profiles.png
    hb_vs_network_comparison.png
    sensitivity_analysis.png
    topology_correlation_heatmap.png

---

# Primary Results

## hub_bottleneck_results.csv

Contains the complete node-level dataset together with:

- Hub status
- Betweenness centrality rank
- Bottleneck status
- Hub-Bottleneck status
- Hub-Bottleneck rank
- Hub-Bottleneck score
- Hub strength
- Bottleneck strength
- Supporting ranks
- Topology percentile values

## hub_bottleneck_ranked.csv

Contains the identified Hub-Bottleneck nodes ranked according to the
combined H-B score.

## hub_bottleneck_summary.txt

Contains a text summary of:

- Number of nodes
- Average degree
- Degree standard deviation
- Hub threshold
- Bottleneck criterion
- Number of hubs
- Number of bottlenecks
- Number of Hub-Bottlenecks
- Identified Hub-Bottleneck genes

---

# Advanced Results

## advanced_topology_results.csv

Contains the complete network topology dataset together with
classification, ranking, and topology percentile information.

## hub_bottleneck_topology_profiles.csv

Contains the topology profiles of identified Hub-Bottleneck nodes.

## hb_vs_network_comparison.csv

Contains network-wide and Hub-Bottleneck mean topology values together
with relative enrichment values.

## topology_correlations.csv

Contains the pairwise topology correlation matrix.

## sensitivity_analysis.csv

Contains the results of parameter sensitivity analysis across different
hub threshold multipliers and bottleneck percentages.

---

# Example

A complete example dataset is provided in:

    example/networkanalyzer_input.xlsx

Expected v0.1 analysis outputs are provided in:

    example/expected_results/

The example demonstrates the core Hub-Bottleneck identification workflow.

---

# Project Structure

    HubBottleNet/
    ├── data/
    │   └── .gitkeep
    │
    ├── example/
    │   ├── networkanalyzer_input.xlsx
    │   └── expected_results/
    │       ├── hub_bottleneck_results.csv
    │       └── hub_bottleneck_summary.txt
    │
    ├── results/
    │   └── .gitkeep
    │
    ├── src/
    │   ├── advanced_analysis.py
    │   ├── hub_analysis.py
    │   ├── input_parser.py
    │   ├── main.py
    │   ├── test_input.py
    │   └── validation.py
    │
    ├── environment.yml
    ├── LICENSE
    ├── README.md
    └── .gitignore

Generated results and local test data are excluded from version control
through `.gitignore`.

---

# Development History

## Version 0.1.0

Initial stable HubBottleNet release.

Implemented:

- NetworkAnalyzer input handling
- Robust topology-column detection
- Dataset validation
- Hub identification
- Bottleneck identification
- Hub-Bottleneck identification
- Hub-Bottleneck ranking
- Result and summary generation

## Version 0.2.0

Advanced network-analysis extension.

Added:

- Network topology profiling
- Topology percentile analysis
- Hub-Bottleneck topology profiling
- Hub-Bottleneck vs network comparison
- Topology correlation analysis
- Parameter sensitivity analysis
- Automated figure generation
- Extended analysis outputs

---

# Development Roadmap

Future versions may include:

- Additional network centrality measures
- Network robustness and perturbation analysis
- Community/module analysis
- Network visualization and interactive exploration
- Cytoscape integration
- Expression-network integration
- Directionality and causality analysis
- Multi-network comparison
- Additional statistical validation
- Automated biological interpretation

---

# Citation

If you use HubBottleNet in your research, please cite:

Roy Chowdhury, M. (2026). HubBottleNet: A Python-based tool for
hub-bottleneck analysis of biological networks. Version 0.2.0. GitHub.

Repository:

    https://github.com/Mayankroy242/HubBottleNet

A formal software/research publication citation will be added when
available.

---

# License

HubBottleNet is released under the MIT License.

See the `LICENSE` file for the complete license text.

