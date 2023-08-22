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
        self._output_mode = "CLASSIFICATION"

    def __repr__(self) -> str:
        return f"RandomForestModel(n_trees={self.numberOfTrees}, var_per_split={self.variablesPerSplit}, min_leaf_pop={self.minLeafPopulation}, bag_frac={self.bagFraction},max_nodes={self.maxNodes}, seed={self.seed})"

    @property
    def model(self):
        return self._model

    @property
    def output_mode(self):
        return self._output_mode

    @output_mode.setter
    def output_mode(self, mode):
        self._output_mode = mode
        self._model = self._model.setOutputMode(self._output_mode)

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


class RandomForestClassifier:
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

        # private attributes
        self._rf_model = ee.Classifier.smileRandomForest(
            **{
                "numberOfTrees": n_trees,
                "variablesPerSplit": var_per_split,
                "minLeafPopulation": min_leaf_pop,
                "bagFraction": bag_frac,
                "maxNodes": max_nodes,
                "seed": seed,
            }
        )
        self._output_mode = "CLASSIFICATION"
        self._classifier = None

    @property
    def rf_model(self):
        return self._rf_model

    @property
    def output_mode(self):
        return self._output_mode

    @output_mode.setter
    def output_mode(self, mode):
        self._output_mode = mode
        self._rf_model = self._rf_model.setOutputMode(self._output_mode)

    @property
    def classifier(self):
        return self._classifier

    @classifier.setter
    def classifier(self, classifier):
        self._classifier = classifier
