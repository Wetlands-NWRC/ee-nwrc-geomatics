from math import pi
import ee

from ..calc import NDVI


class HarmonicsCollection(ee.ImageCollection):
    def __init__(self, args, dependent = NDVI(), cycles: int = 3):
        super().__init__(args)
        self.indep = ['constant', 't']
        self.dep = dependent
        self.cycles = cycles

    def addDependent(self, calc):
        self.dep = calc.name
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

    def addHarmonics(self):
        sin = [f"cos_{i}" for i in range(1, self.cycles + 1)]
        cos = [f"sin_{i}" for i in range(1, self.cycles + 1)]

        def _addHarmonics(image: ee.Image):
            frequencies = ee.Image.constant(self.cycles)
            time = ee.Image(image).select("t")
            cosines = time.multiply(frequencies).cos().rename(cos)
            sines = time.multiply(frequencies).sin().rename(sin)
            return image.addBands(cosines).addBands(sines)

        return self.map(_addHarmonics)


class HarmonicModel:
    def __init__(self, col: HarmonicsCollection) -> None:
        self.col = col
        self._model = None
        self._coefficients = None

    @property
    def model(self) -> ee.ComputedObject:
        return self._model
    
    @property
    def coefficients(self) -> ee.Image:
        return self._coefficients

    def fit(self) -> None:
        """ Sets the trend property. Reduces the ImageCollection to an image by Linear Regression """
        self._model = self.col.select(self.col.indep.append(self.col.dep).reduce(
            ee.Reducer.linearRegression(len(self.col.ind), 1)
        ))
        return None
    
    def apply(self) -> None:
        if self._model is None:
            raise Exception("Fit must be run before you can apply the model")
        
        self._coefficients = (
            self.col.select('coefficients')
            .arrayProject([0])
            .arrayFlatten([self.col.indep], ['coeff'])
        )

        return None


class FourierTransform:
    def __init__(self, model: HarmonicModel) -> None:
        self.model = model

        # TODO add validators, need strict types

    def addCoefficients(self, coefficients: ee.Image) -> None:
        self.col = self.col.map(lambda image: image.addBands(coefficients))
        return self

    def addAmplitude(self, mode: int):
        def mk_amplitude(image):
            sin_coef = image.select(f"sin_{mode}_coeff")
            cos_coef = image.select(f"cos_{mode}_coeff")
            amp = sin_coef.atan2(cos_coef).rename(f"amp_{mode}")
            return image.addBands(amp)

        self.col = self.col.map(mk_amplitude)
        return self

    def addPhase(self, mode: int):
        def mk_phase(image):
            sin_coef = image.select(f"sin_{mode}")
            cos_coef = image.select(f"cos_{mode}")
            phase = sin_coef.atan2(cos_coef).rename(f"phase_{mode}")
            return image.addBands(phase)

        self.col = self.col.map(mk_phase)
        return self

    def build(self):
        # build steps

        coeff_col = self.addCoefficients(self.model.coefficients)

        # 1. add coeff to collection
        for cycle in list(range(0, self.col.cycles)):
            coeff_col.addAmpliture(cycle)
            coeff_col.addPhase(cycle)
        
        self.col = coeff_col.median().unitScale(-1, 1)
        return self
