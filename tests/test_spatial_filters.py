import unittest
import ee

from pprint import pprint

# from eeng.server.collections import denoise
from eeng.server.filters import BoxCar

ee.Initialize()

class TestSpatialFilters(unittest.TestCase):
    def setUp(self) -> None:
        # ee.ImageCollection.denoise = denoise
        self.collection = ee.ImageCollection("COPERNICUS/S1_GRD").filterDate("2020-01-01", "2020-01-02").filterBounds(ee.Geometry.Point(-74.3, 44.3))

    
    def test_boxcar(self):
        filterd = self.collection.denoise(BoxCar(3))

        try:
            pprint(filterd.first().getInfo())
        except Exception as e:
            print(e)
            self.fail("Failed to get info")