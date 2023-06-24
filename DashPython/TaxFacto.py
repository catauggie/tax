# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, Input, Output, callback
import json
import pandas as pd
import plotly.express as px

filter_options = {
        'Причины': ['возврат/зачет', 'вычеты', 'документы', 'льготы', 'недоимка', 'расчеты', 'схемы'],
        'Последствия': ['документы', 'МНК', 'отказ в возврате/зачете', 'отказ в вычете', 'отказ в льготе', 'штрафные санкции'],
        'Классификация НО действий НП': ['взаимозависимые организации', 'дробление бизнеса', 'искажение сведений о фактах хозяйственной жизни', 'минимальные суммы налогов к уплате', 'минимальный предельный срок владения объектом недвижимого имущества', 'минимальный размер оплаты труда', 'минимизация налоговых обязательств', 'недостоверные сведения', 'необоснованная налоговая выгода (экономия)', 'непроявление должной осмотрительности', 'нереальность хозяйственных операций', 'осуществление реальной хозяйственной деятельности', 'признаки недобросовестности', 'признаки технической компании', 'признаки транзитной компании', 'проблемный контрагент', 'процедура банкротства', 'согласованность действий', 'сумма исчисленного минимального налога', 'схема ухода от налогообложения', 'уклонение от уплаты налогов', 'фиктивный документооборот'],
        'Обстоятельства НП': ['аренда машин и оборудования', 'аренда недвижимого имущества', 'безвозмездная сделка', 'владение и пользование недвижимым имуществом', 'водоснабжение и водоотведение', 'газоснабжение', 'деятельность по эксплуатации автомобильных дорог', 'добыча (переработка) углеводородов', 'добыча полезных ископаемых', 'изъятие земельных участков и объектов недвижимого имущества для государственных нужд', 'инвестиционные правоотношения', 'использование информационных ресурсов', 'использование программного обеспечения', 'кадастровая стоимость', 'квалификация недвижимого и движимого имущества', 'купля-продажа недвижимого имущества', 'ликвидация выводимых из эксплуатации основных средств', 'ликвидация юридического лица', 'медицинская деятельность', 'оборот спиртосодержащей продукции', 'общественные и некоммерческие организации', 'оказание бытовых услуг населению', 'определение качества товарного продукта', 'оптовая торговля', 'отправление почтовой корреспонденции', 'оформление договоров займа', 'перевозка грузов и пассажиров', 'поставка (учет) тепловой энергии, теплоизоляция', 'поставка грунта', 'поставка каменного угля', 'поставка материалов', 'поставка нефтепродуктов (добыча нефти)', 'поставка товаров', 'поставка топлива', 'предоставление продуктов питания', 'продажа машин и оборудования', 'регистрация права на недвижимое имущество', 'реестр кредиторов', 'реконструкция (ремонт) объектов недвижимости', 'реорганизация юридического лица', 'розничная торговля', 'складская и логистическая деятельность', 'строительство объектов недвижимости', 'субсидии', 'транспортировка и размещение отходов', 'транспортные средства в собственности', 'трудовые правоотношения', 'трудовые ресурсы', 'услуги доставки', 'экспорт и импорт'],
        'Штраф (статья)': ['пункт 1 статьи 119 НК РФ', 'пункт 1 статьи 122 НК РФ', 'пункт 1 статьи 126 НК РФ', 'пункт 1 статьи 134 НК РФ', 'пункт 3 статьи 122 НК РФ', 'пункту статьи 122 НК РФ', 'статьи 126.1 и 135 НК РФ', 'статьи 129.3 и 129 НК РФ', 'статья 119 НК РФ', 'статья 120 НК РФ', 'статья 122 НК РФ', 'статья 123 НК РФ', 'статья 126 НК РФ', 'статья 126.1 НК РФ', 'статья 129.1 НК РФ', 'статья 129.6 НК РФ'],
        'Эпизод (статья)': ['пункт 1 статьи 265 НК РФ', 'пункт 1 статьи 45 НК РФ', 'пункт 1 статьи 80 НК РФ', 'пункт 2 статьи 265 НК РФ', 'пункт 2 статьи 266 НК РФ', 'пункт 2 статьи 272 НК РФ', 'пункт 2 статьи 45 НК РФ', 'пункт 3 статьи 45 НК РФ', 'пункт 4 статьи 416 НК РФ', 'пункт 6 статьи 78 НК РФ', 'пункт 6 статьи 80 НК РФ', 'пункт 7 статьи 78 НК РФ', 'статьи 272 и 54 НК РФ', 'статьи 78 и 79 НК РФ', 'статья 100 НК РФ', 'статья 101 НК РФ', 'статья 101.2 НК РФ', 'статья 258 НК РФ', 'статья 266 НК РФ', 'статья 283 НК РФ', 'статья 381 НК РФ', 'статья 45 НК РФ', 'статья 46 НК РФ', 'статья 54.1 НК РФ', 'статья 69 НК РФ', 'статья 70 НК РФ', 'статья 78 НК РФ', 'статья 88 НК РФ', 'статья 90 НК РФ', 'статья 92 НК РФ', 'статья 93 НК РФ', 'статья 93.1 НК РФ', 'статья 95 НК РФ'],
        'Тема прецедента': ['авансовые платежи', 'ввоз и вывоз товаров', 'взыскание неосновательного обогащения', 'вычет (возмещение)', 'действия контрагента', 'доказывание вины', 'доходы от имущества', 'доходы физических лиц', 'злоупотребление правом', 'излишне уплаченный (взысканный) налог', 'истребование документов', 'кадастровая стоимость', 'налоговые декларации', 'налоговые льготы', 'налоговые ставки', 'налоговое резидентство', 'недополучение дохода', 'некоммерческие организации', 'неплательщики налога', 'неправомерная налогообложение', 'неправомерные решения и действия органов', 'облагаемая база налогообложения', 'облагаемый период', 'обязательная проверка', 'оспаривание налоговых решений', 'оспаривание решений налоговых органов', 'ответственность за нарушение налогового законодательства', 'отсутствие контроля налоговых платежей', 'понятие налогового правонарушения', 'порядок и сроки предоставления налоговой отчетности', 'представительство в налоговых органах', 'применение и толкование налогового законодательства', 'процедура предъявления налоговых требований', 'распределение налоговых доходов', 'система налогообложения', 'снижение налоговой нагрузки', 'соответствие налоговому законодательству', 'спорные вопросы налогообложения', 'споры о налоговых обязательствах', 'споры о праве собственности', 'споры о размере налоговых обязательств', 'статус налогоплательщика', 'статус налогового агента', 'требования налогового законодательства', 'трудовые отношения', 'удержание налога', 'уплата налога', 'уступка налоговых прав', 'утратившие силу нормативные акты', 'факторы учета в налоговом законодательстве'],
      }

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

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Nav(
        className='navbar navbar-expand-lg navbar-dark bg-dark',
        children=[
            html.A('Page 1', className='navbar-brand', href='/page-1'),
            html.A('Page 2', className='navbar-brand', href='/page-2'),
        ]
    ),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def render_page_content(pathname):
    if pathname == '/page-1':
        return html.Div([
            html.Div(id='dynamic-dropdowns'),
            html.Div(id='decoded-json-output'),
            html.Div(id='table-info'),
            html.Div(id='table-output', style={'maxHeight': '400px', 'overflow': 'scroll'}),
            dcc.Graph(id='pie-chart'),
            dcc.Graph(id='bar-chart'),
            dcc.Graph(id='case-number-bar-chart')
        ])
    elif pathname == '/page-2':
        return html.Div([
            html.H1('Page 2'),
            html.P('This is an empty page.')
        ])
    else:
        return html.Div([
            html.H1('404 - Page not found')
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
    Output('table-info', 'children'),
    Output('table-output', 'children'),
    Output('pie-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('case-number-bar-chart', 'figure'),
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

    selected_data = pd.concat(sort_by(res, 'Номер дела')).drop_duplicates()

    # Convert selected data to an HTML table with scrolling
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in selected_data[['Номер дела', 'Прецедент']].columns])] +
        # Rows
        [html.Tr([html.Td(selected_data[['Номер дела', 'Прецедент']].iloc[i][col]) for col in selected_data[['Номер дела', 'Прецедент']].columns]) for i in
         range(len(selected_data[['Номер дела', 'Прецедент']]))],
        style={'width': '100%'}
    )

    # Create a pie chart for the column 'Категория спора'
    pie_chart = px.pie(selected_data, names='Категория спора')

    # Create a bar chart for the column 'law_court' with color based on a numerical variable
    bar_chart = px.bar(selected_data['law_court'].value_counts())

    # Create a bar chart for the 'case_number' column
    case_number_bar_chart = px.bar(selected_data['Номер дела'].value_counts())

    table_info = html.P(f"Число записей в таблице: {len(selected_data)}")

    return html.Pre(parsed_json), table_info, table, pie_chart, bar_chart, case_number_bar_chart

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
