from typing import Dict, Union
import ee

ColumnName = str
ColumnMapping = Union[Dict[str, int], ee.Dictionary]


class TabularFunctions:
    def remap(
        collection: ee.FeatureCollection, column: ColumnName, mapping: ColumnMapping
    ) -> ee.FeatureCollection:
        if isinstance(mapping, dict):
            mapping = ee.Dictionary(mapping)

        lookup_in = ee.List(mapping.keys())
        lookup_out = ee.List(mapping.values())
        return collection.remap(lookup_in, lookup_out, column)

    def insert_xy(x: str = None, y: str = None) -> callable:
        x = "x" if x is None else x
        y = "y" if y is None else y

        def insert_xy_inner(feature: ee.Feature) -> ee.Feature:
            geom = feature.geometry().coordinates()
            return feature.set(
                {
                    x: geom.get(0),
                    y: geom.get(1),
                }
            )

        return insert_xy_inner
