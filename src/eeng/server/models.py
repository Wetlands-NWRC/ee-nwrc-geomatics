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

        self._model = ee.Classifier.smileRandomForest(**self.__dict__)

    @property
    def model(self):
        return self._model

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
