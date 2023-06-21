import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, ALL


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

json_data = {
    "Причины": ["возврат/зачет", "вычеты", "документы", "льготы", "недоимка", "расчеты", "схемы"],
    "Следствия": ["документы", "МНК", "отказ в возврате/зачете", "отказ в вычете", "отказ в льготе", "штрафные санкции"],
    "Классификация НО действий НП": ["взаимозависимые организации", "дробление бизнеса"]
}

navbar_items = []
for category, values in json_data.items():
    dropdown_items = [
        dbc.DropdownMenuItem(
            item,
            id={"type": "navbar-item", "index": f"{category}-{item}"},
        )
        for item in values
    ]
    navbar_items.append(
        dbc.NavItem(
            dbc.DropdownMenu(
                dropdown_items,
                label=category,
                nav=True,
                in_navbar=True,
                className="dropdown-toggle",
            )
        )
    )

app.layout = dbc.Container(
    [
        dbc.Card(
            [
                dbc.CardHeader("Dropzone"),
                dbc.CardBody(
                    [
                        dcc.Upload(
                            id="dropdown-dropzone",
                            children=html.Div([
                                "Drag and drop or ",
                                html.A("click to select files")
                            ]),
                            style={
                                "width": "100%",
                                "height": "150px",
                                "lineHeight": "150px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px"
                            },
                            multiple=True
                        ),
                        html.Div(id="selected-values-output", className="dragndrop-output")
                    ]
                ),
            ],
            style={"margin-top": "20px"},
        ),
        dbc.Navbar(
            [
                dbc.Container(
                    [
                        dbc.NavbarBrand("Navbar", className="navbar-brand"),
                        dbc.Nav(navbar_items, className="navbar-nav", id="navbar"),
                    ],
                    fluid=True,
                )
            ],
            color="light",
            light=True,
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("selected-values-output", "children"),
    [Input({"type": "navbar-item", "index": ALL}, "n_clicks"),
     Input({"type": "selected-value-button", "index": ALL}, "n_clicks")],
    [State("selected-values-output", "children"),
     State({"type": "selected-value-button", "index": ALL}, "n_clicks"),
     State({"type": "selected-value-button", "index": ALL}, "id")],
)
def update_selected_values(navbar_n_clicks, button_n_clicks, selected_values_output, button_clicks, button_ids):
    ctx = dash.callback_context
    triggered_prop_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if selected_values_output is None:
        selected_values_output = []

    if triggered_prop_id.startswith("navbar-item"):
        selected_values = [prop_id.split("-")[-1] for prop_id in triggered_prop_id]
        selected_values_output.extend(selected_values)
    else:
        if button_clicks:
            for button_id, button_click in zip(button_ids, button_clicks):
                if button_click is not None and button_click > 0:
                    selected_values_output.remove(button_id["index"])

    if selected_values_output:
        return html.Div(
            [
                dbc.Button(item_value, outline=True, color="primary", className="selected-value-button",
                           id={"type": "selected-value-button", "index": str(item_value)})
                for item_value in selected_values_output
            ]
        )
    else:
        return html.Div("No items selected")








if __name__ == "__main__":
    app.run_server(debug=True)
