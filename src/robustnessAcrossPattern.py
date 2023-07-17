from dataWrangler import EnsembleDataReaderStreamlit, RobustnessTestPctDiff
import pandas as pd



def main():
    
    excelWriter = pd.ExcelWriter(r'output\pctDiffTestResultsAll_v2.xlsx')

    for sf in list(range(200,510,10)):

        for pattern in ['1986', '1997']:
            compiledMemberTable = pd.DataFrame()
            compiledPctDiffTable = pd.DataFrame()
            scaleData = EnsembleDataReaderStreamlit(pattern, sf).loadData()
            rt  = RobustnessTestPctDiff(scaleData, 1)
            pctDiff = rt.calculate()
            pctDiff = pctDiff.drop('FOLC1F', axis=1)

            for exceedProb in [5,10,25,50,75,90,95,99]:     
                
                
                memberTable, pctDiffTable = rt.pctDiffNEP(pctDiff, exceedProb)
                compiledMemberTable = pd.concat([compiledMemberTable, memberTable],axis=1)
                compiledPctDiffTable = pd.concat([compiledPctDiffTable, pctDiffTable], axis=1)

            statSummary = rt.pctDiffStats(pctDiff)
            compiledMemberTable.to_excel(excelWriter, sheet_name = f'{pattern}_{sf}',startcol=0)
            compiledPctDiffTable.to_excel(excelWriter, sheet_name = f'{pattern}_{sf}',startcol=10)
            statSummary.to_excel(excelWriter, sheet_name = f'{pattern}_{sf}',startcol=21, startrow=1)
            pctDiff.to_excel(excelWriter, sheet_name = f'{pattern}_{sf}',startcol=31, startrow=1)


    excelWriter.close()
    print('here')


if __name__ == '__main__':

    main()