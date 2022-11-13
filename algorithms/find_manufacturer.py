from dataclasses import dataclass
from typing import Callable, Optional

from algorithms.base import NewSequenceResult, TokenBasedAlgorithm
from algorithms.find_series import FindSeries
from connectors.models import ManufacturerModel, ManufacturerMethod, SeriesModel
from tokens import TokenSeq, ManufacturerToken


@dataclass(eq=True, frozen=True)
class FindManufacturersResult(NewSequenceResult):
    manufacturers: frozenset[ManufacturerModel]
    method: ManufacturerMethod
    series: SeriesModel = None


class FindManufacturers(TokenBasedAlgorithm[FindManufacturersResult]):
    def __init__(self, is_manufacturer_exists: Callable[[TokenSeq], Optional[ManufacturerModel]], is_series_exists: Callable[[TokenSeq], Optional[SeriesModel]]):
        self.is_manufacturer_exists = is_manufacturer_exists
        self.is_series_exists = is_series_exists

    def parse_by_tokens(self, token_seq: TokenSeq) -> FindManufacturersResult:
        manufacturers_to_chunks: dict[ManufacturerModel, list[tuple[int, int]]] = {}

        for ngram, start, end in token_seq.select_longest_ngrams_match(self.is_manufacturer_exists):
            manuf = self.is_manufacturer_exists(ngram)
            if manuf not in manufacturers_to_chunks:
                manufacturers_to_chunks[manuf] = []
            manufacturers_to_chunks[manuf].append((start, end))

        # filter substring
        for key in list(manufacturers_to_chunks.keys()):
            if any(key.normal_form.lower() in x.normal_form.lower() for x in manufacturers_to_chunks.keys() if x != key):
                manufacturers_to_chunks.pop(key)

        new_seq = token_seq
        manufacturers = list(manufacturers_to_chunks.keys())
        manufacturer = None

        series_res = FindSeries(self.is_series_exists).parse_by_tokens(token_seq)
        series = series_res.series

        if len(manufacturers) == 2 and series:
            matched_manufacturers = set(manufacturers) & set(series.manufacturers)

            if len(matched_manufacturers) == 1:
                manufacturers = [matched_manufacturers[0]]
        if len(manufacturers) >= 2:
            method = ManufacturerMethod.MULTY
            pass
        if len(manufacturers) == 1:
            if series and manufacturers[0] not in series.manufacturers:
                # TODO conflict
                print(str(token_seq))
                pass
            method = ManufacturerMethod.BY_NAME_CLEAR
            manufacturer = manufacturers[0]
            manufacturer_token = ManufacturerToken(manufacturer.normal_form)
            new_seq = token_seq.merge(manufacturers_to_chunks[manufacturer], lambda x: manufacturer_token)

            series_res = FindSeries(self.is_series_exists).parse_by_tokens(new_seq)
            new_seq = series_res.seq
        if len(manufacturers) == 0:
            if series and len(series.manufacturers) == 1:
                method = ManufacturerMethod.BY_SERIES
                manufacturers = [series.manufacturers[0]]
                new_seq = series_res.seq
            else:
                method = ManufacturerMethod.MISSED
                pass

        return FindManufacturersResult(
            seq=new_seq,
            manufacturers=frozenset(manufacturers),
            method=method,
            series=series
        )
