from abc import ABC, abstractmethod
from typing import Any
import ee


BandName = str

# TODO - Update Band Math to be Object Oriented
# TODO - Create an Abstract Base Class for Band Math


class Calculator(ABC):

    @abstractmethod
    def __call__(self, image: ee.Image) -> ee.Image:
        pass

    @abstractmethod
    def calc(self, image: ee.Image) -> ee.Image:
        pass


class Ratio(BandMath):
    def __init__(self):
        self.numerator: BandName = 'VV'
        self.demoninator: BandName = 'VH'
        self.name: str = 'VV/VH'

    def __call__(self, image: ee.Image) -> ee.Image:
        return image.addBands(self.calc(image))

    def calc(self, image: ee.Image) -> ee.Image:
        calc = image.select(self.numerator).divide(image.select(self.demoninator)).rename(self.name)
        return calc


class NDVI(BandMath):
    def __init__(self):
        self.nir: BandName = 'B8'
        self.red: BandName = 'B4'
        self.name: str = 'NDVI'

    def __call__(self, image: ee.Image) -> ee.Image:
        return image.addBands(self.calc(image))

    def calc(self, image: ee.Image) -> ee.Image:
        calc = image.normalizedDifference([self.nir, self.red]).rename(self.name)
        return calc


class SAVI(BandMath):
    def __init__(self):
        self.nir: BandName = 'B8'
        self.red: BandName = 'B4'
        self.name: str = 'SAVI'
        self.L: float = 0.5

    def __call__(self, image: ee.Image) -> ee.Image:
        return image.addBands(self.calc(image))

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


def addCalculator(self, calculator: BandMath):
    if not issubclass(calculator, BandMath):
        raise TypeError("calculator must be a subclass of BandMath")
    return self.map(calculator)


class OpticalBandMath:
    def ndvi(nir: BandName = None, red: BandName = None) -> callable:
        nir = "B8" if nir is None else nir
        red = "B4" if red is None else red

        def wrapper(image: ee.Image) -> ee.Image:
            calc = image.normalizedDifference([nir, red]).rename("NDVI")
            return image.addBands(calc)

        return wrapper

    def savi(nir: BandName = None, red: BandName = None, L: float = 0.5):
        nir = "B8" if nir is None else nir
        red = "B4" if red is None else red

        def wrapper(image: ee.Image) -> ee.Image:
            calc = image.expression(
                "(1 + L) * (NIR - RED) / (NIR + RED + L)",
                {
                    "NIR": image.select(nir),
                    "RED": image.select(red),
                    "L": L,
                },
            ).rename("SAVI")
            return image.addBands(calc)
        return wrapper


    def tassel_cap(
        blue: str = None,
        green: str = None,
        red: str = None,
        nir: str = None,
        swir1: str = None,
        swir2: str = None,
    ) -> callable:
        blue = "B2" if blue is None else blue
        green = "B3" if green is None else green
        red = "B4" if red is None else red
        nir = "B8" if nir is None else nir
        swir1 = "B11" if swir1 is None else swir1
        swir2 = "B12" if swir2 is None else swir2

        def wrapper(image: ee.Image) -> ee.Image:
            _img = image.select([blue, green, red, nir, swir1, swir2])

            co_array = [
                [0.3037, 0.2793, 0.4743, 0.5585, 0.5082, 0.1863],
                [-0.2848, -0.2435, -0.5436, 0.7243, 0.0840, -0.1800],
                [0.1509, 0.1973, 0.3279, 0.3406, -0.7112, -0.4572],
            ]

            co = ee.Array(co_array)

            arrayImage1D = _img.toArray()
            arrayImage2D = arrayImage1D.toArray(1)

            components_image = (
                ee.Image(co)
                .matrixMultiply(arrayImage2D)
                .arrayProject([0])
                .arrayFlatten([["Brightness", "Greenness", "Wetness"]])
            )

            return image.addBands(components_image)

        return wrapper


class SARBandMath:
    def ratio(band1: str, band2: str, name: str) -> callable:
        name = f"{band1}/{band2}"

        def wrapper(image: ee.Image) -> ee.Image:
            calc = image.select(band1).divide(image.select(band2)).rename(name)
            return image.addBands(calc)

        return wrapper
