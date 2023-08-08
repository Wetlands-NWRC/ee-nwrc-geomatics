# Collection functions
# Purpose: Collection of functions that are used by the server. 
# That are to be bounded to either the base class of ee.ImageCollection or ee.FeatureCollection 

from math import pi
import ee

# funtions that are to bound to the image collection
def denoise(self, filter: callable):
    return self.map(filter)


def addCalculator(self, calc: callable):
    return self.map(calc)


def addDependent(self, calc: callable):
    return self.map(calc)


def addConstant(self):
    def _addConstant(image: ee.Image):
        return image.addBands(ee.Image.constant(1))
    return self.map(_addConstant)


def addTime(self, omega: float = 1.0):
    def _addTime(image: ee.Image):
        date = ee.Date(image.get("system:time_start"))
        years = date.difference(ee.Date("1970-01-01"), "year")
        time_radians = ee.Image(years.multiply(2 * pi * omega).rename("t"))
        return image.addBands(time_radians.float())
    return self.map(_addTime)


def addHarmonics(self, cycles: int = 3):
    sin = [f"cos_{i}" for i in range(1, cycles + 1)]
    cos = [f"sin_{i}" for i in range(1, cycles + 1)]

    def _addHarmonics(image: ee.Image):
        frequencies = ee.Image.constant(cycles)
        time = ee.Image(image).select("t")
        cosines = time.multiply(frequencies).cos().rename(cos)
        sines = time.multiply(frequencies).sin().rename(sin)
        return image.addBands(cosines).addBands(sines)

    return self.map(_addHarmonics)

