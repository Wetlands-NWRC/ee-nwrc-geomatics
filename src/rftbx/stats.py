from typing import List
import ee

Labels = List[str]

class Assessment:
    def __init__(self, validation: ee.FeatureCollection) -> None:
        self._matrix: ee.Feature = self._build_confusion_matrix(validation, "class", "classification")
        self.cfm: ee.Feature = None
        self.accuracy: ee.Feature = None
        self.producers: ee.Feature = None
        self.consumers: ee.Feature = None

    @staticmethod
    def _build_confusion_matrix(validation: ee.FeatureCollection, classProperty: str, predictedProperty: str) -> ee.Feature:
        return validation.errorMatrix(classProperty, predictedProperty)

    @property
    def confusion_matrix(self):
        return self._matrix

    def generate_matrix(self):
        self.cfm = ee.Feature(
            None, {"cfm", self._assessment.matrix.array().slice(0, 1).slice(1, 1)}
        )
        return self
    
    def generate_accuracy(self):
        self._accuracy = ee.Feature(None, {"accuracy": self._matrix.accuracy()})
        return self
    
    def generate_producers(self):
        self._producers = ee.Feature(
            None, {"producers": self._matrix.producersAccuracy().toList().flatten().slice(1)}
        )
        return self

    def generate_consumers(self):
        self._producers = ee.Feature(
            None, {"consumers": self._matrix.consumersAccuracy().toList().flatten().slice(1)}
        )
    
    def add_labels(self, labels: Labels):
        self._labels = ee.Feature(None, {"labels": labels})
        return self

    def build(self) -> ee.FeatureCollection:
        # cast and format the matrix
        return ee.FeatureCollection([v for v in self.__dict__.values() if isinstance(v, ee.Feature)])
        