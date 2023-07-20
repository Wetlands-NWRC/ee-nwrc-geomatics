import json
from typing import List
import ee

ConfusionMatrix = ee.ComputedObject
ColumnName = str


class Assessment:
    def __init__(self, matrix: ConfusionMatrix) -> None:
        self._matrix = matrix

    @property
    def matrix(self) -> ConfusionMatrix:
        return self._matrix

    @property
    def accuracy(self) -> ee.Number:
        return self._matrix.accuracy()

    @property
    def producers(self):
        return self._matrix.producersAccuracy()

    @property
    def consumers(self):
        return self._matrix.consumersAccuracy()


class AssessmentFormatter:
    def __init__(self, assessment: Assessment):
        self._assessment = assessment

    def format(self) -> ee.FeatureCollection:
        matrix = ee.Feature(
            None, {"cfm", self._assessment.matrix.array().slice(0, 1).slice(1, 1)}
        )

        accuracy = ee.Feature(None, {"overall": self._assessment.accuracy})

        producers = ee.Feature(
            None, {"producers": self._assessment.producers.toList().flatten().slice(1)}
        )

        consumers = ee.Feature(
            None, {"consumers": self._assessment.consumers.toList().flatten().slice(1)}
        )

        return ee.FeatureCollection([matrix, accuracy, producers, consumers])


class AssessmentTable:
    def __init__(self, assessmnet_json, lookup, on: str = None) -> None:
        self._assessment = assessmnet_json
        self._lookup = lookup
        self._on = "class" if on is None else on

    @staticmethod
    def _extract_labels(filename, on) -> List[str]:
        return pd.read_csv(filename)[on].to_list()

    @staticmethod
    def _unpack_data(filename: str) -> dict:
        with open(filename, "r") as f:
            return json.load(f)
