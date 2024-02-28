import pandas as pd
from dataWrangler import EnsembleDataReaderStreamlit, RobustnessTestPctDiff
import numpy as np
import pytest
import os

class TestClass:

    def test_pctDiff(self):
        
        # Test to check percent difference calcs against excel calcs
        # Pattern: 1986
        # Scale: 200
        # Forecast Date: 1986020112
        # Ture workbook: data\ExcelCalc_1986_200_1986020112.xlsx
        
        testDate = '1986020112'
        trueData = pd.read_excel(r'data\ExcelCalc_1986_200_1986020112.xlsx', usecols="CP:CV",skiprows=5)
        trueData = trueData[['X3WM_200','% difference.1']].dropna()
        trueData.columns = ['member','pctDiff']

        ndays = 1
        selected_reservoir = 'FOLC1F'
        selected_pattern = '1986'
        selected_scaleFactor = 200
        data_directory = os.path.join('data','Folsom')

        testObj = RobustnessTestPctDiff(
            selected_pattern=selected_pattern,
            reservoir_name=selected_reservoir,
            selected_scaleFactor=selected_scaleFactor,
            data_directory=data_directory,
            nDays=ndays
        )

        rCalc = testObj.calculate()
        rCalc = rCalc.drop(selected_reservoir, axis=1)
        rCalc = rCalc.iloc[0:1].reset_index(drop=True).stack()
        rCalc.index = rCalc.index.droplevel(0)
        rCalc = rCalc.reset_index()
        rCalc.columns = trueData.columns
        rCalc.member = rCalc.member.astype(float)

        assert np.allclose(rCalc.pctDiff, trueData.pctDiff, rtol=1e-3)





if __name__ == '__main__':
    tc = TestClass()
    tc.test_pctDiff()