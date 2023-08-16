import ee

from .filters import SpatialFilters
from .calc import Calculator
from .cmasking import S2CloudlessAlgorithm


def denoise(self, filter: SpatialFilters):
    if not issubclass(filter, SpatialFilters):
        raise TypeError("filter must be a subclass of SpatialFilters")
    return self.map(filter)


def addCalculator(self, calculator: Calculator):
    if not issubclass(calculator, Calculator):
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
