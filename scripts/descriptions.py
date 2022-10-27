import logging

import click

from algorithms.final import Final
from connectors.production import ProductionConnector
from connectors.testing import TestingConnector


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


@click.command()
@click.option('--development', '-d', is_flag=True, default=0, help='use development data')
def parse_descriptions(development):
    if development:
        connector = TestingConnector()
    else:
        connector = ProductionConnector()
    gen = connector.read_and_update_data_tables(
        columns=('id', 'description_product', 'title_product', 'manufacturer', 'model'),
        limit=200
    )
    print("working...")
    for row in gen:
        description_product, title_product, manufacturer, model = row
        alg = Final(connector)
        title_res = alg.parse(title_product)
        if title_res.model_model is None:
            description_res = alg.parse(description_product)
        actual_model = description_res.model_model.normal_form_with_series if description_res.model_model else ''
        actual_manufacturer = description_res.model_model.manufacturer.normal_form if description_res.model_model and description_res.model_model.manufacturer else ''
        logger.warning(f'{description_product}\n{manufacturer:<20} -> {actual_manufacturer}\n{model:<20} -> {actual_model}', )


if __name__ == '__main__':
    parse_descriptions()
