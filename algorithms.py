from abc import ABC, abstractmethod
from sklearn.metrics import mean_squared_error
import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
from statsmodels.tsa.arima_model import ARIMA
import warnings
warnings.filterwarnings("ignore")#, category=FutureWarning)

class TrainTestIntervalException(Exception):
    def __str__(self):
        return f"Длины массивов предсказанного и тестового набора данных не совпадают."

class MovingAverageException(Exception):
    def __str__(self):
        return f"Окно расчета скользящего среднего должно быть меньше длины обучающей выборки."

class Algorithm(ABC):

    name='ABC algorithm class'

    def __init__(self,train):
        self.predictions=[]
        self.train=train

    def fit(self):
        pass

    @abstractmethod
    def predict(self):
        pass

    def meanSquaredError(self,test):
        if (len(test)!=len(self.predictions)):
            raise TrainTestIntervalException()
        return mean_squared_error(test, self.predictions, squared=False)

    def accuracy(self,test):
        acc = []
        for i in range(len(self.predictions)):
            k = test[i]
            if test[i] == 0:
                k = 0.001
            acc.append(abs(self.predictions[i] - test[i]) / k)
        return round((1 - sum(acc) / 3) * 100, 1)


class MovingAverage(Algorithm):
    name='Скользящее среднее'
    parameters=[2,3]

    def __init__(self, train):
        super().__init__(train)
        self.history = train[:]


    def predict(self,horizont, nums):
        if nums>=len(self.history):
            raise MovingAverageException()
        else:
            self.nums=nums
        for i in range(horizont):
            self.history.append(pd.Series(self.history).rolling(self.nums).mean().iloc[-1])
        self.predictions=self.history[-horizont:]
        return self.predictions


class SimpleExponentialSmothing(Algorithm):
    name='Простое экспоненциальное сглаживание'
    parameters = {'level': [2]}

    def __init__(self,train):
        super().__init__(train)
        #self.train=train

    def fit(self, level):
        self.fit = SimpleExpSmoothing(self.train).fit(smoothing_level=level, optimized=False)

    def predict(self,horizont):
        self.predictions = self.fit.predict(start=len(self.train), end=len(self.train) + horizont - 1)
        return self.predictions

class HoltMethod(Algorithm):
    name = 'Метод Холта'
    parameters={'level':[0.1,0.2,0.3,0.4,0.5],'smoothing_trend':[0.1,0.2,0.3,0.4,0.5]}

    def __init__(self,train):
        super().__init__(train)
        #self.train = train

    def fit(self, level, smoothing_slope):
        self.model = Holt(self.train).fit(smoothing_level=level, smoothing_slope=smoothing_slope)

    def predict(self, horizont):
        self.predictions = self.model.predict(start=len(self.train), end=len(self.train) + horizont - 1)
        return self.predictions


class ExponentialSmothing(Algorithm):
    name = 'Экспоненциальное сглаживание'
    parameters = {'periods': [1, 2, 3, 4], 'trend': ['add']}

    def __init__(self,train):
        super().__init__(train)
        #self.train = train

    def fit(self, periods, trend='add'):
        self.model = ExponentialSmoothing(self.train, seasonal_periods=periods, trend=trend).fit()

    def predict(self, horizont):
        self.predictions = self.model.predict(start=len(self.train), end=len(self.train) + horizont - 1)
        return self.predictions

class ARIMAMethod(Algorithm):
    name = 'ARIMA'
    parameters = {'ord1': [0, 1, 2], 'ord2': [0, 1, 2], 'ord3':[0, 1, 2]}

    def __init__(self,train):
        super().__init__(train)
        #self.train = train

    def fit(self, ord1, ord2, ord3):
        self.model = ARIMA(self.train, order=(ord1, ord2, ord3)).fit()

    def predict(self, horizont):
        self.predictions = self.model.predict(start=len(self.train), end=len(self.train) + horizont - 1)
        return self.predictions




a=HoltMethod([1,2,3,4,5])
print(a.predictions)
a.fit(0.1,0.1)
a.predict(2)
print(a.predictions)
print(a.meanSquaredError([1,2]))



'''
a=MovingAverage([1,2,3,4,5],2,2)
print(a.predictions)
a.predict()
print(a.predictions)
print(a.meanSquaredError([1,2]))
'''