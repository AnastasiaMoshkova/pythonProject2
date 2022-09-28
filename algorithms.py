from abc import ABC, abstractmethod
from sklearn.metrics import mean_squared_error
import pandas as pd

class TrainTestIntervalException(Exception):
    def __str__(self):
        return f"Длины массивов предсказанного и тестового набора данных не совпадают."

class Algorithm(ABC):

    name='ABC algorithm class'

    def __init__(self, predictions):
        self.predictions=predictions

    def fit(self):
        pass

    @abstractmethod
    def predict(self):
        pass

    def meanSquaredError(self,test):
        if (len(test)!=len(self.predictions)):
            raise TrainTestIntervalException()
        return mean_squared_error(test, self.predictions, squared=False)


class MovingAverage(Algorithm):
    name='Скользящее среднее'

    def __init__(self, train, horizont, nums):
        history = list(train)
        for i in range(horizont):
            history.append(pd.Series(history).rolling(nums).mean().iloc[-1])
        return history[-horizont,:]
