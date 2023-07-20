from dataclasses import dataclass, field
from math import pi
from typing import List, Dict, Callable
import ee

Optical = ee.ImageCollection
Harmonics = int
Dependent = str
Independent = List[str]
HarmonicsCollection = ee.ImageCollection
CosNames = List[str]
SinName = List[str]


class HarmonicsBuilder:
    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, value: Optical):
        self._builder = value

    def add_dependent(self, func: callable):
        self._builder.col = self._builder.map(func)
        return self

    def add_constant(self):
        def wrapper(image):
            return image.addBands(ee.Image.constant(1))

        self._builder.col = self._builder.map(wrapper)
        return self

    def add_time(self, omega: float = 1.0):
        def wrapper(image):
            date = ee.Date(image.get("system:time_start"))
            years = date.difference(ee.Date("1970-01-01"), "year")
            time_radians = ee.Image(years.multiply(2 * pi * omega).rename("t"))
            return image.addBands(time_radians.float())

        self.col = self.col.map(wrapper)
        return self

    def add_harmonics(self, cos: CosNames, sin: SinName):
        if len(cos) != len(sin):
            raise ValueError("Number of cosines must equal number of sines")

        freqs = (len(cos) + len(sin)) // 2

        def wrapper(image):
            frequencies = ee.Image.constant(freqs)
            time = ee.Image(image).select("t")
            cosines = time.multiply(frequencies).cos().rename(cos)
            sines = time.multiply(frequencies).sin().rename(sin)
            return image.addBands(cosines).addBands(sines)

        self._builder = self._builder.map(wrapper)
        return self

    def build(self):
        return self


class HarmonicTrend:
    def __init__(
        self, col: HarmonicsCollection, ind: Independent, dep: Dependent
    ) -> None:
        self.col = col
        self.ind = ind
        self.dep = dep
        self._harmonic_trend = self._trend()

    def _trend(self) -> ee.ComputedObject:
        return self.col.select(self.ind.append(self.dep)).reduce(
            ee.Reducer.linearRegression(len(self.ind), 1)
        )

    @property
    def harmonic_trend(self):
        return self._harmonic_trend

    @property
    def harmonic_trend_coefficients(self) -> ee.ComputedObject:
        return (
            self.harmonic_trend.select("coefficients")
            .arrayProject([0])
            .arrayFlatten([self.ind, ["coeff"]])
        )


class FourierTransform:
    def __init__(self) -> None:
        self.builder: Optical = None

    def add_coefficients(self, coefficients: ee.Image) -> None:
        self.builder = self.builder.map(lambda image: image.addBands(coefficients))
        return self

    def add_amplitude(self, mode: int):
        def mk_amplitude(image):
            sin_coef = image.select(f"sin_{mode}_coeff")
            cos_coef = image.select(f"cos_{mode}_coeff")
            amp = sin_coef.atan2(cos_coef).rename(f"amp_{mode}")
            return image.addBands(amp)

        self.builder = self.builder.map(mk_amplitude)
        return self

    def add_phase(self, mode: int):
        def mk_phase(image):
            sin_coef = image.select(f"sin_{mode}")
            cos_coef = image.select(f"cos_{mode}")
            phase = sin_coef.atan2(cos_coef).rename(f"phase_{mode}")
            return image.addBands(phase)

        self.builder = self.builder.map(mk_phase)
        return self

    def build(self):
        return self
