from dash import Dash, dcc, html, Input, Output, callback
import json
import pandas as pd

filter_options = {
    'причины': ['возврат/зачет', 'вычеты', 'документы'],
    'последствия': ['документы', 'МНК']}#,
    #'Классификация НО действий НП': ['взаимозависимые организации', 'дробление бизнеса']}

def make_label_value(filter_options):
    label_value = []
    for key, values in filter_options.items():
        options = []
        for i, value in enumerate(values):
            option = {'label': value, 'value': value}
            options.append(option)
        label_value.append(options)
    return label_value

label_value_lists = make_label_value(filter_options)

# Load data from Excel file
df = pd.read_excel(r'D:\python\DashPython\СУДЫ_PowerBI.xlsx')

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.Div(id='dynamic-dropdowns'),
    html.Div(id='decoded-json-output'),
    html.Div(id='table-output')
])

@app.callback(
    Output('dynamic-dropdowns', 'children'),
    Input('dynamic-dropdowns', 'id')
)
def generate_dropdowns(_):
    dropdowns = []
    for l in range(len(label_value_lists)):
        dropdown = html.Div([
            dcc.Dropdown(
                options=label_value_lists[l],
                id=f'demo-dropdown-{l}',
                placeholder=f"{list(filter_options.keys())[l]}",
                multi=True,
            ),
            html.Div(id=f'dd-output-container-{l}')
        ])
        dropdowns.append(dropdown)
    return dropdowns

@app.callback(
    Output('decoded-json-output', 'children'),
    Output('table-output', 'children'),
    [Input(f'demo-dropdown-{s}', 'value') for s in range(len(label_value_lists))]
)
def create_json(*selected_values):
    selected_items = {}
    for s, values in enumerate(selected_values):
        key = list(filter_options.keys())[s]
        selected_items[key] = values

    parsed_json = json.dumps(selected_items, indent=4, ensure_ascii=False)

    # Process selected data using the select_method function
    reduced_json = json.loads(parsed_json)
    selected_data = select_method(df, reduced_json)[['case_number', 'why_argument']]

    # Convert selected data to an HTML table
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in selected_data.columns])] +
        # Rows
        [html.Tr([html.Td(selected_data.iloc[i][col]) for col in selected_data.columns]) for i in range(len(selected_data))]
    )

    return html.Pre(parsed_json), table

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


if __name__ == '__main__':
    app.run_server(debug=True)
