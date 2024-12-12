# ipy-compare

`ipy-compare` is an interactive tool designed for use in Jupyter notebooks, enabling users to visually compare rows and columns of a DataFrame. It supports customizable measures, pagination, and repeatable sampling, with modular branding options for seamless integration.

## Features
- **Row and Column Comparison**: Supports both overall row-level measures and column-specific measures.
- **Pagination**: Navigate through rows using custom indices or iterators.
- **Repeatable Sampling**: Use a fixed random seed for consistent sampling.
- **Branding**: Add customizable branding to the footer, including a linkable logo and text.
- **Interactive Radio Buttons**: Visual indicators for selected measures.

---

## Installation

```bash
pip install ipy-compare
```

Clone or download the repository to include `ipy-compare` in your project.

---

## Usage

### Import and Initialize

```python
from ipy_compare import Compare
import pandas as pd

# Sample DataFrame
data = {
    'Column1': ['A', 'B', 'C'],
    'Column2': ['X', 'Y', 'Z'],
    'Column3': ['Apple', 'Fish swimming', 'Vrooom car']
}
df = pd.DataFrame(data)

# Define measures
measures = {
    "overall": ["Good", "Bad"],
    "each": ["Better", "Worse", "Neutral"]
}

# Initialize Compare
tool = Compare(df, columns=["Column1", "Column3"], measures=measures)
```

---

### Navigation and Interaction
1. Navigate between rows using the `Previous` and `Submit & Next` buttons.
2. Use the radio buttons to select measures for each column or for the overall row.
3. Capture measurements interactively, which can be retrieved programmatically.

---

### Custom Pagination
To specify a subset of rows or custom order:

```python
# Custom row order
custom_order = [2, 0, 1]

# Initialize Compare with custom pagination
tool = Compare(df, columns=["Column1", "Column3"], measures=measures, pagination=custom_order)
```

---

### Repeatable Sampling
To use random sampling with a fixed seed:

```python
# Get a random sample of rows
sampled_indices = Compare.sample_indices(df, n=2, seed=42)

# Initialize Compare with sampled indices
tool = Compare(df, columns=["Column1", "Column3"], measures=measures, pagination=sampled_indices)
```

---

### Retrieve Measurements
Once interactions are complete, retrieve the captured measurements:

```python
# Get measurements as a DataFrame
measurements = tool.get_measurements()
print(measurements)
```

**Example Output:**

| row_index | column   | value          | measure   | type    |
|-----------|----------|----------------|-----------|---------|
| 0         | None     | None           | Good      | overall |
| 0         | Column1  | A              | Better    | column  |
| 0         | Column3  | Apple          | Neutral   | column  |
| 1         | None     | None           | Bad       | overall |
| 1         | Column1  | B              | Worse     | column  |
| 1         | Column3  | Fish swimming  | Neutral   | column  |

---


---

## Advanced Options

### Custom Measures
Define your own measure categories:

```python
measures = {
    "overall": ["Excellent", "Poor"],
    "each": ["Correct", "Incorrect", "Not Sure"]
}
```

---

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---

## License
This project is licensed under the MIT License.

