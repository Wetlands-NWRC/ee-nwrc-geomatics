# Collection functions
# Purpose: Collection of functions that are used by the server. 
# That are to be bounded to either the base class of ee.ImageCollection or ee.FeatureCollection 

from math import pi
import ee

# image collection factory functions
@classmethod
def sentinel2SR(cls, start, end, aoi, cloud_px_percent: int = 10):
    """ """
    instance = cls("COPERNICUS/S2_SR").filterBounds(aoi).filterDate(start, end).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_px_percent))
    return instance


@classmethod
def sentinel2TOA(cls, start, end, aoi, cloud_px_percent: int = 10):
    """ """
    instance = cls("COPERNICUS/S2").filterBounds(aoi).filterDate(start, end).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_px_percent))
    return instance

@classmethod
def sentinel2CloudProbability(cls, start, end, aoi):
    """ """
    instance = cls("COPERNICUS/S2_CLOUD_PROBABILITY").filterBounds(aoi).filterDate(start, end)
    return instance

@classmethod
def sentinel2Cloudless(cls, s2_col, s2_prob):
    join = ee.Join.saveFirst('s2cloudless').apply(**{
        'primary': s2_col,
        'secondary': s2_prob,
        'condition': ee.Filter.equals(**{
            'leftField': 'system:index',
            'rightField': 'system:index'
        })
    })

    return cls(join)


@classmethod
def sentinel1DV(cls, start, end, aoi):
    instance = cls("COPERNICUS/S1_GRD").filterBounds(aoi).filterDate(start, end).filter(ee.Filter([
        ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'),
        ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')
    ]))
    return instance.select("VV", "VH")

@classmethod
def alos(cls, start, end, aoi):
    instance = cls("JAXA/ALOS/PALSAR/YEARLY/SAR").filterBounds(aoi).filterDate(start, end)
    return instance.select("HH", "HV")

# funtions that are to bound to the image collection
def denoise(self, filter: callable):
    return self.map(filter)


def addCalculator(self, calc: callable):
    return self.map(calc)


def add_cloud_mask(self, cloud_mask: callable):
    return self.map(cloud_mask)


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


# Feature Collection bounding methods
ColumnName = str

def add_x_coordinate(self, x: ColumnName = None):
    """ adds the x coordinate column to the feature collection
    Args:
        x (ColumnName, optional): [description]. Defaults to x.

    """
    x = 'x' if x is None else x
    def _add_x_col(feature: ee.Feature) -> ee.Feature:
        geom = feature.geometry().centroid().coordinates()
        return feature.set({x: geom.get(0)})
    return self.map(_add_x_col)


def add_y_coordinate(self, y: ColumnName = None):
    y = 'y' if y is None else y
    def _add_y_col(feature: ee.Feature) -> ee.Feature:
        geom = feature.geometry().centroid().coordinates()
        return feature.set({y: geom.get(1)})
    return self.map(_add_y_col)


def generate_samples(self, image: ee.Image, props: list[ColumnName] = None, scale: int = 10, tileScale: int = 16) -> ee.FeatureCollection:
    """ generates samples from the image. It is a geometry less feature collection"""
    props = [] if props is None else props
    sample = image.sampleRegions(
        collection=self,
        scale=10,
        properties=props,
        tileScale=16,
    )
    return sample


def lookup(self, column: ColumnName, sorted: bool = False) -> ee.Dictionary:
    """ returns a dictionary of the unique values in the column and their associated value alphabetically sorted"""
    if sorted:
        keys = self.aggregate_array(column).distinct().sort()
    else:
        keys = self.aggregate_array(column).distinct()
    values = ee.List.sequence(1, keys.size())
    return ee.Dictionary.fromLists(keys, values)


def remap_from_lookup(self, column: ColumnName, lookup: ee.Dictionary) -> ee.FeatureCollection:
    pass
