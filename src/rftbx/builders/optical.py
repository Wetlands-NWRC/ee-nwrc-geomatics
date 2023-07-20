from typing import Tuple
import ee

from ..rmath import OpticalBandMath

OpticalDataset = ee.ImageCollection
BandName = str
DateConstraint = Tuple[str, str]


class OpticalDatasetBuilder:
    def __init__(self) -> None:
        self.builder: OpticalDataset = None

    def add_ndvi(self, nir: BandName, red: BandName, ndvi_name: str = None):
        self.builder = self.builder.map(OpticalBandMath.ndvi(nir, red, ndvi_name))
        return self

    def add_savi(
        self, nir: BandName, red: BandName, L: float = 0.5, savi_name: str = None
    ):
        self.builder = self.builder.map(OpticalBandMath.savi(nir, red, L, savi_name))
        return self

    def add_tassel_cap(self, b, g, r, nir, swir1, swir2):  # TODO add band hooks
        self.builder = self.builder.map(OpticalBandMath.tassel_cap())
        return self

    def add_date_constraint(self, date_constraint: DateConstraint):
        self.builder = self.builder.filterDate(*date_constraint)
        return self

    def add_geometry_constraint(self, geometry):
        self.builder = self.builder.filterBounds(geometry)
        return self

    def add_meta_filters(self, meta_filters: ee.Filter):
        """Filters the dataset by the images metadata.
        Meta filters are filters that have been chained together using.
        Represent and List of Filters that have been ANDed together.
        """
        self.builder = self.builder.filter(meta_filters)
        return self

    def build(self):
        return self
