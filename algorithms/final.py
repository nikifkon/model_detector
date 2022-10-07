from algorithms.base import TokenBasedAlgorithm, BaseResult
from connectors.base import BaseConnector
from connectors.models import ManufacturerMethod, ManufacturerModel, ManufacturerStatus, ModelModel
from tokens import TokenSeq, ValueToken


class Manufacturer(ValueToken):
    pass


class Model(ValueToken):
    pass


class FinalResults(BaseResult):
    essence: str
    manufacturer_model: ManufacturerModel
    model: ModelModel
    seq: TokenSeq

    def __init__(self, seq: TokenSeq, essence: str, manufacturer: ManufacturerModel, model: ModelModel):
        self.seq = seq
        self.essence = essence
        self.manufacturer = manufacturer
        self.model = model


class Final(TokenBasedAlgorithm[FinalResults]):
    def __init__(self, connector_type: BaseConnector):
        self.connector_type = connector_type

    def parse_by_tokens(self, token_seq: TokenSeq) -> FinalResults:
        return FinalResults(token_seq, None, ManufacturerModel('tetst', ManufacturerStatus.BANNED, ManufacturerMethod.FROM_DATA), ModelModel('test'))
