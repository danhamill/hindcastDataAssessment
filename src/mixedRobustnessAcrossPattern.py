from dataWrangler import MixedEnsembleDataReaderStreamlit, RobustnessTestPctDiff
from plots import getEnsembleChart
import pandas as pd
import altair as alt
import numpy as np
alt.data_transformers.disable_max_rows()
import os

'''
Goal is mix ensemble and determinstic data

ensemble data will be from a larger scale factor
deterministic data will from a smaller scale factor
'''


def main():
    
    for nday in [1,3]:
        outDir = rf'output\mixedScaleFactorHeatmapsSorted\{nday}_day'
        os.makedirs(outDir, exist_ok=True)
        for pattern in ['1986', '1997']:
            for determinsticScaleFactor in list(range(200,550,50)):
                if determinsticScaleFactor < 450:
                    for mixedScaleFactor in list(range(determinsticScaleFactor+10, 510, 10)):   
                    
                        compiledMemberTable = pd.DataFrame()
                        compiledPctDiffTable = pd.DataFrame()
                        scaleData = MixedEnsembleDataReaderStreamlit(pattern, determinsticScaleFactor, mixedScaleFactor).loadData()
                        
                        # for forecastDate in scaleData.forecastDate.unique():
                        #     c = getEnsembleChart(scaleData, forecastDate = forecastDate, ensembleColor='blue')
                        #     c = c.properties(title=forecastDate, width=750)
                        #     c.save(rf'output\mixedScaleFactorEnsemblePlots\pattern_{pattern}_detScale_{determinsticScaleFactor}_ensembleScale_{mixedScaleFactor}_forecastDate_{forecastDate}.png', scale_factor=1)
                        
                        
                        rt  = RobustnessTestPctDiff(scaleData, nday)
                        pctDiff = rt.calculate()
                        pctDiff = pctDiff.drop('FOLC1F', axis=1)

                        tmp = pctDiff.reset_index().drop('forecastDate', axis=1).set_index('times')

                        tmp = pd.DataFrame(index = tmp.index, columns = tmp.columns, data =np.sort(tmp.values, axis=1)).stack()

                        tmp.index.names = ['forecastDate','member']
                        tmp.name = 'pctDif'
                        tmp = tmp.reset_index()

                        c = alt.Chart(tmp, width = 1500, height=750).mark_rect().encode(
                            x = alt.X('member:O'),
                            y = alt.Y('yearmonthdate(forecastDate):O').axis(format = '%d %b %Y'),
                            color = alt.Color('pctDif').scale(scheme = 'redblue', domainMax=2, domainMin=-2)
                        )

                        text = c.mark_text(baseline='middle').encode(
                            alt.Text('pctDif', format = '.0%'),
                            color = alt.condition(
                                abs(alt.datum.pctDif) > 0,
                                alt.value('black'),
                                alt.value('white')
                            )
                        )

                        merge = (c + text).properties(title =f"Determinstic AEP: {determinsticScaleFactor} -- Ensemble AEP: {mixedScaleFactor}" )
                        merge.save(rf'{outDir}\pattern_{pattern}_detScale_{determinsticScaleFactor}_ensembleScale_{mixedScaleFactor}.png', scale_factor=1)







if __name__ == '__main__':

    main()