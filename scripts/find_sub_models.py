from functools import partial

import click

from connectors.base import BaseConnector
from connectors.production import ProductionConnector
from connectors.testing import TestingConnector
from algorithms.list_possible_sub_models import ListPossibleSubModels, SelectSubModel


@click.command()
@click.option('--development', '-d', is_flag=True, default=0, help='use development data')
def find_sub_models(development):
    connector: BaseConnector = None
    if development:
        connector = TestingConnector()
    else:
        connector = ProductionConnector()
    connector.connect()

    where = "WHERE model is not null and essence is not null and manufacturer is not null"

    for row, update in connector.read_and_update(("id", "model", "manufacturer", "essence"), where=where):
        id, model, manufacturer, essence = row
        check_sub_model = partial(connector.check_model_existence(essence=essence, manufacturer=manufacturer))
        possibilities = ListPossibleSubModels(check_sub_model).parse(model)
        sub_model = SelectSubModel(possibilities)
        if sub_model is None:
            pass
        else:
            update(id, {
                "model": sub_model,
                "original_model": model
            })


if __name__ == '__main__':
    find_sub_models()
