from typing import List, Dict, Callable
import ee

from .tsm.fourier import *
from ..rftbx.rmath import OpticalBandMath

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

    def apply(self, image: ee.Image) -> ee.Image:
        return image.classify(self._model).uint8()

    def validate(self, validationData) -> ee.FeatureCollection:
        return validationData.classify(self._model)


class TimeSeriesModeling:
    def fourier_transform(
        col: ee.ImageCollection, cycles: int = 3, dependent: Dict[str, Callable] = None
    ) -> ee.ImageCollection:
        dependent = {"NDVI": OpticalBandMath.ndvi()} if dependent is None else dependent

        cos = [f"cos_{i}" for i in range(1, cycles + 1)]
        sin = [f"sin_{i}" for i in range(1, cycles + 1)]

        independent = ["constant", "t"] + cos + sin
        dependent = list(dependent.keys())[0]

        harmbldr = HarmonicsBuilder()
        harmbldr.builder = col
        harmbldr.add_dependent(dependent.get("NDVI"))
        harmbldr.add_constant()
        harmbldr.add_time()
        harmbldr.add_harmonics(cycles)
        harmbldr.build()

        trend = HarmonicTrend(col=harmbldr.builder, ind=independent, dep=dependent)

        ftbldr = FourierTransform()
        ftbldr.builder = col
        ftbldr.add_coefficients(trend.harmonic_trend_coefficients.select(".*coeff"))

        # add amplitude and phase for n number of harmonics
        for cycle in cycles:
            ftbldr.add_amplitude(cycle)
            ftbldr.add_phase(cycle)

        ftbldr.build()

        ft_image = ftbldr.builder.median().unitScale(-1, 1)
        return ft_image.select(".*coeff | amp.* | phase.*")
