from dataclasses import dataclass
from typing import Optional

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
    model_model: ModelModel
    method: ManufacturerMethod
    name_product: str
    properties: dict[str, tuple[str, str]]
    original_manufacturer_form: Optional[str] = None
    original_model_form: Optional[str] = None


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

        default_res = DefaultAlgorithm().parse_by_tokens(token_seq)
        default_seq = default_res.seq
        properties = default_res.properties

        res = ProductNameFinder(lambda x: False).parse_by_tokens(default_seq)
        seq_with_product_name = res.seq
        product_name = res.product_name.value if res.product_name else ''
        essence = EssenceFinder(lambda x: False).parse(product_name).essence

        res = FindModels(is_model_exists, is_prefix_exists).parse_by_tokens(seq_with_product_name)
        if res.model:
            # TODO: еще какие-то условия типа проверки сути и производителя
            return FinalResults(
                model_model=res.model,
                method=ManufacturerMethod.BY_VERIFIED_MODEL,
                properties=properties,
                name_product=product_name)

        manuf_res = FindManufacturers(is_manufacturer_exists, is_series_exists).parse_by_tokens(seq_with_product_name)
        seq_with_manuf = manuf_res.seq
        if manuf_res.method == ManufacturerMethod.MULTY:
            return FinalResults(
                model_model=ModelModel(' & '.join(sorted(manuf.normal_form for manuf in manuf_res.manufacturers))),
                method=ManufacturerMethod.MULTY,
                properties=properties,
                name_product=product_name)

        manuf = list(manuf_res.manufacturers)[0] if len(manuf_res.manufacturers) == 1 else None
        res = ModelDetector(lambda x: False).parse_by_tokens(seq_with_manuf)

        return FinalResults(
            model_model=ModelModel(res.model.value, manuf, essence=essence,
                                   series=manuf_res.series) if res.model else None,
            method=manuf_res.method,
            properties=properties,
            name_product=product_name)
