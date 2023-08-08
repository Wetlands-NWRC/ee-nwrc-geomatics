from .server.cfuncs import *

# bound functions to the ee.ImageCollection class
ee.ImageCollection.denoise = denoise
ee.ImageCollection.addCalculator = addCalculator
ee.ImageCollection.addDependent = addDependent
ee.ImageCollection.addConstant = addConstant
ee.ImageCollection.addTime = addTime
ee.ImageCollection.addHarmonics = addHarmonics
ee.ImageCollection.addCloudMask = add_cloud_mask
ee.ImageCollection.sentinel2SR = sentinel2SR
ee.ImageCollection.sentinel2TOA = sentinel2TOA
ee.ImageCollection.sentinel2CloudProbability = sentinel2CloudProbability
ee.ImageCollection.sentinel1DV = sentinel1DV
ee.ImageCollection.alos = alos
ee.ImageCollection.sentinel2Cloudless = sentinel2Cloudless

# bound functions to the ee.FeatureCollection class
ee.FeatureCollection.addXCordinate = add_x_coordinate
ee.FeatureCollection.addYCordinate = add_y_coordinate
ee.FeatureCollection.generateSamples = generate_samples
ee.FeatureCollection.getLookup = lookup