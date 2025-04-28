import pandas as pd
import altair as alt
alt.data_transformers.disable_max_rows()
import vl_convert
import os
from src.dataWrangler import EnsembleDataReaderStreamlit, RobustnessTestPctDiff

def prepareData(testObj: RobustnessTestPctDiff) -> pd.DataFrame:
    data = testObj.calculate()
    data = data.drop(testObj.reservoir_name, axis=1).stack()
    data.index.names = ['times','forecastDate', 'member']
    data.name = 'pctDiff'
    data = data.reset_index()
    data.loc[:, 'site'] = testObj.reservoir_name
    return data


def getIterationData():
    patternScales = {
    '1997': ['84','86','88','90','92','94','96','98','100','102','104','106','108','110','120','130'],
    '1986': ['100','102','104','106','108','110','112','114','116','118','120','130','140','150']
    }
    for pattern, scaleFactors in patternScales.items():

        for scaleFactor in scaleFactors:

            yield pattern, scaleFactor

data_directory =  os.path.join('data', 'nbbORO')


oroSite = 'ORDC1'
nbbSite = 'NBBC1'

memberNames = [str(i) for i in range(1980, 2021)]

nDay = 7

## Pattern 1997
## Scale 102
## NBBC1

sspResult = [['01-day', '01/02/1997',101005.0],
            ['03-day', '01/03/1997',62216.6],
            ['05-day', '01/04/1997',46271.9],
            ['07-day', '01/03/1997',36325.1],
            ['10-day', '01/05/1997',29118.3],
            ['15-day', '01/10/1997',20850.9]]

truthData = pd.DataFrame(sspResult, columns=['nDay', 'times', 'flow'])

mergeData = pd.DataFrame()
for pattern, scaleFactor in getIterationData():

    oroTest = RobustnessTestPctDiff(pattern, scaleFactor, oroSite, data_directory, nDay)

    nbbTest = RobustnessTestPctDiff(pattern, scaleFactor, nbbSite, data_directory, nDay)
    nbbData = nbbTest.data
    simHist = nbbData.loc[:, (nbbSite)]
    simHist.name = 'flow'
    simHist = simHist.groupby('times').first()
    simHist = simHist.dropna()

    output = pd.DataFrame(columns = ['reservoir','duration', 'Annual Maximum'] )
    for duration in [1,3,5,7]:
        annualMaximum = simHist.rolling(pd.Timedelta(days=duration)).mean().max()

        output = pd.concat(
            [
                output,
                pd.DataFrame(
                    data=[["NBBC1", f"{duration}-day", annualMaximum]],
                    columns=["reservoir", "duration", "Annual Maximum"],
                ),
            ]
        )
                  
    oroTest = RobustnessTestPctDiff(pattern, scaleFactor, oroSite, data_directory, nDay)
    oroData = oroTest.data
    simHist = oroData.loc[:, (oroSite)]
    simHist.name = 'flow'
    simHist = simHist.groupby('times').first()
    simHist = simHist.dropna()

    for duration in [1,3,5,7]:
        annualMaximum = simHist.rolling(pd.Timedelta(days=duration)).mean().max()

        output = pd.concat(
            [
                output,
                pd.DataFrame(
                    data=[["ORDC1", f"{duration}-day", annualMaximum]],
                    columns=["reservoir", "duration", "Annual Maximum"],
                ),
            ]
        )
    output.loc[:,'pattern'] = pattern
    output.loc[:,'scaleFactor'] = scaleFactor

    mergeData = pd.concat([mergeData, output])

mergeData.to_excel(rf'output\NBB-ORO\simulatedHistoricalAnnualMax.xlsx', index=False)