# from pydsstools.heclib.dss import HecDss
import pandas as pd
import numpy as np
import os


def getIssueDates(pattern):
    return {
        '1986': [
            '1986020112',
            '1986020212',
            '1986020312',
            '1986020412',
            '1986020512',
            '1986020612',
            '1986020712',
            '1986020812',
            '1986020912',
            '1986021012',
            '1986021112',
            '1986021212',
            '1986021312',
            '1986021412',
            '1986021512',
            '1986021612',
            '1986021712',
            '1986021812',
            '1986021912',
            '1986022012',
            '1986022112',
            '1986022212',
            '1986022312',
            '1986022412',
            '1986022512',
            '1986022612',
            '1986022712',
            '1986022812'
        ],
        '1997': [
            '1996121512',
            '1996121612',
            '1996121712',
            '1996121812',
            '1996121912',
            '1996122012',
            '1996122112',
            '1996122212',
            '1996122312',
            '1996122412',
            '1996122512',
            '1996122612',
            '1996122712',
            '1996122812',
            '1996122912',
            '1996123012',
            '1996123112',
            '1997010112',
            '1997010212',
            '1997010312',
            '1997010412',
            '1997010512',
            '1997010612',
            '1997010712',
            '1997010812',
            '1997010912',
            '1997011012',
            '1997011112',
            '1997011212',
            '1997011312',
            '1997011412',
            '1997011512'
        ]
    }[pattern]

class EnsembleDataReaderStreamlit(object):

    def __init__(self, pattern: str, scaleFactor: int ) -> None:
        # dataDirs = {
        # '1986': r'C:\workspace\git_clones\folsom-hindcast-processing\outputNormalDate4\1986_results.dss',
        # '1997': r'C:\workspace\git_clones\folsom-hindcast-processing\outputNormalDate4\1997_results.dss',
        # }
        self.scaleFactor = scaleFactor
        self.pattern = pattern
        self.featherFile = rf'data/{self.pattern}_{self.scaleFactor}.feather'

    def loadData(self) -> pd.DataFrame:
        df = pd.read_feather(self.featherFile)
        return df



class RobustnessTestPctDiff(object):

    def __init__(self, allData: pd.DataFrame, exceedProb: int, nDays: int) -> None:
        self.data = allData.set_index(['forecastDate','times'])
        self.nDay = nDays
        self.exceedProb = exceedProb

    def calculate(self) -> pd.DataFrame:
        output = pd.DataFrame()

        for forecastDate, group in self.data.groupby('forecastDate'):
            group.index = group.index.droplevel('forecastDate')
            if not group.index.get_level_values('times').is_monotonic_increasing:
                group = group.sort_index()
            # Accumulate Volume (cfs)
            group = group.astype(float).cumsum(axis=0)

            # Select nDay Volume
            nDayTimeStamp = group.index.min()+ pd.DateOffset(days=int(self.nDay))

            # Calculate pct difference
            subGroup = group.loc[group.index == nDayTimeStamp, :]
            trueValue = subGroup.iloc[0]['FOLC1F']
            subGroup = (subGroup - trueValue)/trueValue
            subGroup = pd.concat([subGroup], keys=[forecastDate], names =['forecastDate'])

            output = pd.concat([output, subGroup])



        return output
    
    def pctDiffStats(self, data:pd.DataFrame) -> pd.DataFrame:
        data= data.drop('FOLC1F', axis=1).stack()
        data.index.names = ['forecastDate','times', 'member']
        data.name = 'pctDiff'
        data = data.reset_index()
        summary = data.groupby('forecastDate').pctDiff.describe().drop('count', axis=1).applymap("{0:.3%}".format)
        summary.index.name = 'forecastDate'
        return summary
        
# class EnsembleDataReader(object):
    
