import pandas as pd

from input_parser import load_and_standardize
from validation import validate_dataset


def test_csv_input_loading(tmp_path):
    """Test CSV loading and topology-column detection."""

    test_file = tmp_path / "test_network.csv"

    data = pd.DataFrame({
        "Gene": ["AKT1", "EGFR", "TP53"],
        "Node Degree": [20, 30, 40],
        "Betweenness Centrality": [0.10, 0.20, 0.30],
        "Closeness Centrality": [0.50, 0.60, 0.70]
    })

    data.to_csv(
        test_file,
        index=False
    )

    df, detected = load_and_standardize(
        test_file
    )

    assert not df.empty

    assert "node" in df.columns
    assert "degree" in df.columns
    assert "bc" in df.columns
    assert "cc" in df.columns


def test_required_columns():
    """Test that essential H-B columns are available."""

    data = pd.DataFrame({
        "node": ["AKT1", "EGFR", "TP53"],
        "degree": [20, 30, 40],
        "bc": [0.10, 0.20, 0.30]
    })

    result = validate_dataset(data)

    assert "node" in result["data"].columns
    assert "degree" in result["data"].columns
    assert "bc" in result["data"].columns


def test_numeric_conversion():
    """Test conversion of topology values to numeric format."""

    data = pd.DataFrame({
        "node": ["AKT1", "EGFR"],
        "degree": ["20", "30"],
        "bc": ["0.10", "0.20"]
    })

    result = validate_dataset(data)

    assert pd.api.types.is_numeric_dtype(
        result["data"]["degree"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["data"]["bc"]
    )
