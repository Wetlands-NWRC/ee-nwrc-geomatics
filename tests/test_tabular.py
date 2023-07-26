import unittest
from pprint import pprint
import ee

ee.Initialize()


from src.rftbx.tabular import TrainingData


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.training_data = TrainingData("projects/fpca-336015/assets/NovaScotia/_527_POINTS")
        self.training_data.class_property = 'land_cover'
    def test_lookup(self):
        lookup = self.training_data.lookup

        try:
            info = lookup.getInfo()
        except Exception as e:
            self.fail(e)

        pprint(info)

    def test_remap(self):
        remapped = self.training_data.remap_(self.training_data.lookup)
        try:
            remapped.getInfo()
        except Exception as e:
            self.fail(e)
        pprint(remapped.first().getInfo())

    def test_add_x(self):
        with_x = self.training_data.add_x_col()
        try:
            with_x.getInfo()
        except Exception as e:
            self.fail(e)
        pprint(with_x.first().getInfo())

    def test_add_y(self):
        with_y = self.training_data.add_y_col()
        try:
            with_y.getInfo()
        except Exception as e:
            self.fail(e)
        pprint(with_y.first().getInfo())

if __name__ == '__main__':
    unittest.main()
