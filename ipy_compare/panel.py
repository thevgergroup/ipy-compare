import pandas as pd
import panel as pn
from .brand import footer_html

class Compare:
    def __init__(self, df, columns, measures=None, pagination=None):
        """
        Initialize the Compare class.

        Args:
            df (pd.DataFrame): The DataFrame to compare.
            columns (list): List of columns to compare.
            measures (dict): Dictionary of measures (e.g., overall, each).
            pagination (iterable or None): Custom pagination logic.
        """
        pn.extension()
        
        self.df = df
        self.columns = columns
        self.measures = measures or {}
        self.measurements = []
        self.radio_buttons = {}

        # Handle pagination
        if pagination is None:
            self.pagination = list(df.index)
        else:
            self.pagination = list(pagination)
        self.pagination_iter = iter(self.pagination)
        self.current_index = self.pagination[0] if self.pagination else None

        # Create main layout
        self.main_layout = pn.Column(sizing_mode='stretch_width')
        self._create_layout()
        
    def _create_layout(self):
        """Create the initial panel layout"""
        # Content area
        self.content_area = pn.Column(sizing_mode='stretch_width')
        
        # Navigation buttons
        self.prev_button = pn.widgets.Button(name='Previous', button_type='primary')
        self.submit_button = pn.widgets.Button(name='Submit', button_type='success')
        self.next_button = pn.widgets.Button(name='Submit & Next', button_type='primary')
        
        # Button callbacks
        self.prev_button.on_click(self._previous_row)
        self.submit_button.on_click(self._submit_measures)
        self.next_button.on_click(self._submit_and_next)
        
        # Navigation layout
        nav_buttons = pn.Row(
            self.prev_button,
            self.submit_button,
            self.next_button,
            sizing_mode='stretch_width'
        )
        
        # Assemble main layout
        self.main_layout.extend([
            self.content_area,
            nav_buttons,
            pn.pane.HTML(footer_html)
        ])
        
        self.render()
        
    def render(self):
        """Render the current state"""
        self.content_area.clear()
        
        if self.current_index is None:
            self.content_area.append(pn.pane.Markdown("## No more rows to compare."))
            return
            
        # Current row display
        row = self.df.iloc[self.current_index]
        self.content_area.append(self._generate_row_layout(row))
        
        # Add overall measures if specified
        if "overall" in self.measures:
            self._add_overall_measure_buttons()
            
    def _generate_row_layout(self, row):
        """Generate the layout for a single row"""
        columns = []
        
        for col in self.columns:
            col_layout = pn.Column(
                pn.pane.Markdown(f"**{col}**"),
                pn.pane.HTML(
                    f"<div style='white-space: pre-wrap; word-wrap: break-word; "
                    f"max-height: 200px; overflow: auto; padding: 10px; "
                    f"border: 1px solid #ccc;'>{row[col]}</div>"
                ),
                sizing_mode='stretch_width'
            )
            
            # Add measure radio buttons if "each" is specified
            if "each" in self.measures:
                radio = self._get_or_create_radio_buttons(col)
                col_layout.append(radio)
                
            columns.append(col_layout)
            
        return pn.Row(*columns, sizing_mode='stretch_width')
        
    def _get_or_create_radio_buttons(self, col):
        """Create or retrieve radio buttons for a column"""
        if col not in self.radio_buttons:
            options = [None] + self.measures.get("each", [])
            self.radio_buttons[col] = pn.widgets.RadioButtonGroup(
                options=options,
                value=None,
                name=f"{col} measure"
            )
        
        # Set saved value if it exists
        saved = self._get_saved_measure(col)
        if saved:
            self.radio_buttons[col].value = saved
            
        return self.radio_buttons[col]
        
    def _add_overall_measure_buttons(self):
        """Add overall measure radio buttons"""
        options = [None] + self.measures["overall"]
        if "overall" not in self.radio_buttons:
            self.radio_buttons["overall"] = pn.widgets.RadioButtonGroup(
                options=options,
                value=None,
                name="Overall measure"
            )
            
        saved = self._get_saved_measure("overall")
        if saved:
            self.radio_buttons["overall"].value = saved
            
        self.content_area.append(pn.Column(
            pn.pane.Markdown("### Overall Measures"),
            self.radio_buttons["overall"]
        ))

    def _get_saved_measure(self, column):
        """Get previously saved measure for the current row/column"""
        for measurement in self.measurements:
            if measurement["row_index"] == self.current_index and measurement.get("column") == column:
                return measurement["measure"]
        return None

    def _previous_row(self, event):
        """Handle previous button click"""
        idx = self.pagination.index(self.current_index)
        if idx > 0:
            self.current_index = self.pagination[idx - 1]
            self.pagination_iter = iter(self.pagination[idx:])
        self.render()

    def _submit_measures(self, event):
        """Handle submit button click"""
        self._save_or_update_measures()
        self.render()

    def _submit_and_next(self, event):
        """Handle submit and next button click"""
        self._save_or_update_measures()
        try:
            self.current_index = next(self.pagination_iter)
        except StopIteration:
            self.current_index = None
        self.render()

    def _save_or_update_measures(self):
        """Save or update measurements for the current row"""
        row_index = self.current_index
        if "overall" in self.radio_buttons:
            selected_overall = self.radio_buttons["overall"].value
            if selected_overall is not None:
                self._update_or_add_measure(row_index, None, None, selected_overall, "overall")
                
        for col in self.columns:
            if col in self.radio_buttons:
                selected_measure = self.radio_buttons[col].value
                if selected_measure is not None:
                    value = self.df.iloc[row_index][col]
                    self._update_or_add_measure(row_index, col, value, selected_measure, "column")

    def _update_or_add_measure(self, row_index, column, value, measure, measure_type):
        """Update existing measure or add new one"""
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
        """Get all measurements as a DataFrame"""
        return pd.DataFrame(self.measurements)

    @staticmethod
    def sample_indices(df, n, seed=None):
        """Get a sample of indices from the DataFrame"""
        return df.sample(n=n, random_state=seed).index.tolist()
        
    def servable(self):
        """Return the main layout for serving"""
        return self.main_layout
