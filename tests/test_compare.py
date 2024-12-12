import pytest
import pandas as pd
from ipy_compare.panel import Compare

@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'col1': ['A', 'B', 'C'],
        'col2': ['D', 'E', 'F'],
        'col3': ['G', 'H', 'I']
    })

@pytest.fixture
def sample_measures():
    """Create sample measures configuration."""
    return {
        'overall': ['Good', 'Bad', 'Neutral'],
        'each': ['Correct', 'Incorrect', 'Unsure']
    }

def test_compare_initialization(sample_df):
    """Test basic initialization of Compare class."""
    columns = ['col1', 'col2']
    compare = Compare(sample_df, columns)
    
    assert compare.df.equals(sample_df)
    assert compare.columns == columns
    assert compare.measures == {}
    assert compare.measurements == []
    assert compare.current_index == 0

def test_compare_with_measures(sample_df, sample_measures):
    """Test initialization with measures."""
    columns = ['col1', 'col2']
    compare = Compare(sample_df, columns, measures=sample_measures)
    
    assert compare.measures == sample_measures
    assert 'overall' in compare.measures
    assert 'each' in compare.measures

def test_sample_indices():
    """Test the sample_indices static method."""
    df = pd.DataFrame({'col1': range(100)})
    indices = Compare.sample_indices(df, n=10, seed=42)
    
    assert len(indices) == 10
    assert all(isinstance(idx, int) for idx in indices)
    assert len(set(indices)) == 10  # Check for uniqueness

def test_measurements_storage(sample_df, sample_measures):
    """Test that measurements are properly stored."""
    compare = Compare(sample_df, ['col1'], measures=sample_measures)
    
    # Simulate adding measurements
    compare._update_or_add_measure(
        row_index=0,
        column='col1',
        value='A',
        measure='Correct',
        measure_type='column'
    )
    
    measurements_df = compare.get_measurements()
    assert len(measurements_df) == 1
    assert measurements_df.iloc[0]['row_index'] == 0
    assert measurements_df.iloc[0]['measure'] == 'Correct'
    assert measurements_df.iloc[0]['column'] == 'col1'

def test_pagination_custom(sample_df):
    """Test custom pagination."""
    custom_pagination = [1, 2]  # Only look at second and third rows
    compare = Compare(sample_df, ['col1'], pagination=custom_pagination)
    
    assert compare.pagination == custom_pagination
    assert compare.current_index == 1  # Should start at first index in pagination

def test_update_existing_measure(sample_df, sample_measures):
    """Test updating an existing measure."""
    compare = Compare(sample_df, ['col1'], measures=sample_measures)
    
    # Add initial measure
    compare._update_or_add_measure(0, 'col1', 'A', 'Correct', 'column')
    
    # Update the measure
    compare._update_or_add_measure(0, 'col1', 'A', 'Incorrect', 'column')
    
    measurements_df = compare.get_measurements()
    assert len(measurements_df) == 1  # Should still only have one measurement
    assert measurements_df.iloc[0]['measure'] == 'Incorrect'  # Should be updated
 