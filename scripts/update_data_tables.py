import logging

import click

from algorithms.final import Final
from connectors.production import ProductionConnector
from connectors.testing import TestingConnector


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# file_handler = logging.FileHandler('logs.log', encoding='utf-8')
# file_handler.setLevel(logging.DEBUG)
# logger.addHandler(file_handler)


@click.command()
@click.option('--development', '-d', is_flag=True, default=0, help='use development data')
def update_data_tables(development):
    if development:
        connector = TestingConnector()
    else:
        connector = ProductionConnector()
    gen = connector.read_and_update_data_tables(
        columns=('id', 'title_product', 'manufacturer', 'model'),
        limit=200,
        offset=2500
    )
    print("working...")
    for row in gen:
        title_product, manufacturer, model = row
        logger.warning(f'{title_product}')
        alg = Final(connector)
        res = alg.parse(title_product)
        actual_model = res.model_model.normal_form_with_series if res.model_model else ''
        actual_manufacturer = res.model_model.manufacturer.normal_form if res.model_model and res.model_model.manufacturer else ''
        if actual_manufacturer != manufacturer or actual_model != model:
            gen.send({
                'manufacturer': actual_manufacturer,
                'model': actual_model
            })
            logger.warning(f'{manufacturer:<20} -> {actual_manufacturer}\n{model:<20} -> {actual_model}', )


if __name__ == '__main__':
    update_data_tables()
