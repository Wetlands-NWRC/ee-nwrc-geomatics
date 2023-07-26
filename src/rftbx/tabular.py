from dataclasses import dataclass
from typing import Dict, Union
import ee

ColumnName = str
ColumnMapping = Union[Dict[str, int], ee.Dictionary]
Lookup = ee.Dictionary


class TrainingData:
    def __init__(self, args):
        self.raw = self._instaniate_collection(args)
        self.class_property: ColumnName = 'Wetland'
        self._lookup = self._build_lookup(self.raw, self.class_property)
        # TODO add a validation check to ensure the class property is in the feature collection

    @property
    def lookup(self) -> Lookup:
        return self._lookup

    @staticmethod
    def _instaniate_collection(args: ee.FeatureCollection):
        """ helps construct the collection from VALID arguments """
        if isinstance(args, ee.FeatureCollection):
            return args
        return ee.FeatureCollection(args)

    @staticmethod
    def _build_lookup(collection: ee.FeatureCollection, column: ColumnName) -> Lookup:
        keys = collection.aggregate_array(column).distinct().sort()
        values = ee.List.sequence(1, keys.size())
        return ee.Dictionary.fromLists(keys, values)

    def remap_cls_prop(self, mapping: ColumnMapping = None):
        if mapping is not None and isinstance(mapping, dict):
            # if any key value is not a string then convert to string
            for key in mapping.keys():
                if not isinstance(key, str):
                    mapping[str(key)] = mapping.pop(key)
            mapping = ee.Dictionary(mapping)
        else:
            mapping = self.lookup

        lookup_in = ee.List(mapping.keys())
        lookup_out = ee.List(mapping.values()).map(lambda x: ee.Number(x).int())
        self.raw = self.raw.remap(lookup_in, lookup_out, self.class_property)
        return self

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


