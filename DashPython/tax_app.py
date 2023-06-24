from dash import Dash, dcc, html, Input, Output, callback
import json
import pandas as pd
import plotly.express as px

filter_options = {
    'причины': ['возврат/зачет', 'вычеты', 'документы', 'льготы', 'недоимка', 'расчеты', 'схемы'],
    'последствия': ['документы', 'МНК', 'отказ в возврате/зачете', 'отказ в вычете', 'отказ  в льготе', 'штрафные санкции'],
    'Классификация НО действий НП': ['взаимозависимые организации', 'дробление бизнеса']}

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
    html.Div(id='table-output', style={'maxHeight': '400px', 'overflow': 'scroll'}),
    dcc.Graph(id='pie-chart'),
    dcc.Graph(id='bar-chart')
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
    Output('pie-chart', 'figure'),
    Output('bar-chart', 'figure'),
    [Input(f'demo-dropdown-{s}', 'value') for s in range(len(label_value_lists))]
)
def create_json(*selected_values):
    selected_items = {}
    for s, values in enumerate(selected_values):
        key = list(filter_options.keys())[s]
        selected_items[key] = values

    parsed_json = json.dumps(selected_items, indent=4, ensure_ascii=False)

    # Process selected data using the select_method function
    reduced_json = popping_null_json(json.loads(parsed_json))
    res = select_method(df, reduced_json)

    selected_data = pd.concat(sort_by(res, 'case_number')).drop_duplicates()

    # Convert selected data to an HTML table with scrolling
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in selected_data[['case_number', 'why_argument']].columns])] +
        # Rows
        [html.Tr([html.Td(selected_data[['case_number', 'why_argument']].iloc[i][col]) for col in selected_data[['case_number', 'why_argument']].columns]) for i in
         range(len(selected_data[['case_number', 'why_argument']]))],
        style={'width': '100%'}
    )

    # Create a pie chart for the column 'Категория спора'
    pie_chart = px.pie(selected_data, names='Категория спора')

    # Create a bar chart for the column 'law_court' with color based on a numerical variable
    bar_chart = px.bar(selected_data['law_court'].value_counts())

    return html.Pre(parsed_json), table, pie_chart, bar_chart

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


def sort_by(data, col_by_group):
    col_by_group_list = pd.DataFrame(data[col_by_group].value_counts())
    data_col_by_group_list = []
    for s in range(len(col_by_group_list)):
        data_col_by_group_s = data[data[col_by_group] == list(col_by_group_list.index)[s]]
        data_col_by_group_list.append(data_col_by_group_s)
    return data_col_by_group_list

def popping_null_json(null_json):
    values_list = list(null_json.values())

    empty_index = []
    for v in range(len(values_list)):
        if values_list[v] == [] or values_list[v] == None:
            empty_index.append(v)

    json_without_null = {k: v for i, (k, v) in enumerate(null_json.items()) if i not in empty_index}
    return json_without_null

if __name__ == '__main__':
    app.run_server(debug=True)
