# -*- coding: utf-8 -*-
import re
import csv
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from translate import Translator
from word2number import w2n
from pdf2image import convert_from_path
import pytesseract
import os
from pdf2image import*

# Set the path to your Tesseract executable (change it if necessary)
pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_tin(text):
    tin_pattern = r"(?i)ИНН\s*(\d{10})"
    match = re.search(tin_pattern, text)
    if match:
        return match.group(1)
    else:
        return None


def extract_address(text):
    address_pattern = r"(?i)(\d{6})\s*(.*?)(\w+[\s\w]+)"
    match = re.search(address_pattern, text)
    if match:
        zip_code = match.group(1)
        street = match.group(2)
        city = match.group(3)
        return {"zip_code": zip_code, "street": street, "city": city}
    else:
        return None


def extract_patient_name(text):
    name_pattern = r"(?i)ФИО пациента:\s*(\S+\s\S+\s\S+)"
    match = re.search(name_pattern, text)
    if match:
        return match.group(1)
    else:
        return None


def extract_patient_tin(text):
    tin_pattern = r"(?i)ИНН налогоплательщика:\s*(\d{12})"
    match = re.search(tin_pattern, text)
    if match:
        return match.group(1)
    else:
        return None


def extract_cost(text):
    cost_pattern = r"(?i)(?:стоимость|стоимости|стоимостью):\s*(.*?)(?:\.|\n)"
    match = re.search(cost_pattern, text)
    if match:
        cost_sentence = match.group(1)
        cost_sentence_english = translate_to_english(cost_sentence)
        return cost_sentence_english
    else:
        return None


def translate_to_english(sentence):
    translator = Translator(from_lang='ru', to_lang='en')
    translation = translator.translate(sentence)
    return translation


def convert_sentence_to_number(sentence):
    words = sentence.split()
    number_words = []
    fractional_part = None
    for i, word in enumerate(words):
        if word == 'rubles':
            break
        elif word == 'kopecks':
            if i >= 3 and words[i-2].isdigit() and len(words[i-2]) == 2:
                fractional_part = words[i-2]
                number_words.append(words[i-3])  # Keep the word before "kopecks"
        try:
            number = w2n.word_to_num(word)
            number_words.append(str(number))
        except ValueError:
            number_words.append(word)
    result = " ".join(number_words)

    # Add the fractional part to the result if available
    if fractional_part is not None:
        result += " " + fractional_part + " kopecks"

    return result


def extract_digits(sentence):
    digits = []
    words = sentence.split()
    for word in words:
        if word.isdigit():
            digits.append(int(word))
    return digits


def sum_total_amount(sentence):
    words = sentence.split()
    total_amount = 0
    previous_number = 0

    for word in words:
        if word == 'rubles':
            break

        try:
            number = w2n.word_to_num(word)
            if number == 100:
                previous_number *= number
            elif number >= 1000:
                total_amount += previous_number * number
                previous_number = 0
            else:
                previous_number += number
        except ValueError:
            continue

    total_amount += previous_number

    return total_amount


def process_pdf_to_text(pdf_path):
    # Convert PDF pages to images and perform OCR
    pages = convert_from_path(pdf_path, dpi=300)  # Adjust the dpi if needed
    extracted_text = ""

    for i, page in enumerate(pages):
        try:
            # Perform OCR on the image to recognize the text
            text = pytesseract.image_to_string(page, lang='rus')

            # Append the extracted text to the result
            extracted_text += text

        except Exception as e:
            print(f'Error processing page {i + 1}: {str(e)}')

    return extracted_text


def process_text_file(text):
    # Process the extracted text to extract the desired information
    tin = extract_tin(text)
    address = extract_address(text)
    patient_name = extract_patient_name(text)
    patient_tin = extract_patient_tin(text)
    cost = extract_cost(text)
    amount = sum_total_amount(convert_sentence_to_number(cost)) + extract_digits(cost)[0] / 100

    result = {
        "tin": tin,
        "address": address,
        "patient_name": patient_name,
        "patient_tin": patient_tin,
        "cost": cost,
        "amount": amount
    }

    return result


def save_to_csv(results, csv_file_path):
    df = pd.DataFrame.from_records([results])
    df.to_csv(csv_file_path, index=False)


app = Dash(__name__)

app.layout = html.Div(
    className='container',
    style={
        'display': 'flex',
        'flex-direction': 'row',
    },
    children=[
        html.Div(
            className='column',
            style={
                'width': '50%',
                'padding': '20px',
            },
            children=[
                html.H1(
                    children="Проверь свою справку",
                    style={
                        'text-align': 'center',
                    }
                ),
                dcc.Upload(
                    id='upload-pdf',
                    className='upload-area',
                    style={
                        'border': '2px dashed gray',
                        'border-radius': '5px',
                        'padding': '20px',
                        'text-align': 'center',
                        'cursor': 'pointer',
                    },
                    children=html.Div([
                        html.Div(className='upload-icon'),
                        html.Div(['Перетащите сюда файл в формате PDF или ', html.A('выберите файл')],
                                 className='upload-text')
                    ]),
                    accept='.pdf',
                    multiple=False
                ),
                html.Div(id='selected-pdf', style={'margin-top': '20px'}),
                html.Button("Сохранить в CSV", id='save-csv-btn', disabled=True)
            ]
        ),
        html.Div(
            className='column',
            style={
                'width': '50%',
                'padding': '20px',
            },
            children=[
                html.Div(id='output-message')
            ]
        )
    ]
)

@app.callback(
    [Output('selected-pdf', 'children'), Output('output-message', 'children'), Output('save-csv-btn', 'disabled')],
    [Input('upload-pdf', 'contents')],
    [State('upload-pdf', 'filename')]
)
def process_uploaded_pdf(contents, filename):
    if contents is None:
        raise PreventUpdate

    _, content_string = contents.split(',')
    decoded_pdf = content_string.encode('utf-8')
    pdf_path = f'uploads/{filename}'

    with open(pdf_path, 'wb') as file:
        file.write(decoded_pdf)

    processed_text, text_file_path = process_pdf_to_text(pdf_path)

    results = process_text_file(text_file_path)

    csv_file_path = 'results.csv'
    save_to_csv(results, csv_file_path)

    selected_pdf = html.Div(
        children=[
            html.H3(f"Selected PDF: {filename}"),
            html.Pre(processed_text)
        ]
    )

    output_message = html.Div(
        children=[
            html.H3("Результаты обработки файла:"),
            html.Pre(f"ИНН медицинского учреждения: {results['tin']}"),
            html.Pre(f"Адрес медицинского учреждения: {results['address']}"),
            html.Pre(f"ФИО пациента: {results['patient_name']}"),
            html.Pre(f"ИНН пациента: {results['patient_tin']}"),
            html.Pre(f"Стоимость услуги: {results['cost']}"),
            html.Pre(f"Общая сумма: {results['amount']}"),
        ]
    )

    return selected_pdf, output_message, False


if __name__ == '__main__':
    app.run_server(debug=True)
