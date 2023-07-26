import ee

from .rmath import *
from .despekle import DespeckleAlgorithm


class Sentinel1(ee.ImageCollection):

    def __init__(self, args=None):
        args = args if args is not None else "COPERNICUS/S1_GRD"
        super().__init__(args)

    def addRatio(self, ratio: Ratio):
        return self.map(ratio)

    def despekle(self, filter: DespeckleAlgorithm):
        return self.map(filter)


class Sentinel2(ee.ImageCollection):

    @classmethod
    def toa(cls):
        """ Factory method for Sentinel2 TOA image collection """
        return cls("COPERNICUS/S2")

    @classmethod
    def probability(cls):
        """ Factory method for Sentinel2 cloud probability image collection"""
        return cls("COPERNICUS/S2_CLOUD_PROBABILITY")

    @classmethod
    def sr(cls):
        """ Factory method for Sentinel2 SR image collection """
        return cls("COPERNICUS/S2_SR")

    def __init__(self, agrs=None):
        args = agrs if agrs is not None else "COPERNICUS/S2_SR"
        super().__init__(args)

    def addNDVI(self, ndvi: NDVI):
        return self.map(ndvi)

    def addSAVI(self, savi: SAVI):
        return self.map(savi)


class ALOS2(ee.ImageCollection):
    def __init__(self):
        super().__init__("JAXA/ALOS/PALSAR/YEARLY/SAR")


class DataCube(ee.ImageCollection):
    SEASON_PREFIX = {"spring": "a_spri_b", "summer": "b_summ_b", "fall": "c_fall_b"}

    def __init__(self, args):
        super().__init__(args)

    @property
    def spring(self):
        return self.select(f'{self.SEASON_PREFIX["spring"]}.*')

    @property
    def summer(self):
        return self.select(f'{self.SEASON_PREFIX["summer"]}.*')

    @property
    def fall(self):
        return self.select(f'{self.SEASON_PREFIX["fall"]}.*')


class Stack:
    def __init__(self):
        self._stack = []

    def add(self, image: ee.Image):
        if not isinstance(image, ee.Image):
            raise TypeError("image must be an ee.Image")
        self._stack.append(image)
        return self

    def concat(self) -> ee.Image:
        """ Concatenate all images in the stack """
        return ee.Image.cat(*self._stack)
