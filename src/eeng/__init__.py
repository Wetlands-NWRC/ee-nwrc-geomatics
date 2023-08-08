from .server.cfuncs import *

# bound functions to the ee.ImageCollection class
ee.ImageCollection.denoise = denoise
ee.ImageCollection.addCalculator = addCalculator
ee.ImageCollection.addDependent = addDependent
ee.ImageCollection.addConstant = addConstant
ee.ImageCollection.addTime = addTime
ee.ImageCollection.addHarmonics = addHarmonics

# bound functions to the ee.FeatureCollection class
ee.FeatureCollection.addXCordinate = add_x_coordinate
ee.FeatureCollection.addYCordinate = add_y_coordinate
ee.FeatureCollection.generateSamples = generate_samples