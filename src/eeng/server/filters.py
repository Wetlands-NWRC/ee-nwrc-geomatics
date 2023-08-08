from abc import ABC, abstractmethod
import ee


class SpatialFilters(ABC):

    def __call__(self, image: ee.Image) -> ee.Image:
        return image.convolve(self.algo()).set('spatialFilter', 'Added')

    @abstractmethod
    def algo(self):
        raise NotImplementedError


class BoxCar(SpatialFilters):
    def __init__(self, radius: int = 2, units: str = "pixels", normalize: bool = True, magnitude: float = 1.0):
        self.radius = radius
        self.units = units
        self.normalize = normalize
        self.magnitude = magnitude

    def algo(self):
        return ee.Kernel.square(self.radius, self.units, self.normalize, self.magnitude)


class Gaussian(SpatialFilters):
    def __init__(self, radius: float = 1.0, units: str = "pixels", normalize: bool = True, magnitude: float = 1.0):
        self.radius = radius
        self.units = units
        self.normalize = normalize
        self.magnitude = magnitude

    def algo(self):
        return ee.Kernel.gaussian(self.radius, self.units, self.normalize, self.magnitude)


class PeronaMalik(SpatialFilters):
    def __init__(self, K: float = 3.5, iterations: int = 10, method: int = 2):
        self.K = K
        self.iterations = iterations
        self.method = method

    def algo(self, img: ee.Image):
        dxW = ee.Kernel.fixed(3, 3, [[0, 0, 0], [1, -1, 0], [0, 0, 0]])

        dxE = ee.Kernel.fixed(3, 3, [[0, 0, 0], [0, -1, 1], [0, 0, 0]])

        dyN = ee.Kernel.fixed(3, 3, [[0, 1, 0], [0, -1, 0], [0, 0, 0]])

        dyS = ee.Kernel.fixed(3, 3, [[0, 0, 0], [0, -1, 0], [0, 1, 0]])

        lamb = 0.2

        k1 = ee.Image(-1.0 / self.K)
        k2 = ee.Image(self.K).multiply(ee.Image(self.K))

        for _ in range(0, self.iterations):
            dI_W = img.convolve(dxW)
            dI_E = img.convolve(dxE)
            dI_N = img.convolve(dyN)
            dI_S = img.convolve(dyS)

            if self.method == 1:
                cW = dI_W.multiply(dI_W).multiply(k1).exp()
                cE = dI_E.multiply(dI_E).multiply(k1).exp()
                cN = dI_N.multiply(dI_N).multiply(k1).exp()
                cS = dI_S.multiply(dI_S).multiply(k1).exp()

                img = img.add(
                    ee.Image(lamb).multiply(
                        cN.multiply(dI_N)
                        .add(cS.multiply(dI_S))
                        .add(cE.multiply(dI_E))
                        .add(cW.multiply(dI_W))
                    )
                )

            else:
                cW = ee.Image(1.0).divide(
                    ee.Image(1.0).add(dI_W.multiply(dI_W).divide(k2))
                )
                cE = ee.Image(1.0).divide(
                    ee.Image(1.0).add(dI_E.multiply(dI_E).divide(k2))
                )
                cN = ee.Image(1.0).divide(
                    ee.Image(1.0).add(dI_N.multiply(dI_N).divide(k2))
                )
                cS = ee.Image(1.0).divide(
                    ee.Image(1.0).add(dI_S.multiply(dI_S).divide(k2))
                )

                img = img.add(
                    ee.Image(lamb).multiply(
                        cN.multiply(dI_N)
                        .add(cS.multiply(dI_S))
                        .add(cE.multiply(dI_E))
                        .add(cW.multiply(dI_W))
                    )
                )

        return img


def denoise(self, algorithm: SpatialFilters):
    if not issubclass(algorithm, SpatialFilters):
        raise TypeError("algorithm must be a subclass of DenoiseAlgorithm")
    return self.map(algorithm)