#     def __init__(self, pattern: str, scaleFactor: int ) -> None:
#         # dataDirs = {
#         # '1986': r'C:\workspace\git_clones\folsom-hindcast-processing\outputNormalDate4\1986_results.dss',
#         # '1997': r'C:\workspace\git_clones\folsom-hindcast-processing\outputNormalDate4\1997_results.dss',
#         # }
#         self.scaleFactor = scaleFactor
#         self.pattern = pattern
#         self.dssFile = rf'data\input\{self.pattern}_{self.scaleFactor}.dss'

#     def getSingleScaleFactorDssPaths(self) -> dict:

#         output = {}
#         for fPartPattern in getIssueDates(self.pattern):

#             singleForecastDssPaths = self.getSingleForecastDssPaths(fPartPattern)
#             output.update({fPartPattern:singleForecastDssPaths})

#         return output

        

#     def getSingleForecastDssPaths(self, fPartPattern) -> list:

        
#         with HecDss.Open(self.dssFile) as fid:
            
#             plist = fid.getPathnameList(f'/{self.scaleFactor}/FOLC1F/FLOW-NAT/*/*/*|{fPartPattern}/')

#         output = []
#         for i in plist:
#             parts = i.split('/')
#             if parts not in output:
#                 output.append(parts) 

#         res = pd.DataFrame(data = output, columns = ['start','PartA','PartB','PartC','PartD', 'PartE','PartF','end'])

#         output = {}
#         for scaling, group in res.groupby('PartA'):

#             group = group.apply(
#                 lambda row: "/".join(["", row.PartA, row.PartB, row.PartC, row.PartD, row.PartE, row.PartF, ""]),
#                 axis=1,
#             ).to_list()

#             output.update({scaling:group})


#         return output[f'{self.scaleFactor}']
    
#     def getDeterminsticDSSPaths(self) -> list:
#         with HecDss.Open(self.dssFile) as fid:

#             plist = fid.getPathnameList(f'/*/FOLC1F/FLOW-NAT/*/*//')

#         output = []
#         for i in plist:
#             parts = i.split('/')
#             if parts not in output:
#                 output.append(parts) 

#         res = pd.DataFrame(data = output, columns = ['start','PartA','PartB','PartC','PartD', 'PartE','PartF','end'])

#         output = {}
#         for scaling, group in res.groupby('PartA'):

#             group = group.apply(
#                 lambda row: "/".join(["", row.PartA, row.PartB, row.PartC, row.PartD, row.PartE, row.PartF, ""]),
#                 axis=1,
#             ).to_list()

#             output.update({scaling:group})


#         return output[f'{self.scaleFactor}']

#     def getEnsembleData(self, pathsToRead: list) -> pd.DataFrame:
#         output = pd.DataFrame(columns = ['times'] +list(range(1980, 2021)))


#         # Read in Ensemble data from DSS Collection
#         for member in range(1980,2021):
            
#             if output.times.empty:
#                 doTimes = True
#             else:
#                 doTimes = False

#             subPathNames = [i for i in pathsToRead if f'C:00{member}|' in i.split('/')[-2]]
            
#             # Single Block
#             if len(subPathNames) == 1:

#                 with HecDss.Open(self.dssFile) as fid:
#                     ts = fid.read_ts(subPathNames[0])
#                     values = ts.values
                    
#                 if doTimes:
#                     times = ts.pytimes
#                     times = [i.strftime('%Y-%m-%d %H:%M:%S') for i in times]
#                     output.loc[:,'times'] = times     
#                 output.loc[:,member] = values.copy()
#             else:
#                 outputValues = []
#                 with HecDss.Open(self.dssFile) as fid:
#                     ts = fid.read_ts(subPathNames[0])
#                     values = ts.values
#                     if doTimes: 
#                         timesFirstBlock = ts.pytimes
#                     valuesFirstBlock = values.copy()
#                 del values
#                 with HecDss.Open(self.dssFile) as fid:
#                     ts = fid.read_ts(subPathNames[1])
#                     values = ts.values
#                     if doTimes:
#                         timesSecondBlock = ts.pytimes
#                     valuesSecondBlock = values.copy()
#                 mergeValues = np.append(valuesFirstBlock, valuesSecondBlock)


