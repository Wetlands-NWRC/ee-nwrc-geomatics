from unittest import TestCase
import ee

from rftbx.datasets import Sentinel2
from rftbx.cmasking import S2CloudlessAlgorithm

ee.Initialize()

class TestS2CloudlessAlgorithm(TestCase):
    def setUp(self) -> None:
        aoi = ee.Geometry.Point([-77.5, 38.5])
        date_range = ("2020-04-01", "2020-10-31")

        self.cloud_prob = Sentinel2.s2cloudless(
            aoi=aoi,
            date_range=date_range,
        )
        return None
    
    def test_algorithm(self):
        try:
            algorithm = S2CloudlessAlgorithm()
            masked = self.cloud_prob.map(algorithm)
            print(masked.median().bandNames().getInfo())
        except ee.EEException as e:
            self.fail(e)
        return None
    