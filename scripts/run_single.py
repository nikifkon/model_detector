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
@click.option('--title_product', '-t', required=True, help='title of the product')
def run_single(development, title_product):
    if development:
        connector = TestingConnector()
    else:
        connector = ProductionConnector()
    alg = Final(connector)
    res = alg.parse(title_product)
    print(res)


if __name__ == '__main__':
    run_single()
