import ee
from ee import Geometry

from math import pi
from .calc import NDVI


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
    
    def get_s2_sr(self, start, end, aoi) -> ee.ImageCollection:
        """ get Sentinel2 Surface Reflectance image collection """
        return self.s2_sr_collection_factory().create_collection(start, end, aoi)

    def get_s2_cloud_propability(self, start, end, aoi):
        return self.s2_cloud_probability_collection_factory().create_collection(start, end, aoi)
    
    def s2Cloudless(self, start, end, aoi, cloud_px_percent: int = 60) -> ee.ImageCollection:
        prob = self.get_s2_cloud_propability(start, end, aoi)
        s2 = self.get_s2_cloud_propability(start, end, aoi).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_px_percent))

        join = ee.Join.saveFirst('s2cloudless').apply(**{
            'primary': s2,
            'secondary': prob,
            'condition': ee.Filter.equals(**{
                'leftField': 'system:index',
                'rightField': 'system:index'
            })
        })

        return ee.ImageCollection(join)


class TimeSeriesCreator(ImageCollectionCreator):
    def get_time_series(self, start, end, aoi, omega: float = 1.0):
        return TimeSeries(self.create_collection(start, end, aoi)).addTime(omega).addConstant()


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


class TraningPointCreator:
    def __init__(self, collection: ee.FeatureCollection) -> None:
        self.collection = collection
    
    def create_training_data(self):
        ...