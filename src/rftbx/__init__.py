import ee
from .rmath import *
from .denoise import denoise


ee.ImageCollection.addCalculator = addCalculator
ee.ImageCollection.denoise = denoise