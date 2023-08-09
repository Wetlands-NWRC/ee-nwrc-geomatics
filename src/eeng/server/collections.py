from dataclasses import dataclass, field

import ee


CollectionID = str

@dataclass(frozen=True)
class ImageCollectionIDs:
    """ Contains the image collection ids for the different data sources """
    s1: CollectionID = field(default="COPERNICUS/S1_GRD")
    s2: CollectionID = field(default="COPERNICUS/S2")
    s2_sr: CollectionID = field(default="COPERNICUS/S2_SR")
    s2_cloud_prob: CollectionID = field(default="COPERNICUS/S2_CLOUD_PROBABILITY")
    alos: CollectionID = field(default="JAXA/ALOS/PALSAR/YEARLY/SAR")


class ImageCollectionCreator:
    def __init__(self, collection_id: CollectionID, start, end, aoi) -> None:
        self.collection_id = collection_id
        self.start = start
        self.end = end
        self.aoi = aoi

    def get_collection(self, filter_function: ee.Filter) -> ee.ImageCollection:
        date_filter = ee.Filter.date(self.start, self.end)
        combo_filter = ee.Filter.And(date_filter, filter_function)
        collection = ee.ImageCollection(self.collection_id).filterBounds(self.aoi).filter(combo_filter)
        return collection


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