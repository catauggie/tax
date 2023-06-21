import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc

# Function to filter data
def select_method(data, reduced_json):
    selected_data = []
    for c1 in range(len(list(reduced_json.keys()))):
        selected_data_by_topic = []
        for c2 in range(len(reduced_json[list(reduced_json.keys())[c1]])):
            data_by_topic_item = data[data[list(reduced_json.keys())[c1]] == reduced_json[list(reduced_json.keys())[c1]][c2]]
            selected_data_by_topic.append(data_by_topic_item)
        selected_data.append(selected_data_by_topic)

    concat_list = []
    for c in range(len(selected_data)):
        concat_c = pd.concat(selected_data[c]).drop_duplicates()
        concat_list.append(concat_c)

    final_result = pd.concat(concat_list).drop_duplicates()

    return final_result

# Read the data from the provided link
data = pd.read_excel('https://github.com/catauggie/ChatGPT/blob/main/%D0%A1%D0%A3%D0%94%D0%AB_PowerBI.xlsx', engine='openpyxl')

# Define filter options
filter_options = {
    'причины': ['возврат/зачет', 'вычеты', 'документы'],
    'последствия': ['документы', 'МНК'],
    'Классификация НО действий НП': ['взаимозависимые организации', 'дробление бизнеса']
}

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container(
    children=[
        html.H1("Dashboard"),
        html.H2("Table"),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        id="filter-div",
                        children=[
                            html.H3("Filter"),
                            dcc.Dropdown(
                                id="dropdown-toggle",
                                options=[{"label": key, "value": key} for key in filter_options.keys()],
                                value=None,
                                multi=True
                            ),
                            dcc.Dropdown(
                                id="dropdown-item",
                                options=[],
                                value=None,
                                multi=True
                            ),
                        ]
                    ),
                    md=4
                ),
                dbc.Col(
                    dash_table.DataTable(
                        id="table",
                        columns=[
                            {"name": "Case Number", "id": "case_number"},
                            {"name": "Why Argument", "id": "why_argument"}
                        ],
                        style_cell={"textAlign": "left"},
                        style_header={
                            "backgroundColor": "rgb(230, 230, 230)",
                            "fontWeight": "bold"
                        },
                        fixed_rows={"headers": True},
                        style_table={
                            "height": "400px",
                            "overflowY": "auto",
                            "overflowX": "auto"
                        },
                        virtualization=True
                    ),
                    md=8
                ),
            ],
            align="center"
        )
    ],
    className="mt-4"
)

# Callback to update the dropdown items based on the selected toggle value
@app.callback(
    dash.dependencies.Output('dropdown-item', 'options'),
    [dash.dependencies.Input('dropdown-toggle', 'value')]
)
def update_dropdown_items(selected_values):
    options = []
    if selected_values:
        for key in selected_values:
            options.extend([{"label": val, "value": val} for val in filter_options.get(key, [])])
    return options

# Callback to update the table based on the selected dropdown values
@app.callback(
    dash.dependencies.Output('table', 'data'),
    [dash.dependencies.Input('dropdown-item', 'value')]
)
def update_table_data(selected_values):
    reduced_json = {}
    for key in filter_options.keys():
        values = filter_options[key]
        if selected_values:
            reduced_json[key] = [val for val in values if val in selected_values]
        else:
            reduced_json[key] = []

    if selected_values:
        filtered_data = select_method(data, reduced_json)
        return filtered_data[["case_number", "why_argument"]].to_dict("records")
    else:
        return []

# Run the Dash app
if __name__ == '__main__':
    app.run_server()
