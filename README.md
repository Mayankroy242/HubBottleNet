# HubBottleNet

HubBottleNet is a Python-based network analysis tool for systematic
identification of hub, bottleneck, and hub-bottleneck genes from
Cytoscape NetworkAnalyzer topology data.

## Current Version

Version 0.1 — Hub-Bottleneck Analysis

## Methodology

HubBottleNet implements the following methodology:

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

A node is classified as a Hub-Bottleneck only when it satisfies BOTH:

1. Degree >= AD + 2 × SD
2. Belongs to the top 5% of BC

## Input

HubBottleNet accepts an Excel file containing topology parameters
exported from Cytoscape NetworkAnalyzer.

The input parser automatically detects common variations in column
names.

Required parameters:

- Node
- Degree
- Betweenness centrality

Additional NetworkAnalyzer parameters are retained when available,
including:

- Closeness centrality
- Clustering coefficient
- Neighborhood connectivity
- Number of undirected edges
- Radiality
- Topological coefficient

## Installation

Clone the repository:

    git clone https://github.com/YOUR_USERNAME/HubBottleNet.git

    cd HubBottleNet

Create the Conda environment:

    conda env create -f environment.yml

Activate the environment:

    conda activate hubbottlenet

## Usage

Place the NetworkAnalyzer Excel file in:

    data/

The default input filename is:

    data/networkanalyzer_input.xlsx

Run:

    python src/main.py

## Output

HubBottleNet generates:

    results/hub_bottleneck_results.csv
    results/hub_bottleneck_summary.txt

The CSV contains the topology parameters together with:

- Hub status
- Betweenness centrality rank
- Bottleneck status
- Hub-Bottleneck status

## Example

A complete example dataset and expected results are provided in:

    example/

The example reproduces the Hub-Bottleneck analysis described by the
implemented methodology.

## Project Structure

    HubBottleNet/
    ├── data/
    ├── example/
    │   └── expected_results/
    ├── results/
    ├── src/
    ├── environment.yml
    ├── .gitignore
    └── README.md

## Development Roadmap

Future versions may include:

- Additional centrality-based criteria
- Network robustness analysis
- Sensitivity analysis
- Advanced network visualization
- Cytoscape integration
- Expression-network analysis
- Directionality/causality analysis

## Citation

Citation information will be added with the first software publication.

## License

License information will be added before public release.
