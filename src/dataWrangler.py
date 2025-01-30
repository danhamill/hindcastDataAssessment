from __future__ import annotations
import pandas as pd
import numpy as np
import os


def getIssueDates(pattern, project):
    if project == 'FOLSOM':
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
    else:
        return {
            '1986':[
                '1986012612',
                 '1986012712',
                 '1986012812',
                 '1986012912',
                 '1986013012',
                 '1986013112',
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
                 '1986022812',
                 '1986030112'
                 ],
            '1997': [
                '1996120812',
                '1996120912',
                '1996121012',
                '1996121112',
                '1996121212',
                '1996121312',
                '1996121412',
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

    def __init__(self, pattern: str, scaleFactor: int, reservoir_name: str, data_directory: str ) -> None:
        # dataDirs = {
        # '1986': r'C:\workspace\git_clones\folsom-hindcast-processing\outputNormalDate4\1986_results.dss',
        # '1997': r'C:\workspace\git_clones\folsom-hindcast-processing\outputNormalDate4\1997_results.dss',
        # }
        self.scaleFactor = scaleFactor
        self.pattern = pattern
        self.data_directory = data_directory
        self.reservoir_name = reservoir_name
        if self.reservoir_name == 'FOLC1F':
            self.featherFile = os.path.join(self.data_directory,f'{self.pattern}_{self.scaleFactor}.feather')
        else:
            self.featherFile = os.path.join(self.data_directory,f'{self.pattern}_{self.reservoir_name}_{self.scaleFactor}.feather')

    def loadData(self) -> pd.DataFrame:
        df = pd.read_feather(self.featherFile)
        df = df.rename(columns = {'date':'times','fileDate':'forecastDate'})
        df[df.columns[2:]]= df.loc[:,df.columns[2:]].astype(float)
        return df

class MixedEnsembleDataReaderStreamlit(object):

    def __init__(self, pattern: str, truthScaleFactor: int, mixedScaleFactor: int ) -> None:

        self.truthScaleFactor = truthScaleFactor
        self.mixedScaleFactor = mixedScaleFactor
        self.pattern = pattern
        self.truthFeatherFile = os.path.join('data',f'{self.pattern}_{self.truthScaleFactor}.feather')
        self.mixedFeatherFile = os.path.join('data',f'{self.pattern}_{self.mixedScaleFactor}.feather')

    def loadData(self) -> pd.DataFrame:
        trueDf= pd.read_feather(self.truthFeatherFile)
        trueDf[trueDf.columns[2:]]= trueDf.loc[:,trueDf.columns[2:]].astype(float)

        mixedDf= pd.read_feather(self.mixedFeatherFile)
        mixedDf[mixedDf.columns[2:]]= mixedDf.loc[:,mixedDf.columns[2:]].astype(float)

        result = pd.concat([trueDf[trueDf.columns[:3]], mixedDf[mixedDf.columns[3:]]], axis=1)
        return result


class RobustnessTestPctDiff(object):

    # def __init__(self, allData: pd.DataFrame, nDays: int, reservoir_name: str,
    #              pattern: str, scaleFactor: str | int) -> None:
    #     self.data = allData.set_index(['forecastDate','times'])
    #     self.nDay = nDays
    #     self.reservoir_name = reservoir_name     
    #     self.pattern = pattern
    #     self.scaleFactor = scaleFactor

    def __init__(self, selected_pattern: str,  selected_scaleFactor:str, reservoir_name: str, data_directory:str, nDays: str | int):
        self.nDay = nDays
        self.pattern = selected_pattern
        self.reservoir_name = reservoir_name
        self.dataDir = data_directory
        self.scaleFactor = selected_scaleFactor
        
        self.dataReader = EnsembleDataReaderStreamlit(
            self.pattern, 
            self.scaleFactor, 
            self.reservoir_name, 
            self.dataDir)

        self.data = self.dataReader.loadData().set_index(['forecastDate','times'])
        self.sourceFile = self.dataReader.featherFile

    def calculate(self) -> pd.DataFrame:
        output = pd.DataFrame()

        for forecastDate, group in self.data.groupby('forecastDate'):
            group.index = group.index.droplevel('forecastDate')
            if not group.index.get_level_values('times').is_monotonic_increasing:
                group = group.sort_index()
            # Accumulate Volume (cfs)
            group = group.astype(float).cumsum(axis=0)

            # Select nDay Volume
            nDayTimeStamp = group.index.min()+ pd.DateOffset(hours=int(self.nDay)*24-1)

            # Calculate pct difference
            subGroup = group.loc[group.index == nDayTimeStamp, :]
            trueValue = subGroup.iloc[0][self.reservoir_name]
            subGroup = (subGroup - trueValue)/trueValue
            subGroup = pd.concat([subGroup], keys=[forecastDate], names =['forecastDate'])

            output = pd.concat([output, subGroup])

        return output
    
    def pctDiffStats(self, data:pd.DataFrame) -> pd.DataFrame:
        if self.reservoir_name in data.columns:
            data= data.drop(self.reservoir_name, axis=1)
        data = data.stack()
        data.index.names = ['forecastDate','times', 'member']
        data.name = 'pctDiff'
        
        data = data.reset_index()
        
        summary = data.groupby('forecastDate').pctDiff.describe().drop('count', axis=1).applymap("{0:.3%}".format)
        summary.index.name = 'forecastDate'
        return summary
    
    def pctDiffNEP(self, data: pd.DataFrame, exceedProb: int) -> pd.DataFrame:
        output = pd.DataFrame()
        if self.reservoir_name in data.columns:
            data= data.drop(self.reservoir_name, axis=1)
                    
        for forecastDate, group in data.groupby('forecastDate'):
            dist = group.stack()
            idxQuantile = (dist.sort_values()[::-1] <= dist.quantile(exceedProb/100)).idxmax()
            valueQuantile = dist[idxQuantile]
            outIdx = (idxQuantile[0], exceedProb, idxQuantile[-1])
            tmp = pd.DataFrame(
                index = pd.MultiIndex.from_product(
                    [[outIdx[0]],[outIdx[1]],[outIdx[2]]], 
                    names = ['forecastDate','exceedProb','member']
                ), 
                data = {'pctDiff':[valueQuantile]}
            )
            output = pd.concat([output, tmp])

        memberTable = output.reset_index()[['forecastDate','exceedProb','member']].set_index(['forecastDate','exceedProb']).unstack('exceedProb')
        pctDiffTable = output.reset_index()[['forecastDate','exceedProb','pctDiff']].set_index(['forecastDate','exceedProb']).unstack('exceedProb')
        return memberTable, pctDiffTable
        
