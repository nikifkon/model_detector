# python -m metrics.compare_to_characteristics
from datetime import datetime

from algorithms.final import Final
from connectors.production import ProductionConnector
from utils import json_loads

# Производитель такой же
# Кода товара нет


def test():
    with open('metrics/reports/characteristics_report_' + str(datetime.utcnow().strftime("%d_%m_%Y_%H_%M_%S")) + '.log', 'a', encoding='utf-8') as f:
        for id, *data in ProductionConnector().read(columns=('id', 'title_product', 'characteristics'), limit=100):
            title_product, characteristics = data
            data = json_loads(characteristics)
            res = Final(ProductionConnector).parse(title_product)
            if 'Производитель' in data:
                expected_manufacturer = data['Производитель']
                if expected_manufacturer != res.manufacturer.normal_form:
                    f.write(f'{id}: Производитель из характеристик ({expected_manufacturer}) не совпадает c обнаруженным производителем ({res.manufacturer.normal_form})\n')
            if 'Код товара' in data:
                code_product = data['Код товара']
                if code_product in res.model.normal_form:
                    f.write(f'{id}: {title_product} Код товара ({code_product}) в модели {res.model.normal_form}\n')
            if 'Артикул' in data:
                article = data['Артикул']
                if article in res.model.normal_form:
                    f.write(f'{id}: {title_product} Артикул ({article}) в модели {res.model.normal_form}\n')
            if 'Серия' in data:
                series = data['Серия']
                if series != res.model.series:
                    f.write(f'{id}: {title_product} Серия из характеристик ({series}) не совпадает c обнаруженной серией ({res.model.series})\n')


if __name__ == '__main__':
    test()
