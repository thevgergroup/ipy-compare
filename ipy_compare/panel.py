import pandas as pd
from .brand import footer_html  # Import footer_html from brand.py
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output


class Compare:
    def __init__(self, df, columns, measures=None, pagination=None):
        """
        Initialize the Compare class.

        Args:
            df (pd.DataFrame): The DataFrame to compare.
            columns (list): List of columns to compare.
            measures (dict): Dictionary of measures (e.g., overall, each).
            pagination (iterable or None): Custom pagination logic (e.g., list of ilocs or iterator).
        """
        self.df = df
        self.columns = columns
        self.measures = measures or {}
        self.measurements = []
        self.radio_widgets = {}

        # Handle pagination logic
        if pagination is None:
            self.pagination = list(df.index)  # Default: all rows
        else:
            self.pagination = list(pagination)
        self.pagination_iter = iter(self.pagination)  # Iterator for navigation
        self.current_index = self.pagination[0] if self.pagination else None

        self._output = widgets.Output()
        display(self._output)
        self.render()

    def render(self):
        """
        Renders the current row with all elements: values, measures, navigation, and footer.
        """
        with self._output:
            clear_output(wait=True)
            if self.current_index is None:
                display(HTML("<h3>No more rows to compare.</h3>"))
                return

            # Display current row
            row = self.df.iloc[self.current_index]
            container = self._generate_row_html(row)
            display(container)

            # Add overall measure radio buttons if "overall" is provided
            if "overall" in self.measures:
                self._add_overall_measure_radio_buttons()

            # Add navigation and submission buttons
            self._add_navigation_buttons()

            # Add branding footer
            self._add_footer()

    def _generate_row_html(self, row):
        """
        Generates the layout for a single row, with values and measures directly under each column.
        """
        # Create a container for the row
        container = widgets.VBox()

        # Create a row for column headers
        header_row = widgets.HBox([widgets.Label(value=f"{col}", layout=widgets.Layout(width="120px")) for col in self.columns])

        # Create a row for values
        value_row = widgets.HBox([widgets.Label(value=f"{row[col]}", layout=widgets.Layout(width="120px")) for col in self.columns])

        # Create a row for radio buttons (if "each" is provided in measures)
        if "each" in self.measures:
            measure_row = widgets.HBox()
            for col in self.columns:
                options = [None] + self.measures["each"]
                if col not in self.radio_widgets:
                    self.radio_widgets[col] = widgets.RadioButtons(
                        options=options,
                        value=None,
                        layout=widgets.Layout(width="120px")
                    )
                saved = self._get_saved_measure(col)
                self.radio_widgets[col].value = saved
                measure_row.children += (self.radio_widgets[col],)
        else:
            measure_row = widgets.HBox([])

        # Add all rows to the container
        container.children = [header_row, value_row, measure_row]
        return container

    def _add_overall_measure_radio_buttons(self):
        """
        Displays the radio buttons for overall measures.
        """
        display(HTML("<h4>Overall Measures:</h4>"))
        options = [None] + self.measures["overall"]
        if "overall" not in self.radio_widgets:
            self.radio_widgets["overall"] = widgets.RadioButtons(
                options=options,
                value=None,  # No default selection
                description="Select:",
                layout=widgets.Layout(width='auto')  # Adjust layout as needed
            )
        # Preload saved selection if it exists
        saved = self._get_saved_measure("overall")
        self.radio_widgets["overall"].value = saved
        display(self.radio_widgets["overall"])

    def _get_saved_measure(self, column):
        """
        Retrieve the saved measure for the current row and column (or overall).
        """
        for measurement in self.measurements:
            if measurement["row_index"] == self.current_index and measurement.get("column") == column:
                return measurement["measure"]
        return None

    def _add_footer(self):
        """Display footer with branding."""
        display(HTML(footer_html))  # Use the imported footer_html variable

    def _next_row(self, _):
        try:
            self.current_index = next(self.pagination_iter)
            self.render()
        except StopIteration:
            self.current_index = None
            self.render()

    def _previous_row(self, _):
        # Reset pagination iterator to current row
        idx = self.pagination.index(self.current_index)
        if idx > 0:
            self.current_index = self.pagination[idx - 1]
            self.pagination_iter = iter(self.pagination[idx:])
            self.render()

    def _add_navigation_buttons(self):
        prev_button = widgets.Button(description="Previous")
        submit_button = widgets.Button(description="Submit")
        submit_next_button = widgets.Button(description="Submit & Next")

        prev_button.on_click(self._previous_row)
        submit_button.on_click(self._submit_measures)
        submit_next_button.on_click(self._submit_and_next)

        display(widgets.HBox([prev_button, submit_button, submit_next_button]))

    def _submit_measures(self, _):
        self._save_or_update_measures()

    def _submit_and_next(self, _):
        self._save_or_update_measures()
        self._next_row(None)

    def _save_or_update_measures(self):
        row_index = self.current_index
        # Update overall measure
        if "overall" in self.radio_widgets:
            selected_overall = self.radio_widgets["overall"].value
            if selected_overall is not None:  # Ensure a selection was made
                self._update_or_add_measure(row_index, None, None, selected_overall, "overall")
        # Update each column measure
        for col in self.columns:
            if col in self.radio_widgets:
                selected_measure = self.radio_widgets[col].value
                if selected_measure is not None:  # Ensure a selection was made
                    value = self.df.iloc[row_index][col]
                    self._update_or_add_measure(row_index, col, value, selected_measure, "column")

    def _update_or_add_measure(self, row_index, column, value, measure, measure_type):
        """Update an existing measure or add a new one."""
        for existing in self.measurements:
            if (
                existing["row_index"] == row_index
                and existing.get("column") == column
                and existing["type"] == measure_type
            ):
                # Update the existing measure
                existing["measure"] = measure
                return
        # Add a new measure if not found
        self.measurements.append({
            "row_index": row_index,
            "column": column,
            "value": value,
            "measure": measure,
            "type": measure_type  # Distinguish between overall and column-specific
        })

    def get_measurements(self):
        """
        Returns the captured measurements as a DataFrame for easier analysis.
        """
        return pd.DataFrame(self.measurements)

    @staticmethod
    def sample_indices(df, n, seed=None):
        """
        Sample row indices from a DataFrame with a fixed seed.

        Args:
            df (pd.DataFrame): The DataFrame to sample.
            n (int): Number of rows to sample.
            seed (int or None): Random seed for repeatability.

        Returns:
            list: List of sampled row indices.
        """
        return df.sample(n=n, random_state=seed).index.tolist()
