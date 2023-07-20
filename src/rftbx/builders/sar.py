from typing import Tuple, Callable
import ee

from ..rmath import SARBandMath

BandName = str
DateConstraint = Tuple[str, str]


class RadarBuilder:
    def __init__(self) -> None:
        self.builder: ee.ImageCollection = None

    def add_ratio(
        self, numerator: BandName, denominator: BandName, ratio_name: str = None
    ):
        self.builder = self.builder.map(
            SARBandMath.ratio(numerator, denominator, ratio_name)
        )
        return self

    def add_spatial_filter(self, filter: Callable):
        self.builder = self.builder.map(filter)
        return self

    def add_date_constraint(self, date_constraint: DateConstraint):
        self.builder = self.builder.filterDate(*date_constraint)
        return self

    def add_geometry_constraint(self, geometry):
        self.builder = self.builder.filterBounds(geometry)
        return self

    def add_meta_filters(self, meta_filters: ee.Filter):
        self.builder = self.builder.filter(meta_filters)
        return self

    def build(self):
        return self
