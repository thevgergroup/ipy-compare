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
        Generates the layout for a single row, ensuring all columns are properly aligned.
        Adds borders between columns for better visual separation.
        Handles auto-sizing for cells and supports scrollbars for overflow content.
        """
        from ipywidgets import GridspecLayout

        # Create a grid layout for better alignment
        grid = GridspecLayout(3, len(self.columns), width="100%")

        # Add column headers with borders
        for i, col in enumerate(self.columns):
            grid[0, i] = widgets.HTML(
                value=f"<div style='text-align: center; font-weight: bold; padding: 5px; border-right: {'' if i == len(self.columns) - 1 else '1px solid #ccc'};'>{col}</div>",
                layout=widgets.Layout(width="auto", max_width="300px")
            )

        # Add row values with borders
        for i, col in enumerate(self.columns):
            grid[1, i] = widgets.HTML(
                value=f"<div style='white-space: pre-wrap; word-wrap: break-word; overflow: auto; max-width: 300px; max-height: 100px; padding: 5px; border-right: {'' if i == len(self.columns) - 1 else '1px solid #ccc'};'>{row[col]}</div>",
                layout=widgets.Layout(width="auto", max_width="300px", overflow="auto", height="auto")
            )

        # Add measure widgets directly (if "each" is provided in measures)
        if "each" in self.measures:
            for i, col in enumerate(self.columns):
                grid[2, i] = self._get_or_create_radio_buttons(col)

        return widgets.VBox(
            [grid],
            layout=widgets.Layout(
                border="2px solid #ccc",
                border_radius="8px",
                padding="10px",
                margin="10px",
            ),
        )

    def _get_or_create_radio_buttons(self, col):
        options = [None] + self.measures.get("each", [])
        if col not in self.radio_widgets:
            self.radio_widgets[col] = widgets.RadioButtons(
                options=options,
                value=None,
                layout=widgets.Layout(width="auto", max_width="300px")
            )
        saved = self._get_saved_measure(col)  # Preload saved selection if it exists
        self.radio_widgets[col].value = saved
        return self.radio_widgets[col]

    def _add_overall_measure_radio_buttons(self):
        display(HTML("<h4>Overall Measures:</h4>"))
        options = [None] + self.measures["overall"]
        if "overall" not in self.radio_widgets:
            self.radio_widgets["overall"] = widgets.RadioButtons(
                options=options,
                value=None,
                description="Select:",
                layout=widgets.Layout(width='auto')
            )
        saved = self._get_saved_measure("overall")
        self.radio_widgets["overall"].value = saved
        display(self.radio_widgets["overall"])

    def _get_saved_measure(self, column):
        for measurement in self.measurements:
            if measurement["row_index"] == self.current_index and measurement.get("column") == column:
                return measurement["measure"]
        return None

    def _add_footer(self):
        display(HTML(footer_html))

    def _next_row(self, _):
        """
        Move to the next row in the pagination iterator.
        """
        try:
            # Advance to the next index in pagination
            self.current_index = next(self.pagination_iter)
        except StopIteration:
            # If no more rows, set to None to indicate completion
            self.current_index = None
        self.render()  # Render the new state

    def _previous_row(self, _):
        """
        Move to the previous row and reset the pagination iterator to reflect the state.
        """
        idx = self.pagination.index(self.current_index)
        if idx > 0:
            self.current_index = self.pagination[idx - 1]
            self.pagination_iter = iter(self.pagination[idx:])  # Reinitialize iterator
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
        """
        Save or update the current row's measurements without advancing to the next row.
        """
        self._save_or_update_measures()
        self.render()  # Redraw the current row

    def _submit_and_next(self, _):
        """
        Save or update the current row's measurements and advance to the next row.
        """
        self._save_or_update_measures()
        self._next_row(None)

    def _save_or_update_measures(self):
        row_index = self.current_index
        if "overall" in self.radio_widgets:
            selected_overall = self.radio_widgets["overall"].value
            if selected_overall is not None:
                self._update_or_add_measure(row_index, None, None, selected_overall, "overall")
        for col in self.columns:
            if col in self.radio_widgets:
                selected_measure = self.radio_widgets[col].value
                if selected_measure is not None:
                    value = self.df.iloc[row_index][col]
                    self._update_or_add_measure(row_index, col, value, selected_measure, "column")

    def _update_or_add_measure(self, row_index, column, value, measure, measure_type):
        for existing in self.measurements:
            if existing["row_index"] == row_index and existing.get("column") == column and existing["type"] == measure_type:
                existing["measure"] = measure
                return
        self.measurements.append({
            "row_index": row_index,
            "column": column,
            "value": value,
            "measure": measure,
            "type": measure_type
        })

    def get_measurements(self):
        return pd.DataFrame(self.measurements)

    @staticmethod
    def sample_indices(df, n, seed=None):
        return df.sample(n=n, random_state=seed).index.tolist()
