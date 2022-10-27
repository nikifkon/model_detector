from dataclasses import dataclass

from algorithms.base import TokenBasedAlgorithm, BaseResult
from algorithms.find_models import FindModels
from algorithms.find_manufacturer import FindManufacturers
from algorithms.detect_product_name import ProductNameFinder
from algorithms.detect_essence import EssenceFinder
from algorithms.detect_model import ModelDetector
from algorithms.defaults import DefaultAlgorithm
from connectors.base import BaseConnector
from connectors.models import ManufacturerMethod, ModelModel
from tokens import TokenSeq


@dataclass(eq=True, frozen=True)
class FinalResults(BaseResult):
    # manufacturer_model: ManufacturerModel
    model_model: ModelModel
    # essence: str
    method: ManufacturerMethod


class Final(TokenBasedAlgorithm[FinalResults]):
    def __init__(self, connector: BaseConnector):
        self.connector = connector

    def parse_by_tokens(self, token_seq: TokenSeq) -> FinalResults:
        def is_model_exists(x):
            return self.connector.check_model_existence(x)

        def is_prefix_exists(x):
            return False

        def is_manufacturer_exists(x):
            return self.connector.check_manufacturer_existence(x)

        def is_series_exists(x):
            return self.connector.check_series_existence(x)

        default_seq = DefaultAlgorithm().parse_by_tokens(token_seq).seq
        # with_units_res = UnitExtractor().parse_by_tokens(NumbersMerge().parse_by_tokens(UnitMerge().parse_by_tokens(XReplace().parse_by_tokens(token_seq).seq).seq).seq)
        # with_units_seq = with_units_res.seq

        res = FindModels(is_model_exists, is_prefix_exists).parse_by_tokens(default_seq)
        if res.model:
            # TODO: еще какие-то условия типа проверки сути и производителя
            return FinalResults(
                logs=None,
                # essence=res.model.essence,
                # manufacturer_model=res.model.manufacturer,
                model_model=res.model,
                method=ManufacturerMethod.BY_VERIFIED_MODEL)

        manuf_res = FindManufacturers(is_manufacturer_exists, is_series_exists).parse_by_tokens(default_seq)
        seq_with_manuf = manuf_res.seq
        if manuf_res.method == ManufacturerMethod.MULTY:
            return FinalResults(
                logs=None,
                # essence=essence,
                # manufacturer_model=None,
                model_model=ModelModel(' & '.join(sorted(manuf.normal_form for manuf in manuf_res.manufacturers))),
                method=ManufacturerMethod.MULTY)

        res = ProductNameFinder(lambda x: False).parse_by_tokens(seq_with_manuf)
        seq_with_product_name = res.seq
        product_name = res.product_name
        essence = EssenceFinder(lambda x: False).parse(product_name).essence

        manuf = list(manuf_res.manufacturers)[0] if len(manuf_res.manufacturers) == 1 else None
        res = ModelDetector(lambda x: False).parse_by_tokens(seq_with_product_name)

        return FinalResults(
            logs=None,
            model_model=ModelModel(res.model.value, manuf, essence=essence,
                                   series=manuf_res.series) if res.model else None,
            method=manuf_res.method)
