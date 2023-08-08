import ee
from .calc import *
from .collections import denoise, addCalculator


ee.ImageCollection.addCalculator = addCalculator
ee.ImageCollection.denoise = denoise