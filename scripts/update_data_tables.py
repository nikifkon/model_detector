import json
import logging

import click

from algorithms.final import Final
from connectors.base import BaseConnector
from connectors.models import ManufacturerStatus
from connectors.production import ProductionConnector
from connectors.testing import TestingConnector


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


@click.command()
@click.option('--development', '-d', is_flag=True, default=0, help='use development data')
@click.option('--limit', '-l', default=18446744073709551615, help='update only limited rows in each database')
@click.option('--offset', '-o', default=0, help='start from offset')
@click.option('--dry-run', '-d', is_flag=True, default=False, help='Don\'t commit to database')
def update_data_tables(development, limit, offset, dry_run):
    if development:
        connector: BaseConnector = TestingConnector()
    else:
        connector: BaseConnector = ProductionConnector()
    gen = connector.read_and_update_data_tables(
        columns=('id', 'title_product', 'manufacturer', 'model'),
        limit=limit,
        offset=offset
    )
    print("working...")
    for row in gen:
        title_product, manufacturer, model = row
        logger.warning(f'{title_product}')
        alg = Final(connector)
        res = alg.parse(title_product)
        actual_model = res.model_model.normal_form_with_series if res.model_model else ''
        actual_manufacturer = res.model_model.manufacturer.normal_form if res.model_model and res.model_model.manufacturer else ''
        actual_essence = res.model_model.essence if res.model_model else ''
        series = res.model_model.series.normal_form if res.model_model and res.model_model.series else ''
        actual_manufacturer_status = res.model_model.manufacturer.status if res.model_model and res.model_model.manufacturer else ManufacturerStatus.MISSED

        data = {
            'manufacturer': actual_manufacturer,
            'model': actual_model,
            'essence': actual_essence,
            'name_product': res.name_product,
            'original_manufacturer': res.original_manufacturer_form,
            'original_model': res.original_model_form,
            'series': series,
            'manufacturer_status': actual_manufacturer_status.value,
            'manufacturer_method': res.method.value,
            'data': json.dumps(res.properties, ensure_ascii=False)
        }
        logger.warning(data)
        if not dry_run:
            gen.send(data)


if __name__ == '__main__':
    update_data_tables()
