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
