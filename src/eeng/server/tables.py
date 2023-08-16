import ee

ColumnName = str


class TrainingPoints(ee.FeatureCollection):
    def __init__(
        self, args, classProperty: ColumnName = None, opt_column: ColumnName = None
    ):
        super().__init__(args, opt_column)
        self.classProperty = classProperty
        self._properties = []
        self.labels = classProperty
        self.values = self.labels

    @property
    def properties(self):
        return self._properties

    @property
    def lookup(self) -> ee.Dictionary:
        return ee.Dictionary.fromLists(self.labels, self.values)

    @property
    def classProperty(self):
        return self._classProperty

    @classProperty.setter
    def classProperty(self, value):
        self.classProperty = "class_name" if value is None else value
        self._properties.append(self.classProperty)

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, value):
        self._labels = self.aggregate_array(value).distinct()

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, value: ee.List):
        self._values = ee.List.sequence(1, value.size())

    def addXCoordinate(self):
        """adds the x coordinate of the geometry to the feature collection"""

        def add_x_coordinate(feature):
            geom = feature.geometry().centroid(1).coordinates().get(0)
            return feature.set("x", geom)

        self._properties.append("x")
        return self.map(add_x_coordinate)

    def addYCoordinate(self):
        """adds the y coordinate of the geometry to the feature collection"""

        def add_y_coordinate(feature):
            geom = feature.geometry().centroid(1).coordinates().get(1)
            return feature.set("y", geom)

        self._properties.append("y")
        return self.map(add_y_coordinate)

    def generateSamples(
        self, image: ee.Image, scale: int = 10, tileScale: int = 16
    ) -> ee.FeatureCollection:
        """Uses Image.sampleRegions method to generate training points from an image. Returns a geometryless feature collection with the specified properties."""
        sample = image.sampleRegions(
            collection=self,
            scale=scale,
            properties=self.properties,
            tileScale=tileScale,
            geometries=False,
        )

        pts = TrainingPoints(sample, self.classProperty)
        return pts

    def getLookupTable(self) -> ee.FeatureCollection:
        zipped = self.labels.zip(self.values)

        def mkfeat(pair: ee.ComputedObject):
            pair = ee.List(pair)
            return ee.Feature(None, {"label": pair.get(0), "value": pair.get(1)})

        return ee.FeatureCollection(zipped.map(mkfeat))
