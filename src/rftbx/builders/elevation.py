from dataclasses import dataclass
from typing import Callable
import ee
import tagee

from ..datasets import NASADEM


@dataclass
class ElevationDataset:
    dataset: ee.Image = NASADEM()
    rectangle: ee.Geometry = None
    band_selectors: list = None


class ElevationBuilder:
    pass


class TerrainAnalysisBuilder:
    def __init__(self) -> None:
        self.builder: ElevationDataset = ElevationDataset()

    def add_spatial_filter(self, filter: Callable):
        self.builder = self.builder.dataset.map(filter)
        return self

    def add_rectangle(self, rectangle: ee.Geometry):
        self.builder.dataset.rectangle = rectangle
        return self

    def add_band_selections(self, band_selections: list):
        self.builder.dataset.band_selectors = band_selections
        return self

    def build(self):
        ta = tagee.terrainAnalysis(self.builder.dataset, self.builder.rectangle)
        self.builder.dataset = (
            ta.select(self.builder.band_selectors)
            if self.builder.band_selectors is not None
            else ta
        )
        return self
