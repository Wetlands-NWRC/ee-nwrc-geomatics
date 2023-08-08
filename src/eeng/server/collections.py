import ee
from ee import Geometry

from math import pi
from .calc import NDVI


class TimeSeries:
    def __init__(self, args):
        super().__init__(args)
        self.col = None
        self._independent = []
        self._dependent = None

    def addDependent(self, calc):
        self._dependent = calc.name
        self.col = self.col.map(calc)
        return self

    def addConstant(self):
        def _addConstant(image: ee.Image):
            return image.addBands(ee.Image.constant(1))
        self.col = self.col.map(_addConstant)
        return self

    def addTime(self, omega: float = 1.0):
        self._independent.append("t")
        def _addTime(image: ee.Image):
            date = ee.Date(image.get("system:time_start"))
            years = date.difference(ee.Date("1970-01-01"), "year")
            time_radians = ee.Image(years.multiply(2 * pi * omega).rename("t"))
            return image.addBands(time_radians.float())
        self.col = self.col.map(_addTime)
        return self


class ImageCollectionCreator:
    def __init__(self, collection_id: str) -> None:
        self.collection_id = collection_id

    def create_collection(self, start, end, aoi) -> ee.ImageCollection:
        return ee.ImageCollection(self.collection_id).filterDate(start, end).filterBounds(aoi)
    
    @classmethod
    def s1_collection_factory(cls):
        return cls("COPERNICUS/S1_GRD")

    @classmethod
    def s2_sr_collection_factory(cls):
        return cls("COPERNICUS/S2_SR")

    @classmethod
    def s2_cloud_probability_collection_factory(cls):
        return cls("COPERNICUS/S2_CLOUD_PROBABILITY")
    
    @classmethod
    def s2_toa_collection_factory(cls):
        return cls("COPERNICUS/S2")
    
    @classmethod
    def alos_collection_factory(cls):
        return cls("JAXA/ALOS/PALSAR/YEARLY/SAR")


class Sentinel1Creator(ImageCollectionCreator):
    def get_s1_dv(self, start, end, aoi) -> ee.ImageCollection:
        polerizations = ee.Filter([
            ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'),
            ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')
        ])
        return self.s1_collection_factory().create_collection(start=start, end=end, aoi=aoi).filter(polerizations).select('V.*')
    
    def get_s1_dh(self, start, end, aoi) -> ee.ImageCollection:
        return NotImplemented


class Sentinel2(ImageCollectionCreator):
    def top_of_atmosphere(self):
        return NotImplemented
    
    def surface_refelctance(self):
        ...

    def propability(self):
        ...
    
    def s2Cloudless(self, start, end, aoi, cloud_px_percent: int = 60):
        ...


class DataCubeCreator(ImageCollectionCreator):
    def create_data_cube_collection(self, aoi):
        pass


class ALOSCreator:
    def create_alos_collection(self):
        pass


class TimeSeriesCreator(ImageCollectionCreator):
    def get_time_series(self, start, end, aoi, omega: float = 1.0):
        return TimeSeries(self.create_collection(start, end, aoi)).addTime(omega).addConstant()


class Sentinel2(ee.ImageCollection):

    @classmethod
    def top_of_atmosphere(cls):
        """ Factory method for Sentinel2 TOA image collection """
        return cls("COPERNICUS/S2")

    @classmethod
    def probability(cls):
        """ Factory method for Sentinel2 cloud probability image collection"""
        return cls("COPERNICUS/S2_CLOUD_PROBABILITY")

    @classmethod
    def surface_refelctance(cls):
        """ Factory method for Sentinel2 SR image collection """
        return cls("COPERNICUS/S2_SR")

    @classmethod
    def s2cloudless(cls, date_range, aoi, cloudly_percent: int = 60):
        prob = cls.probability().filterDate(date_range[0], date_range[1]).filterBounds(aoi)
        s2 = cls.surface_refelctance().filterDate(date_range[0], date_range[1]).filterBounds(aoi).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloudly_percent))

        join = ee.Join.saveFirst('s2cloudless').apply(**{
            'primary': s2,
            'secondary': prob,
            'condition': ee.Filter.equals(**{
                'leftField': 'system:index',
                'rightField': 'system:index'
            })
        })

        return cls(join)

    def __init__(self, agrs=None):
        args = agrs if agrs is not None else "COPERNICUS/S2_SR"
        super().__init__(args)


class DataCube(ee.ImageCollection):
    SEASON_PREFIX = {"spring": "a_spri_b", "summer": "b_summ_b", "fall": "c_fall_b"}

    def __init__(self, args):
        super().__init__(args)

    @property
    def spring(self):
        return self.select(f'{self.SEASON_PREFIX["spring"]}.*')

    @property
    def summer(self):
        return self.select(f'{self.SEASON_PREFIX["summer"]}.*')

    @property
    def fall(self):
        return self.select(f'{self.SEASON_PREFIX["fall"]}.*')


class Stack:
    def __init__(self):
        self._stack = []

    def add(self, image: ee.Image):
        if not isinstance(image, ee.Image):
            raise TypeError("image must be an ee.Image")
        self._stack.append(image)
        return self

    def concat(self) -> ee.Image:
        """ Concatenate all images in the stack """
        return ee.Image.cat(*self._stack)


class HarmonicsCollection(ee.ImageCollection):
    def __init__(self, args, dependent = NDVI(), cycles: int = 3):
        super().__init__(args)
        self.indep = ['constant', 't']
        self.dep = dependent
        self.cycles = cycles

    def addDependent(self, calc):
        self.dep = calc.name
        return self.map(calc)

    def addConstant(self):
        def _addConstant(image: ee.Image):
            return image.addBands(ee.Image.constant(1))
        return self.map(_addConstant)

    def addTime(self, omega: float = 1.0):
        def _addTime(image: ee.Image):
            date = ee.Date(image.get("system:time_start"))
            years = date.difference(ee.Date("1970-01-01"), "year")
            time_radians = ee.Image(years.multiply(2 * pi * omega).rename("t"))
            return image.addBands(time_radians.float())
        return self.map(_addTime)

    def addHarmonics(self):
        sin = [f"cos_{i}" for i in range(1, self.cycles + 1)]
        cos = [f"sin_{i}" for i in range(1, self.cycles + 1)]

        def _addHarmonics(image: ee.Image):
            frequencies = ee.Image.constant(self.cycles)
            time = ee.Image(image).select("t")
            cosines = time.multiply(frequencies).cos().rename(cos)
            sines = time.multiply(frequencies).sin().rename(sin)
            return image.addBands(cosines).addBands(sines)

        return self.map(_addHarmonics)


class TraningPointCreator:
    def __init__(self, collection: ee.FeatureCollection) -> None:
        self.collection = collection
    
    def create_training_data(self):
        ...