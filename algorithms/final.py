from dataclasses import dataclass

from algorithms.base import TokenBasedAlgorithm, BaseResult
from algorithms.find_models import FindModels
from connectors.base import BaseConnector
from connectors.models import ManufacturerMethod, ManufacturerModel, ManufacturerStatus, ModelModel
from tokens import TokenSeq, ValueToken


class Manufacturer(ValueToken):
    pass


@dataclass
class FinalResults(BaseResult):
    manufacturer_model: ManufacturerModel
    model_model: ModelModel
    essence: str
    method: ManufacturerMethod


class Final(TokenBasedAlgorithm[FinalResults]):
    def __init__(self, connector: BaseConnector):
        self.connector = connector

    def parse_by_tokens(self, token_seq: TokenSeq) -> FinalResults:
        def is_model_exists(x):
            return self.connector.check_model_existence(x)

        def is_prefix_exists(x):
            return False
        res = FindModels(is_model_exists, is_prefix_exists).parse_by_tokens(token_seq)
        if res.model:
            # TODO: еще какие-то условия типа проверки сути и производителя
            return FinalResults(
                logs=None,
                essence=res.model.essence,
                manufacturer_model=res.model.manufacturer,
                model_model=res.model,
                method=ManufacturerMethod.BY_VERIFIED_MODEL)

        return FinalResults(
            logs=None,
            essence=None,
            manufacturer_model=ManufacturerModel('tetst', ManufacturerStatus.BANNED),
            model_model=ModelModel('test'),
            method=ManufacturerMethod.FROM_DATA)
