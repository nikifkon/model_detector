from datetime import datetime

import click

from algorithms.final import Final
from connectors.production import ProductionConnector
from utils import json_loads

# Производитель такой же
# Кода товара нет


@click.command()
def compare_to_characteristics():
    with open('metrics/reports/characteristics_report_' + str(datetime.utcnow().strftime("%d_%m_%Y_%H_%M_%S")) + '.log', 'a', encoding='utf-8') as f:
        connector = ProductionConnector()
        for title_product, characteristics in connector.read_and_update_data_tables(columns=('id', 'title_product', 'characteristics'), limit=10000):
            data = json_loads(characteristics)
            res = Final(connector).parse(title_product)
            if 'Производитель' in data:
                expected_manufacturer = data['Производитель']
                if not res.model_model or not res.model_model.manufacturer or expected_manufacturer != res.model_model.manufacturer.normal_form:
                    f.write(f'Производитель из характеристик ({expected_manufacturer}) не совпадает c обнаруженным производителем ({res.model_model})\n')
            if 'Код товара' in data:
                code_product = data['Код товара']
                if code_product in res.model_model.normal_form:
                    f.write(f'{title_product} Код товара ({code_product}) в модели {res.model_model.normal_form}\n')
            if 'Артикул' in data:
                article = data['Артикул']
                if article in res.model_model.normal_form:
                    f.write(f'{title_product} Артикул ({article}) в модели {res.model_model.normal_form}\n')
            if 'Серия' in data:
                series = data['Серия']
                if series != res.model_model.series:
                    f.write(f'{title_product} Серия из характеристик ({series}) не совпадает c обнаруженной серией ({res.model_model.series})\n')


if __name__ == '__main__':
    compare_to_characteristics()
