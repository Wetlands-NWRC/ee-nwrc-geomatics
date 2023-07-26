from dataclasses import dataclass
from typing import Dict, Union
import ee

ColumnName = str
ColumnMapping = Union[Dict[str, int], ee.Dictionary]
Lookup = ee.Dictionary


class TrainingData(ee.FeatureCollection):
    def __init__(self, args, opt_column=None):
        super().__init__(args, opt_column)
        self.class_property: ColumnName = 'Wetland'

        # TODO add a validation check to ensure the class property is in the feature collection

    @property
    def lookup(self) -> Lookup:
        keys = self.aggregate_array(self.class_property).distinct().sort()
        values = ee.List.sequence(1, keys.size())
        return ee.Dictionary.fromLists(keys, values)


    def remap_(self, mapping: ColumnMapping):
        if isinstance(mapping, dict):
            # if any key value is not a string then convert to string
            for key in mapping.keys():
                if not isinstance(key, str):
                    mapping[str(key)] = mapping.pop(key)
            mapping = ee.Dictionary(mapping)

        lookup_in = ee.List(mapping.keys())
        lookup_out = ee.List(mapping.values()).map(lambda x: ee.Number(x).int())

        return TrainingData(self.remap(lookup_in, lookup_out, self.class_property))


    def add_x_col(self, x: ColumnName = None):
        """ adds the x coordinate column to the feature collection
        Args:
            x (ColumnName, optional): [description]. Defaults to x.

        """
        x = 'x' if x is None else x
        def _add_x_col(feature: ee.Feature) -> ee.Feature:
            geom = feature.geometry().coordinates()
            return feature.set({x: geom.get(0)})
        return self.map(_add_x_col)

    def add_y_col(self, y: ColumnName = None):
        y = 'y' if y is None else y
        def _add_y_col(feature: ee.Feature) -> ee.Feature:
            geom = feature.geometry().coordinates()
            return feature.set({y: geom.get(1)})
        return self.map(_add_y_col)

