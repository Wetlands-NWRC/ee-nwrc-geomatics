from dataclasses import dataclass
from typing import Dict, Union
import ee

ColumnName = str
ColumnMapping = Union[Dict[str, int], ee.Dictionary]
Lookup = ee.Dictionary


class TrainingPoints(ee.FeatureCollection):
    def __init__(self, args):
        super().__init__(args, None)
        self.class_property: ColumnName = 'Wetland'
        # TODO add a validation check to ensure the class property is in the feature collection

    def remap(self, mapping: ColumnMapping = None):
        if mapping is not None and isinstance(mapping, dict):
            # if any key value is not a string then convert to string
            for key in mapping.keys():
                if not isinstance(key, str):
                    mapping[str(key)] = mapping.pop(key)
            mapping = ee.Dictionary(mapping)
        else:
            lookupin = self.aggregate_array(self.class_property).distinct().sort()
            lookupout = ee.List.sequence(1, lookupin.size())
            mapping = ee.Dictionary.fromLists(lookupin, lookupout)

        def _remap(feature: ee.Feature) -> ee.Feature:
            return feature.set({self.class_property: mapping.get(feature.get(self.class_property))})
        
        return self.map(_remap)

    def add_x_col(self, x: ColumnName = None):
        """ adds the x coordinate column to the feature collection
        Args:
            x (ColumnName, optional): [description]. Defaults to x.

        """
        x = 'x' if x is None else x
        def _add_x_col(feature: ee.Feature) -> ee.Feature:
            geom = feature.geometry().coordinates()
            return feature.set({x: geom.get(0)})
        self.raw = self.raw.map(_add_x_col)
        return self

    def add_y_col(self, y: ColumnName = None):
        y = 'y' if y is None else y
        def _add_y_col(feature: ee.Feature) -> ee.Feature:
            geom = feature.geometry().coordinates()
            return feature.set({y: geom.get(1)})
        self.raw = self.raw.map(_add_y_col)
        return self

    def generate_samples(self, image: ee.Image, props: list[ColumnName] = None):
        """ generates samples from the image and adds them to the feature collection"""
        props = [self.class_property] if props is None else props
        self.raw = image.sampleRegions(
            collection=self.raw,
            scale=10,
            properties=props,
            tileScale=16,
        )
        return self


