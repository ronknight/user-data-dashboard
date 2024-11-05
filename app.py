import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import base64
import io
from datetime import timedelta

# Load Excel data - replace 'data.xlsx' with the exact path to your file
excel_file_path = 'data.xlsx'
df = pd.read_excel(excel_file_path, sheet_name='Sheet1', header=None)

# Parse data to extract metrics and event data (including purchases and others)
metrics = {
    "First seen": "Oct 29, 2024 from Miami, United States",
    "Event count": 1326,
    "Purchase revenue": 2243.58,
    "Transactions": 2,
    "User engagement": "4h 08m",
    "click": 24,
    "begin_checkout": 17,
    "purchase": 15
}
metrics_df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])

# Comprehensive event data, including additional events like 'purchase' and others
all_event_data = {
    "Event Type": ["user_engagement", "page_view", "scroll", "view_item", "view_cart", 
                   "click", "begin_checkout", "purchase"],
    "Count": [408, 400, 318, 86, 25, 24, 17, 15]
}
all_event_df = pd.DataFrame(all_event_data)

# Simulate events over time data, with timestamps every 6 hours
base_dates = pd.date_range(start="2024-10-29 08:00", periods=5, freq="D")
timestamps = [dt + timedelta(hours=hour) for dt in base_dates for hour in range(0, 24, 6)]

events_over_time = {
    "Date": timestamps,
    "user_engagement": [100, 105, 98, 92, 80, 75, 89, 95, 78, 66] * (len(timestamps) // 10),
    "page_view": [90, 92, 88, 85, 79, 76, 83, 90, 72, 65] * (len(timestamps) // 10),
    "scroll": [70, 69, 68, 66, 61, 64, 67, 65, 63, 57] * (len(timestamps) // 10),
    "view_item": [20, 18, 19, 20, 22, 21, 20, 19, 18, 16] * (len(timestamps) // 10),
    "view_cart": [5, 4, 4, 5, 6, 6, 5, 4, 5, 3] * (len(timestamps) // 10),
    "click": [12, 10, 11, 13, 9, 8, 10, 12, 11, 9] * (len(timestamps) // 10),
    "begin_checkout": [7, 7, 6, 8, 9, 8, 6, 7, 5, 5] * (len(timestamps) // 10),
    "purchase": [3, 2, 3, 4, 3, 2, 4, 3, 3, 2] * (len(timestamps) // 10)
}

# Convert to DataFrame
events_time_df = pd.DataFrame(events_over_time)

# Image display setup (assume image_path is 'screenshot.png')
image_path = 'screenshot.png'  # replace with actual screenshot file path
image = Image.open(image_path)
buffered = io.BytesIO()
image.save(buffered, format="PNG")
encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

# Initialize Dash app with suppress_callback_exceptions
app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("User Activity Dashboard"),

    # Radio buttons for view selection
    html.Div([
        html.Label("Select View Mode:"),
        dcc.RadioItems(
            id='view-selection',
            options=[
                {'label': 'Stacked View', 'value': 'stacked'},
                {'label': 'Individual Pages', 'value': 'individual'}
            ],
            value='stacked',  # Default to stacked view
            inline=True
        )
    ]),

    # Content area for charts based on selected view mode
    html.Div(id='content-area')
])

# Callback to control content display based on view selection
@app.callback(
    Output('content-area', 'children'),
    Input('view-selection', 'value')
)
def display_content(view_mode):
    if view_mode == 'stacked':
        # Show all components stacked together
        return [
            html.H2("Summary Metrics"),
            html.Table([
                html.Tr([html.Th("Metric"), html.Th("Value")])] + 
                [html.Tr([html.Td(metrics_df["Metric"][i]), html.Td(metrics_df["Value"][i])]) for i in range(len(metrics_df))]
            ),
            html.H2("Uploaded Screenshot"),
            html.Img(src="data:image/png;base64," + encoded_image, style={"width": "80%", "height": "auto"}),

            # All charts displayed together
            html.H2("Event Type Counts"),
            dcc.Graph(figure=px.bar(all_event_df, x='Event Type', y='Count', title="Event Counts by Type")),
            html.H2("Events Over Time"),
            dcc.Graph(figure=generate_events_over_time_figure())
        ]
    else:
        # Show only one component at a time with dropdown to select which
        return [
            dcc.Dropdown(
                id='individual-chart-dropdown',
                options=[
                    {'label': 'Summary Metrics', 'value': 'metrics'},
                    {'label': 'Uploaded Screenshot', 'value': 'screenshot'},
                    {'label': 'Event Type Counts', 'value': 'event_counts'},
                    {'label': 'Events Over Time', 'value': 'events_over_time'}
                ],
                value='metrics',  # Default to the first option
                clearable=False
            ),
            html.Div(id='individual-chart')
        ]

# Callback to display individual chart based on dropdown selection in individual mode
@app.callback(
    Output('individual-chart', 'children'),
    Input('individual-chart-dropdown', 'value')
)
def display_individual_chart(selected_chart):
    if selected_chart == 'metrics':
        return [
            html.H2("Summary Metrics"),
            html.Table([
                html.Tr([html.Th("Metric"), html.Th("Value")])] + 
                [html.Tr([html.Td(metrics_df["Metric"][i]), html.Td(metrics_df["Value"][i])]) for i in range(len(metrics_df))]
            )
        ]
    elif selected_chart == 'screenshot':
        return [
            html.H2("Uploaded Screenshot"),
            html.Img(src="data:image/png;base64," + encoded_image, style={"width": "80%", "height": "auto"})
        ]
    elif selected_chart == 'event_counts':
        return [
            html.H2("Event Type Counts"),
            dcc.Graph(figure=px.bar(all_event_df, x='Event Type', y='Count', title="Event Counts by Type"))
        ]
    elif selected_chart == 'events_over_time':
        return [
            html.H2("Events Over Time"),
            dcc.Graph(figure=generate_events_over_time_figure())
        ]

# Helper function to generate the "Events Over Time" figure
def generate_events_over_time_figure():
    fig = make_subplots()
    for col in events_time_df.columns[1:]:  # Skip 'Date' column
        fig.add_trace(
            go.Scatter(x=events_time_df['Date'], y=events_time_df[col], mode='lines+markers', name=col)
        )
    fig.update_layout(
        title="Events Over Time",
        xaxis_title="Date and Time",
        yaxis_title="Event Count",
        xaxis_tickformat="%Y-%m-%d %H:%M"
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
