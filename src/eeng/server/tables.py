import ee

ColumnName = str


class TrainingPoints:
    """This is a builder Class that is used to build Traning Points dataset from a Feature Collection that is assuemd to be a collection of points"""

    def __init__(
        self,
        points: ee.FeatureCollection,
        classProperty: ColumnName = None,
    ):
        self.properties = []
        self.points = points
        self.classProperty = classProperty
        self._add_propertity(classProperty)

    @property
    def labels(self):
        return self.points.aggregate_array(self.classProperty).distinct()

    @property
    def values(self):
        return ee.List.sequence(1, self.labels.size())

    @property
    def lookup(self) -> ee.Dictionary:
        return ee.Dictionary.fromLists(self.labels, self.values)

    def __repr__(self) -> str:
        return f"TrainingPoints({self.points}, {self.classProperty})"

    def addXCoordinate(self):
        """adds the x coordinate of the geometry to the feature collection"""

        def add_x_coordinate(feature):
            geom = feature.geometry().centroid(1).coordinates().get(0)
            return feature.set("x", geom)

        self._add_propertity("x")
        self.points = self.points.map(add_x_coordinate)
        return self

    def addYCoordinate(self):
        """adds the y coordinate of the geometry to the feature collection"""

        def add_y_coordinate(feature):
            geom = feature.geometry().centroid(1).coordinates().get(1)
            return feature.set("y", geom)

        self._add_propertity("y")
        self.points = self.points.map(add_y_coordinate)
        return self

    def remap(self, lookup: ee.Dictionary):
        """Remaps the classProperty of the feature collection using the lookup table"""

        def remap(feature):
            return feature.set(
                self.classProperty, lookup.get(feature.get(self.classProperty))
            )

        self.points = self.points.map(remap)
        return self

    def addValues(self):
        """adds the values of the lookup table to the feature collection"""

        def add_values(feature):
            return feature.set(
                "value", self.lookup.get(feature.get(self.classProperty))
            )

        self._add_propertity("value")
        self.points = self.points.map(add_values)
        return self

    def generateSamples(self, image: ee.Image, scale: int = 10, tileScale: int = 16):
        """Uses Image.sampleRegions method to generate training points from an image. Returns a geometryless feature collection with the specified properties."""
        sample = image.sampleRegions(
            collection=self.points,
            scale=scale,
            properties=self.properties,
            tileScale=tileScale,
            geometries=False,
        )

        pts = TrainingPoints(sample, self.classProperty)
        pts.properties = self.properties
        return pts

    def getLookupTable(self) -> ee.FeatureCollection:
        zipped = self.labels.zip(self.values)

        def mkfeat(pair: ee.ComputedObject):
            pair = ee.List(pair)
            return ee.Feature(None, {"label": pair.get(0), "value": pair.get(1)})

        return ee.FeatureCollection(zipped.map(mkfeat))

    def _add_propertity(self, value):
        if value not in self.properties:
            self.properties.append(value)
