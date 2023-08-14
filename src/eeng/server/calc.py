from abc import ABC, abstractmethod
from typing import Any
import ee


BandName = str


class Calculator(ABC):
    def __call__(self, image: ee.Image) -> ee.Image:
        return image.addBands(self.calc)

    @abstractmethod
    def calc(self, image: ee.Image) -> ee.Image:
        pass


class Ratio(Calculator):
    def __init__(self):
        self.numerator: BandName = "VV"
        self.demoninator: BandName = "VH"
        self.name: str = "VV/VH"

    def calc(self, image: ee.Image) -> ee.Image:
        calc = (
            image.select(self.numerator)
            .divide(image.select(self.demoninator))
            .rename(self.name)
        )
        return calc


class NDVI(Calculator):
    def __init__(self, nir: str = None, red: str = None, name: str = None) -> None:
        self.nir: BandName = "B8" if nir is None else nir
        self.red: BandName = "B4" if red is None else red
        self.name: str = "NDVI" if name is None else name

    def calc(self, image: ee.Image) -> ee.Image:
        calc = image.normalizedDifference([self.nir, self.red]).rename(self.name)
        return calc


class SAVI(Calculator):
    def __init__(self, nir: str = None, red: str = None, name: str = None) -> None:
        self.nir: BandName = "B8" if nir is None else nir
        self.red: BandName = "B4" if red is None else red
        self.name: str = "SAVI" if name is None else name
        self.L: float = 0.5

    def calc(self, image: ee.Image) -> ee.Image:
        calc = image.expression(
            "(1 + L) * (NIR - RED) / (NIR + RED + L)",
            {
                "NIR": image.select(self.nir),
                "RED": image.select(self.red),
                "L": self.L,
            },
        ).rename(self.name)
        return calc


class TasselCap(Calculator):
    def __init__(
        self,
        blue: str = None,
        green: str = None,
        red: str = None,
        nir: str = None,
        swir1: str = None,
        swir2: str = None,
    ) -> None:
        self.blue = "B2" if blue is None else blue
        self.green = "B3" if green is None else green
        self.red = "B4" if red is None else red
        self.nir = "B8" if nir is None else nir
        self.swir1 = "B11" if swir1 is None else swir1
        self.swir2 = "B12" if swir2 is None else swir2
        super().__init__()

    def cacl(self, image: ee.Image) -> ee.Image:
        image = image.select(list(self.__dict__.values()))
        co_array = [
            [0.3037, 0.2793, 0.4743, 0.5585, 0.5082, 0.1863],
            [-0.2848, -0.2435, -0.5436, 0.7243, 0.0840, -0.1800],
            [0.1509, 0.1973, 0.3279, 0.3406, -0.7112, -0.4572],
        ]

        co = ee.Array(co_array)

        arrayImage1D = image.toArray()
        arrayImage2D = arrayImage1D.toArray(1)

        components_image = (
            ee.Image(co)
            .matrixMultiply(arrayImage2D)
            .arrayProject([0])
            .arrayFlatten([["Brightness", "Greenness", "Wetness"]])
        )

        return components_image
