from abc import ABC, abstractmethod
from typing import List, Dict, Union
import ee


TrainingData = ee.FeatureCollection
ColumnName = str


class RandomForestModel:
    def __init__(
        self,
        n_trees: int = 1000,
        var_per_split: int = None,
        min_leaf_pop: int = 1,
        bag_frac: float = 0.5,
        max_nodes: int = None,
        seed: int = 0,
    ) -> None:
        self.numberOfTrees = n_trees
        self.variablesPerSplit = var_per_split
        self.minLeafPopulation = min_leaf_pop
        self.bagFraction = bag_frac
        self.maxNodes = max_nodes
        self.seed = seed
        self.outputmode = "CLASSIFICATION"
        self._model = ee.Classifier.smileRandomForest(
            **{
                "numberOfTrees": self.numberOfTrees,
                "variablesPerSplit": self.variablesPerSplit,
                "minLeafPopulation": self.minLeafPopulation,
                "bagFraction": self.bagFraction,
                "maxNodes": self.maxNodes,
                "seed": self.seed,
            }
        )

    def __repr__(self) -> str:
        return f"RandomForestModel(n_trees={self.numberOfTrees}, var_per_split={self.variablesPerSplit}, min_leaf_pop={self.minLeafPopulation}, bag_frac={self.bagFraction},max_nodes={self.maxNodes}, seed={self.seed})"

    @property
    def model(self):
        return self._model

    @property
    def set_output_mode(self):
        return self.outputmode

    @set_output_mode.setter
    def set_output_mode(self, outputmode):
        if outputmode.lower() not in ["classification", "multiprobability"]:
            raise ValueError(
                f"outputmode must be either 'classification' or 'regression' not {outputmode}"
            )
        self.outputmode = outputmode.upper()
        self._model = self._model.setOutputMode(self.outputmode)

    def fit(
        self,
        features: TrainingData,
        classProperty: ColumnName,
        inputProperties: List[ColumnName],
    ):
        self._model = self._model.train(features, classProperty, inputProperties)
        return self

    def apply(
        self, X: Union[ee.Image, ee.FeatureCollection]
    ) -> Union[ee.Image, ee.FeatureCollection]:
        if isinstance(X, ee.Image):
            return X.classify(self._model).uint8()

        return X.classify(self._model)
