import unittest
from pprint import pprint
import ee

ee.Initialize()


from src.rftbx.tabular import TrainingPoints



class TestTrainingPoints(unittest.TestCase):
    def setUp(self) -> None:
        features = [
            ee.Feature(ee.Geometry.Point([1, 2]), {'Wetland': 'class_1'}),
            ee.Feature(ee.Geometry.Point([2, 3]), {'Wetland': 'class_2'}),
            ee.Feature(ee.Geometry.Point([3, 4]), {'Wetland': 'class_3'}),
            ee.Feature(ee.Geometry.Point([4, 5]), {'Wetland': 'class_4'}),        
        ]
        self.training_points = TrainingPoints(features)
        return None
    
    def test_remap_override_from_client_dict(self):

        try:
            fc = self.training_points.remap({'class_1': 1, 'class_2': 2, 'class_3': 3, 'class_4': 4})
            pprint(fc.getInfo())
        except ee.EEException as e:
            self.fail(e)
    
    def test_remap_override_from_ee_dict(self):
        try:
            fc = self.training_points.remap(ee.Dictionary({'class_1': 1, 'class_2': 2, 'class_3': 3, 'class_4': 4}))
            pprint(fc.getInfo())
        except ee.EEException as e:
            self.fail(e)

    def test_remap_override_from_internal_mapping(self):
        try:
            fc = self.training_points.remap()
            pprint(fc.getInfo())
        except ee.EEException as e:
            self.fail(e)