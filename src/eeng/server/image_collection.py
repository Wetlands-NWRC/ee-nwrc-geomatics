import ee

from .filters import SpatialFilters
from .calc import Calculator
from .cmasking import S2CloudlessAlgorithm


def denoise(self, filter: SpatialFilters):
    if not isinstance(filter, SpatialFilters):
        raise TypeError("filter must be a subclass of SpatialFilters")
    return self.map(filter)


def addCalculator(self, calculator: Calculator):
    if not isinstance(calculator, Calculator):
        raise TypeError("calculator must be a subclass of Calculator")
    return self.map(calculator)


# bound functions to the ee.ImageCollection class
ee.ImageCollection.denoise = denoise
ee.ImageCollection.addCalculator = addCalculator


class Sentinel1(ee.ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S1_GRD")


class Sentinel2SR(ee.ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S2_SR")


class Sentinel2TOA(ee.ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S2")


class Sentinel2CloudProbability(ee.ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S2_CLOUD_PROBABILITY")


class Sentinel2Cloudless(ee.ImageCollection):
    def __init__(self, arg: tuple):
        self._arg = arg
        super().__init__(self.arg)

    @property
    def arg(self):
        return self._arg

    @arg.setter
    def arg(self, arg):
        if not isinstance(arg, tuple):
            raise TypeError("arg must be a tuple")
        self._arg = self._join(*arg)

    @staticmethod
    def _join(*args):
        """Joins the given image collections into one"""
        if len(args) != 2:
            raise ValueError("args must be a tuple of length 2")

        s2sr, s2cp = args

        if not isinstance(s2sr, Sentinel2SR):
            raise TypeError("s2sr must be a Sentinel2SR instance")
        if not isinstance(s2cp, Sentinel2CloudProbability):
            raise TypeError("s2cp must be a Sentinel2CloudProbability instance")

        # join the two collections
        return ee.Join.saveFirst("s2cloudless").apply(
            **{
                "primary": s2sr,
                "secondary": s2cp,
                "condition": ee.Filter.equals(
                    **{"leftField": "system:index", "rightField": "system:index"}
                ),
            }
        )

    def addCloudMask(self, algo: S2CloudlessAlgorithm):
        if not isinstance(algo, S2CloudlessAlgorithm):
            raise TypeError("algo must be a S2CloudlessAlgorithm instance")
        return self.map(algo)


# Creator classess
class Sentinel2Creator:
    def __init__(self):
        self._sr = Sentinel2SR()
        self._toa = Sentinel2TOA()
        self._cp = Sentinel2CloudProbability()

    @property
    def sr(self):
        return self._sr

    @property
    def toa(self):
        return self._toa

    @property
    def cp(self):
        return self._cp

    def get_toa_col(
        self,
        start_date: str,
        end_date: str,
        geometry: ee.Geometry,
        cloud_cover: float = 100.0,
    ):
        return (
            self.toa.filterDate(start_date, end_date)
            .filterBounds(geometry)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_cover))
        )

    def get_sr_col(
        self,
        start_date: str,
        end_date: str,
        geometry: ee.Geometry,
        cloud_cover: float = 100.0,
    ):
        return (
            self.sr.filterDate(start_date, end_date)
            .filterBounds(geometry)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_cover))
        )

    def get_cp_col(self, start_date: str, end_date: str, geometry: ee.Geometry):
        return self.cp.filterDate(start_date, end_date).filterBounds(geometry)

    def get_s2_cloudless_col(self, s2_sr, s2_cp) -> Sentinel2Cloudless:
        return Sentinel2Cloudless((s2_sr, s2_cp))


class Sentinel1Creator:
    def __init__(self) -> None:
        self._s1 = Sentinel1()

    @property
    def s1(self):
        return self._s1

    def get_s1_col(self, start_date: str, end_date: str, geometry: ee.Geometry):
        return self.s1.filterDate(start_date, end_date).filterBounds(geometry)

    def get_dv_col(self, start_date, end_date, geometry):
        filter = ee.Filter(
            [
                ee.Filter.listContains("transmitterReceiverPolarisation", "VV"),
                ee.Filter.listContains("transmitterReceiverPolarisation", "VH"),
                ee.Filter.eq("instrumentMode", "IW"),
            ]
        )

        return (
            self._s1.filterDate(start_date, end_date)
            .filterBounds(geometry)
            .filter(filter)
        )

    def get_dh_col(self, start_date, end_date, geometry):
        filter = ee.Filter(
            [
                ee.Filter.listContains("transmitterReceiverPolarisation", "HH"),
                ee.Filter.listContains("transmitterReceiverPolarisation", "HV"),
                ee.Filter.eq("instrumentMode", "IW"),
            ]
        )

        return (
            self._s1.filterDate(start_date, end_date)
            .filterBounds(geometry)
            .filter(filter)
        )

    def get_asc_dv_col(self, start_date, end_date, geometry):
        filter = ee.Filter(
            [
                ee.Filter.listContains("transmitterReceiverPolarisation", "VV"),
                ee.Filter.listContains("transmitterReceiverPolarisation", "VH"),
                ee.Filter.eq("instrumentMode", "IW"),
                ee.Filter.eq("orbitProperties_pass", "ASCENDING"),
            ]
        )

        return (
            self._s1.filterDate(start_date, end_date)
            .filterBounds(geometry)
            .filter(filter)
        )

    def get_desc_dv_col(self, start_date, end_date, geometry):
        filter = ee.Filter(
            [
                ee.Filter.listContains("transmitterReceiverPolarisation", "VV"),
                ee.Filter.listContains("transmitterReceiverPolarisation", "VH"),
                ee.Filter.eq("instrumentMode", "IW"),
                ee.Filter.eq("orbitProperties_pass", "DESCENDING"),
            ]
        )

        return (
            self._s1.filterDate(start_date, end_date)
            .filterBounds(geometry)
            .filter(filter)
        )
