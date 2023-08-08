import unittest
import ee

from pprint import pprint

ee.Initialize()

import eeng

class TestFeatureCollectionFuncs(unittest.TestCase):
    def setUp(self) -> None:
        self.fc = ee.FeatureCollection("users/ryangilberthamilton/BC/widgeon/3Class/wd_tr_3")
    
    def test_add_x_coordinate(self):
        try:
            pprint(self.fc.addXCordinate().first().getInfo())
        except ee.EEException as e:
            print(e)

    def test_add_y_coordinate(self):
        try:
            pprint(self.fc.addYCordinate().first().getInfo())
        except ee.EEException as e:
            print(e)
    
    def test_add_x_y_coordinate(self):
        try:
            pprint(self.fc.addXCordinate().addYCordinate().first().getInfo())
        except ee.EEException as e:
            print(e)

    def test_generate_samples(self):
        img = ee.ImageCollection("COPERNICUS/S2_SR").filterBounds(self.fc).filterDate("2020-01-01", "2020-12-31").median()
        try:
            pprint(self.fc.generateSamples(img).first().getInfo())
        except ee.EEException as e:
            self.fail(e)
    
    def test_get_lookup(self):
        try:
            pprint(self.fc.getLookup('class', sorted=True).getInfo())
        except ee.EEException as e:
            self.fail(e)
