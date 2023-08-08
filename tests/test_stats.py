import unittest
from pprint import pprint
import ee

from eeng.stats import Assessment

ee.Initialize()

class TestAssessmentBuilder(unittest.TestCase):
    def setUp(self) -> None:
        array = ee.Array([
            [1,2,3],
            [4,5,6],
            [7,8,9]
        ])

        self.matrix = ee.ConfusionMatrix(array)

    
    def test_assessment_builder(self):
        asmnt = Assessment(self.matrix)

        try:
            pprint(self.matrix.getInfo())
            (asmnt
             .add_matrix()
             .add_accuracy()
             .add_producers()
             .add_consumers()
             .add_labels(['a', 'b', 'c', 'd', 'e', 'f'])
             .build()
            )

            pprint(asmnt.assessment.getInfo())
        except ee.EEException as e:
            print(e)
            self.fail("Assessment builder failed")