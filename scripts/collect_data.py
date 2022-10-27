import click

from connectors.production import ProductionConnector
from connectors.testing import TestingConnector


@click.command()
@click.option('--development', '-d', is_flag=True, default=0, help='use development data')
def collect_data(development):
    if development:
        TestingConnector()
    else:
        ProductionConnector(force_fetch=True)


if __name__ == '__main__':
    collect_data()
