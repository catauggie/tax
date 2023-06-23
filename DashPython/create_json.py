from dash import Dash, dcc, html, Input, Output, callback
import json

filter_options = {
    'причины': ['возврат/зачет', 'вычеты', 'документы'],
    'последствия': ['документы', 'МНК'],
    'Классификация НО действий НП': ['взаимозависимые организации', 'дробление бизнеса']
}

def make_label_value(filter_options):
    label_value = []
    for key, values in filter_options.items():
        options = []
        for i, value in enumerate(values):
            option = {'label': f'{key}_{i}', 'value': value}
            options.append(option)
        label_value.append(options)
    return label_value

label_value_lists = make_label_value(filter_options)

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.Div(id='dynamic-dropdowns'),
    html.Button('Create JSON', id='create-json-button'),
    html.Div(id='json-output'),
    html.Div(id='decoded-json-output')
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
    Output('json-output', 'children'),
    Output('decoded-json-output', 'children'),
    Input('create-json-button', 'n_clicks'),
    *[Input(f'demo-dropdown-{s}', 'value') for s in range(len(label_value_lists))]
)
def create_json(n_clicks, *selected_values):
    if n_clicks is None:
        return '', ''

    selected_items = {}
    for s, values in enumerate(selected_values):
        key = list(filter_options.keys())[s]
        selected_items[key] = values

    json_data = json.dumps(selected_items, indent=4, ensure_ascii=False)
    parsed_json = json.loads(json_data)
    return html.Pre(json_data), html.Pre(json.dumps(parsed_json, indent=4))


if __name__ == '__main__':
    app.run_server(debug=True)
