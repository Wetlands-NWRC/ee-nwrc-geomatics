import ee

from typing import List, Dict, Union
from abc import ABC, abstractmethod

from eeng.server.models import RandomForestModel


TrainingData = ee.FeatureCollection
ColumnName = str


class RandomForestClassification:
    def __init__(self):
        self.model = RandomForestModel()

    @property
    def model(self):
        return self.model

    @model.setter
    def model(self, model):
        if not isinstance(model, RandomForestModel):
            raise ValueError(
                f"model must be a RandomForestModel instance not {type(model)}"
            )
        self.model = model.set_output_mode = "CLASSIFICATION"

    def fit(
        self,
        features: TrainingData,
        classProperty: ColumnName,
        inputProperties: List[ColumnName],
    ):
        self.classifier = self.__model.train(features, classProperty, inputProperties)
        return self

    def apply(
        self, X: Union[ee.Image, ee.FeatureCollection]
    ) -> Union[ee.Image, ee.FeatureCollection]:
        if self.classifier is None:
            raise ValueError(
                "Classifier has not been trained. Call the fit method before calling apply"
            )

        if isinstance(X, ee.Image):
            return X.classify(self.classifier).uint8()
        return X.classify(self.classifier)


class RandomForestMultiProbability:
    def __init__(self, model: RandomForestModel):
        self.__model = model.set_output_mode = "MULTIPROBABILITY"
        self.array_image = None

    def fit(
        self,
        features: TrainingData,
        classProperty: ColumnName,
        inputProperties: List[ColumnName],
    ):
        self.classifier = self.__model.train(features, classProperty, inputProperties)
        return self

    def apply(self, X: ee.Image) -> None:
        if not isinstance(X, ee.Image):
            raise ValueError(
                "Input must be an ee.Image. Use RandomForestClassification for ee.FeatureCollections"
            )
        if self.classifier is None:
            raise ValueError(
                "Classifier has not been trained. Call the fit method before calling apply"
            )
        self.array_image = X.classify(self.classifier)
        return None

    def get_probability(self, band_names: List[str] | ee.List) -> ee.Image:
        if self.array_image is None:
            raise ValueError(
                "Classifier has not been trained or applied. Call the fit and apply methods before calling get_probability"
            )
        return self.array_image.arrayFlatten([band_names])
