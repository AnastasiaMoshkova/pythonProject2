import matplotlib.pyplot as plt
import pandas as pd
import algorithms as al
import warnings
warnings.filterwarnings("ignore")#, category=FutureWarning)
import enum

NationalProjectsName=['NP',]
NationalProjectsIndexName=['index_name']
transformations=['box_cox']
algoritms={
    'Скользящее среднее':[2,3],
    'Метод Холта':[0.1,0.2,0.3,0.4,0.5],
    'Простое экспоненциальное сглаживание':[2,3,4,5],
    'Экспоненциальное сглаживание':[],
    'ARIMA': [0,1,2,3,4,5]
}

class EmissionFinder():
    '''
    здесь будет функция поиска выбросов
    '''
    def findEmission(self):
        return []


class MonthIntervalException(Exception):
    def __str__(self):
        return f"Длины массивов времнного инетрвала, фактических значений и плановых значений не совпадают."

class NameException(Exception):
    def __init__(self,name):
        self.name = name
    def __str__(self):
        return f"Не существующее наименование: {self.name}."

class Data():

    DataType='Показатель Национального Проекта'

    def __init__(self, nationalProject, index_name, monthInterval, fact, plan, emissions=[], recalculation=False):
        self.nationalProject=nationalProject
        self.index_name=index_name
        self.monthInterval=monthInterval
        self.fact=fact
        self.plan=plan
        self.emissions=emissions
        self.recalculation=recalculation

    @classmethod
    def dataLoaderFromJson(cls, json):
        '''Здесь будет парсер json'''
        nationalProject='NP'
        index_name='index_name'
        monthInterval=[1,2,3,4,5,6,7,8,9,10]
        fact=[1,2,3,4,5,6,7,8,9,10]
        plan=[1,2,3,4,5,6,7,8,9,10]
        emissions=[]
        recalculation=False
        cls.isDataValid(nationalProject, index_name, monthInterval, fact, plan)
        data = cls(nationalProject, index_name, monthInterval, fact, plan, emissions, recalculation)
        return data


    @staticmethod
    def isDataValid(nationalProject, index_name, monthInterval, fact, plan):
        if (len(monthInterval)!=len(fact)) or (len(plan)!=len(fact)):
            raise MonthIntervalException()
        if nationalProject not in NationalProjectsName:
            raise NameException(nationalProject)
        if index_name not in NationalProjectsIndexName:
            raise NameException(index_name)


    def dataVisualization(self):
        plt.rcParams["figure.figsize"] = (30, 3)
        plt.plot(self.monthInterval, self.fact)
        plt.plot(self.monthInterval, self.plan)
        plt.title(self.index_name)
        plt.show()

    def dataToDict(self):
        #return dict(zip(self.monthInterval,self.fact)),dict(zip(self.monthInterval,self.plan))
        return {
            'month':self.monthInterval,
            'fact': self.fact,
            'plan':self.plan,
            'recalculation':self.recalculation
        }





class DataTransformer(EmissionFinder):
    def __init__():
        pass

    def recalculationToAccumulative(self):
        pass
        '''
        здесь буедт функция персчета данных в накопительный итог
        '''
    def recalculationToInitial(self):
        pass
        '''
        здесь будет функция персчета данных из накопительного итога в исходный
        '''
    def emissionReplaser(self):
        self.emissions=super().findEmission()
        '''
        здесь буедт функция замены выбросов интерполированные данные (возможны вариации по замене пропусков)
        '''

    def intervalFinderForBoxcoxTransformation(self):
        pass
        '''
        здесь буедт функция для выбора интервала для box_cox преобразоания (без нулей) или 
        ошибка в случае отрицательного интервала
        '''

    def boxcoxTransformation(self):
        pass
        '''
        здесь буедт функция для box_cox преобразоания
        '''

    def boxcoxRetransformation(self):
        pass
        '''
        здесь буедт функция для обратного box_cox преобразоания
        '''


class TimeSeriesForecast():
    def __init__(self,fact):
        self.fact=fact
        self.algorithmInfo= []


    def TestTrainSplit(self,persent):
        self.train=self.fact[:len(self.fact)-round(persent/100*len(self.fact))]
        self.test=self.fact[len(self.fact)-round(persent/100*len(self.fact)):]
        print(self.train,self.test)



    def chooseBestAlgorithm(self):
        self.ma = al.MovingAverage(self.train)
        self.holt = al.HoltMethod(self.train)
        self.es = al.ExponentialSmothing(self.train)
        self.ses = al.SimpleExponentialSmothing(self.train)
        self.arima=al.ARIMAMethod(self.train)

        horizont=len(self.test)
        '''
        потом оптимизировать
        '''
        for nums in self.ma.parameters:
            try:
                self.algorithmInfo.append(
                    {
                        'algorithm':self.ma.name,
                        'prediction':self.ma.predict(horizont,nums),
                        'parameters':{'nums':nums},
                        'accuracy':{},
                        'error':self.ma.meanSquaredError(self.test)
                    })
            except Exception:
                continue

        for level in self.holt.parameters['level']:
            for smoothing_slope in self.holt.parameters['smoothing_trend']:
                try:
                    self.holt.fit(level,smoothing_slope)
                    self.algorithmInfo.append(
                        {
                            'algorithm':self.holt.name,
                            'prediction':self.holt.predict(horizont),
                            'parameters': {'level':level, 'smoothing_trend':smoothing_slope},
                            'accuracy': {},
                            'error':self.holt.meanSquaredError(self.test)
                        })
                except Exception:
                    continue

        for periods in self.es.parameters['periods']:
            for trend in self.es.parameters['trend']:
                try:
                    self.es.fit(periods,trend)
                    self.algorithmInfo.append(
                        {
                            'algorithm':self.es.name,
                            'prediction':self.es.predict(horizont),
                            'parameters': {'periods':periods, 'trend':trend},
                            'accuracy': self.accuracy(self.test),
                            'error':self.es.meanSquaredError(self.test)
                        })
                except Exception:
                    continue

        for level in self.ses.parameters['level']:
            try:
                self.ses.fit(level)
                self.algorithmInfo.append(
                    {
                        'algorithm':self.ses.name,
                        'prediction':self.ses.predict(horizont),
                        'parameters': {'level':level},
                        'accuracy': self.accuracy(self.test),
                        'error':self.ses.meanSquaredError(self.test)
                    })
            except Exception:
                continue

        for ord1 in self.arima.parameters['ord1']:
            for ord2 in  self.arima.parameters['ord2']:
                for ord3 in self.arima.parameters['ord3']:
                    try:
                        self.arima.fit(ord1,ord2,ord3)
                        self.algorithmInfo.append(
                            {
                                'algorithm':self.arima.name,
                                'prediction':self.arima.predict(horizont),
                                'parameters': {'ord1':ord1,'ord2':ord2, 'ord3':ord3 },
                                'accuracy': self.accuracy(self.test),
                                'error':self.arima.meanSquaredError(self.test)
                            })
                    except Exception:
                        continue
        return sorted(self.algorithmInfo, key=lambda d: d['error'])[0]



d=Data.dataLoaderFromJson('NP')
#d=Data('NP', 'index_name', [1,2,3,4], [1,2,3,4], [1,2,3], emissions=[], recalculation=False)
#d.dataVisualization()
print(d.dataToDict()['fact'])
t= TimeSeriesForecast(d.dataToDict()['fact'])
t.TestTrainSplit(20)
print(t.chooseBestAlgorithm())
print(t.algorithmInfo)

