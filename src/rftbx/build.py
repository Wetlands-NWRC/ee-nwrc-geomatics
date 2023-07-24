from abc import ABC, abstractmethod

from .datasets import *

from .rmath import *

class DataBuilder(ABC):
    """ the abstract base class for all data builders """

    @abstractmethod
    def add_spatial_filter(self, geometry: ee.Geometry):
        pass

    @abstractmethod
    def add_temporal_filter(selfs, date_range: tuple):
        pass

    @abstractmethod
    def add_meta_filters(self, meta_filters: ee.Filter):
        pass

    @abstractmethod
    def add_band_selection(self, bands: list):
        pass


class SARBuilder(DataBuilder):
    """ the abstract base class for all SAR data builders """

    @abstractmethod
    def add_ratio(self, numerator: str, denominator: str, ratio_name: str = None):
        pass

    @abstractmethod
    def despekcle(self, filter):
        pass


class OpcialBuilder(DataBuilder):
    """ the abstract base class for all optical data builders """

    @abstractmethod
    def add_ndvi(self, nir: str, red: str, ndvi_name: str = None):
        pass

    @abstractmethod
    def add_savi(self, nir: str, red: str, L: float , savi_name: str = None):
        pass

    @abstractmethod
    def add_tassel_cap(self):
        pass


class S1Builder(SARBuilder):
    def __init__(self):
        self.builder: ee.ImageCollection = Sentinel1()

    def add_ratio(self, numerator: str, denominator: str, ratio_name: str = None):
        self.builder = self.builder.map(
            SARBandMath.ratio(numerator, denominator, ratio_name)
        )
        return self

    def add_spatial_filter(self, geometry: ee.Geometry):
        self.builder = self.builder.filterBounds(geometry)
        return self

    def add_temporal_filter(self, date_range: tuple):
        self.builder = self.builder.filterDate(*date_range)
        return self

    def add_meta_filters(self, meta_filters: ee.Filter):
        self.builder = self.builder.filter(meta_filters)
        return self

    def add_band_selection(self, bands: list):
        self.builder = self.builder.select(bands)
        return self

    def despekcle(self, filter):
        self.builder = self.builder.map(filter)
        return self

    def build(self):
        return self


class ALOSBuilder(SARBuilder):
    def __init__(self):
        self.builder: ee.ImageCollection = None

    def add_ratio(self, numerator: str, denominator: str, ratio_name: str = None):
        self.builder = self.builder.map(
            SARBandMath.ratio(numerator, denominator, ratio_name)
        )
        return self

    def add_spatial_filter(self, geometry: ee.Geometry):
        return None

    def add_temporal_filter(self, date_range: tuple):
        self.builder = self.builder.filterDate(*date_range)
        return self

    def add_meta_filters(self, meta_filters: ee.Filter):
        self.builder = self.builder.filter(meta_filters)
        return self

    def add_band_selection(self, bands: list):
        self.builder = self.builder.select(bands)
        return self

    def despekcle(self, filter):
        self.builder = self.builder.map(filter)
        return self

    def build(self):
        return self


class S2SRBuilder(OpcialBuilder):
    def __init__(self):
        self.builder: ee.ImageCollection = None

    def add_spatial_filter(self, geometry: ee.Geometry):
        self.builder = self.builder.filterBounds(geometry)
        return self

    def add_temporal_filter(self, date_range: tuple):
        self.builder = self.builder.filterDate(*date_range)
        return self

    def add_meta_filters(self, meta_filters: ee.Filter):
        self.builder = self.builder.filter(meta_filters)
        return self

    def add_band_selection(self, bands: list):
        self.builder = self.builder.select(bands)
        return self

    def add_ndvi(self, nir: str, red: str, ndvi_name: str = None):
        self.builder = self.builder.map(OpticalBandMath.ndvi(nir, red, ndvi_name))
        return self

    def add_tassel_cap(self):
        self.builder = self.builder.map(OpticalBandMath.tassel_cap())
        return self

    def add_savi(self, nir: str, red: str, L: float , savi_name: str = None):
        self.builder = self.builder.map(OpticalBandMath.savi(nir, red, L, savi_name))
        return self

    def build(self):
        return self

