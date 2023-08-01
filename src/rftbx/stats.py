from typing import Any,  List
import ee

Labels = List[str]
ConfusionMatrix = Any
ColumnName = str
ClassificationName = str


def make_confusion_matrix(validation, on: ColumnName = None, name: ClassificationName = None) -> ConfusionMatrix:
    name = 'classification' if name is None else name
    on = 'Wetland' if on is None else on
    return validation.errorMatrix(on, name)


class Assessment:
    def __init__(self, confusion_matrix: ConfusionMatrix) -> None:
        self._matrix = confusion_matrix
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

    def add_matrix(self):
        """ adds a formatted confusion matrix to the assessment """
        self.cfm = ee.Feature(
            None, {"cfm", self._assessment.matrix.array().slice(0, 1).slice(1, 1)}
        )
        return self
    
    def add_accuracy(self):
        """ add the overall accuracy to the assessment """
        self._accuracy = ee.Feature(None, {"accuracy": self._matrix.accuracy()})
        return self
    
    def add_producers(self):
        """ add the producers accuracy to the assessment """
        self._producers = ee.Feature(
            None, {"producers": self._matrix.producersAccuracy().toList().flatten().slice(1)}
        )
        return self

    def add_consumers(self):
        """ add the consumers accuracy to the assessment """
        self._producers = ee.Feature(
            None, {"consumers": self._matrix.consumersAccuracy().toList().flatten().slice(1)}
        )
    
    def add_labels(self, labels: Labels):
        """ add the labels to the assessment """
        self._labels = ee.Feature(None, {"labels": labels})
        return self

    def build(self) -> ee.FeatureCollection:
        """ build the assessment, needs to run inorder to export the assessment """
        # cast and format the matrix
        return ee.FeatureCollection([v for v in self.__dict__.values() if isinstance(v, ee.Feature)])
        