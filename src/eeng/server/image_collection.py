import ee

from .filters import SpatialFilters
from .calc import Calculator
from .cmasking import S2CloudlessAlgorithm


class __ImageCollection(ee.ImageCollection):
    """Not Ment to be used, just extends the ee.Image Collection class with out
    having to bound them to the class at run time"""

    def __init__(self, args):
        super().__init__(args)

    def denoise(self, filter: SpatialFilters):
        if not isinstance(filter, SpatialFilters):
            raise TypeError("filter must be a subclass of SpatialFilters")
        return self.map(filter)

    def addCalculator(self, calculator: Calculator):
        if not isinstance(calculator, Calculator):
            raise TypeError("calculator must be a subclass of Calculator")
        return self.map(calculator)

    def addFDate(self, fmt: str = None):
        """adds the date of the image to the image formatted to the speification
        defaults to YYYY-MM-dd
        """
        fmt = "YYYY-MM-dd" if fmt is None else fmt

        def add_f_date(image: ee.Image):
            return image.set("date", image.date().format(fmt))

        return self.map(add_f_date)

    def addPrefix(self):
        """copies the system:id flag to image"""

        def add_prefix(image: ee.Image):
            return image.set("system_id", image.get("system:id"))

        return self.map(add_prefix)

    def toFeatureCollection(self) -> ee.FeatureCollection:
        """Converts the Image Collection to a Feature Collection
        note: it copies all non system properties
        """

        def to_feature(image: ee.ComputedObject) -> ee.Feature:
            img = ee.Image(image)
            return ee.Feature(img.geometry(), img.toDictionary())

        as_list = self.toList(self.size()).map(to_feature)
        return ee.FeatureCollection(as_list)


class Sentinel1(__ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S1_GRD")

    def addGroupId(self):
        """adds a property that is the Relative Orbit combinded witht the Y coordinate of the centroid of the image footprint"""

        def add_group_id(image: ee.Image):
            y_cent = ee.Number(image.geometry().centroid().coordinates().get(1)).format(
                "%.2f"
            )

            return image.set(
                "group_id",
                ee.Number(image.get("relativeOrbitNumber_start"))
                .format("%d")
                .cat("_")
                .cat(y_cent),
            )

        return self.map(add_group_id)


class Sentinel2SR(__ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S2_SR")


class Sentinel2TOA(__ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S2")


class Sentinel2CloudProbability(__ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S2_CLOUD_PROBABILITY")


class Sentinel2Cloudless(__ImageCollection):
    def __init__(self, arg: tuple):
        super().__init__(self._join(*arg))

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
