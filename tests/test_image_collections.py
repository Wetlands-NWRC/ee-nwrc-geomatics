import unittest 
from pprint import pprint
import eeng

import ee

ee.Initialize()


class TestImageCollections(unittest.TestCase):
    def setUp(self):
        self.start = ee.Date("2019-01-01")
        self.end = ee.Date("2019-12-31")
        longitude = -77.3619
        latitude = 44.1786

        # Create a Geometry.Point over Belleville
        self.aoi = ee.Geometry.Point([longitude, latitude])
    
    def test_sentinel1DV(self):
        """Test the sentinel1DV method"""
        sentinel1DV = ee.ImageCollection.sentinel1DV(self.start, self.end, self.aoi)

        try:
            pprint(sentinel1DV.first().getInfo())
        except ee.EEException as e:
            self.fail(e)
    
    def test_sentinel2_toa(self):
        """Test the sentinel2 method"""
        sentinel2 = ee.ImageCollection.sentinel2TOA(self.start, self.end, self.aoi)

        try:
            pprint(sentinel2.first().getInfo())
        except ee.EEException as e:
            self.fail(e)
    
    def test_sentinel2SR(self):
        """Test the sentinel2SR method"""
        sentinel2SR = ee.ImageCollection.sentinel2SR(self.start, self.end, self.aoi)

        try:
            pprint(sentinel2SR.first().getInfo())
        except ee.EEException as e:
            self.fail(e)

    def test_sentinel2CloudProbability(self):
        """Test the sentinel2CloudProbability method"""
        sentinel2CloudProbability = ee.ImageCollection.sentinel2CloudProbability(self.start, self.end, self.aoi)

        try:
            pprint(sentinel2CloudProbability.first().getInfo())
        except ee.EEException as e:
            self.fail(e)