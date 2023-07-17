import pandas as pd
from dataWrangler import EnsembleDataReaderStreamlit, RobustnessTestPctDiff
import numpy as np
import pytest

class TestClass:

    def test_pctDiff(self):
        
        # Test to check percent difference calcs against excel calcs
        # Pattern: 1986
        # Scale: 200
        # Forecast Date: 1986020112
        # Ture workbook: data\ExcelCalc_1986_200_1986020112.xlsx
        

        trueData = pd.read_excel(r'data\ExcelCalc_1986_200_1986020112.xlsx', usecols="CP:CV",skiprows=5)
        trueData = trueData[['X3WM_200','% difference.1']].dropna()
        trueData.columns = ['member','pctDiff']

        edr = EnsembleDataReaderStreamlit('1986',200)
        allData = edr.loadData()
        forecast = allData.loc[allData.forecastDate == '1986020112', :]

        rTest = RobustnessTestPctDiff(forecast, 1)
        rCalc = rTest.calculate()

        rCalc = rCalc.drop('FOLC1F', axis=1)
        rCalc = rCalc.reset_index(drop=True).stack()
        rCalc.index = rCalc.index.droplevel(0)
        rCalc = rCalc.reset_index()
        rCalc.columns = trueData.columns
        rCalc.member = rCalc.member.astype(float)

        assert np.allclose(rCalc.pctDiff, trueData.pctDiff, rtol=1e-3)





if __name__ == '__main__':
    tc = TestClass()
    tc.test_pctDiff()