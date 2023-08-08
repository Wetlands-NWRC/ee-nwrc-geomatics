from .server.cfuncs import *

# bound functions to the ee.ImageCollection class
ee.ImageCollection.denoise = denoise
ee.ImageCollection.addCalculator = addCalculator
ee.ImageCollection.addDependent = addDependent
ee.ImageCollection.addConstant = addConstant
ee.ImageCollection.addTime = addTime
ee.ImageCollection.addHarmonics = addHarmonics