#                 if doTimes:
#                     mergeTimes = timesFirstBlock+timesSecondBlock
#                     mergeTimes = [i.strftime('%Y-%m-%d %H:%M:%S') for i in mergeTimes]
#                     output.loc[:,'times'] = mergeTimes
#                 output.loc[:,member] = mergeValues.copy()
#         return output


#     def getDeterministicData(self, pathsToRead: list) -> pd.DataFrame:
#         output = pd.DataFrame(columns = ['times','FOLC1F'])

#         doTimes=True
#         # Single Block
#         if len(pathsToRead) == 1:

#             with HecDss.Open(self.dssFile) as fid:
#                 ts = fid.read_ts(pathsToRead[0])
#                 values = ts.values
                
#             if doTimes:
#                 times = ts.pytimes
#                 times = [i.strftime('%Y-%m-%d %H:%M:%S') for i in times]
#                 output.loc[:,'times'] = times     
#             output.loc[:,'FOLC1F'] = values.copy()
#         else:
#             outputValues = []
#             with HecDss.Open(self.dssFile) as fid:
#                 ts = fid.read_ts(pathsToRead[0])
#                 values = ts.values
#                 if doTimes: 
#                     timesFirstBlock = ts.pytimes
#                 valuesFirstBlock = values.copy()
#             del values
#             with HecDss.Open(self.dssFile) as fid:
#                 ts = fid.read_ts(pathsToRead[1])
#                 values = ts.values
#                 if doTimes:
#                     timesSecondBlock = ts.pytimes
#                 valuesSecondBlock = values.copy()
#             mergeValues = np.append(valuesFirstBlock, valuesSecondBlock)

#             if doTimes:
#                 mergeTimes = timesFirstBlock+timesSecondBlock

#                 mergeTimes = [i.strftime('%Y-%m-%d %H:%M:%S') for i in mergeTimes]
#                 output.loc[:,'times'] = mergeTimes
#             output.loc[:,'FOLC1F'] = mergeValues.copy()
#         return output

#     def compileData(self, selected_ensemble_pathnames: list, 
#                     selected_determinstic_pathnames: list,
#                     deterministicData: pd.DataFrame=None) -> pd.DataFrame:
#         forecastData = self.getEnsembleData(selected_ensemble_pathnames)
#         if deterministicData is None:
#             deterministicData = self.getDeterministicData(selected_determinstic_pathnames)
#         forecastData.loc[:,'times'] = pd.to_datetime(forecastData.loc[:,'times'])
#         deterministicData.loc[:,'times'] = pd.to_datetime(deterministicData.loc[:,'times'])
#         mergeData = pd.DataFrame(index = pd.DatetimeIndex(forecastData.times, name='times')).sort_index()
#         mergeData = mergeData.merge(deterministicData.set_index('times'), left_index=True, right_index=True, how='left' )
#         mergeData = mergeData.fillna(method='ffill')
#         mergeData = mergeData.merge(forecastData.set_index('times'), left_index=True, right_index=True, how='left')
#         mergeData = mergeData.applymap("{0:.0f}".format)
#         return mergeData

#     def compileAllData(self, allPathsToRead: dict) -> pd.DataFrame:
#         selected_determinstic_pathnames = self.getDeterminsticDSSPaths()
#         deterministicData = self.getDeterministicData(selected_determinstic_pathnames)
#         output = pd.DataFrame()
#         for forecastDate, pathsToRead in allPathsToRead.items():

#             mergeData = self.compileData(pathsToRead, selected_determinstic_pathnames, deterministicData)
#             mergeData = pd.concat([mergeData], keys=[forecastDate], names =['forecastDate'])
#             assert mergeData.index.get_level_values('times').is_monotonic_increasing, 'times are not monotonic'
#             output = pd.concat([output, mergeData])
#             del mergeData
#         return output.fillna(method='ffill')