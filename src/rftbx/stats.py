import ee


class Assessment:
    def __init__(self, validation: ee.FeatureCollection) -> None:
        self._validation = validation
        self._matrix: ee.Feature = None
        self._accuracy: ee.Feature = None
        self._producers: ee.Feature = None
        self._consumers: ee.Feature = None

    def generate_matrix(self, classProperty: str, predictedProperty: str):
        self._matrix = self._validation.errorMatrix(classProperty, predictedProperty)
        return self
    
    def generate_accuracy(self):
        self._accuracy = ee.Feature(None, {"accuracy": self._matrix.accuracy()})
        return self
    
    def generate_producers(self):
        self._producers = ee.Feature(
            None, {"producers": self._matrix.producersAccuracy().toList().flatten().slice(1)}
        )
        return self
    
    def build() -> ee.FeatureCollection:
        pass