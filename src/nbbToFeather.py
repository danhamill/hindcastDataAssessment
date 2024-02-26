import pandas as pd
from glob import glob
import numpy as np

import gc

def main():

    sites = {
        'ORDC1':'Flow',
        'NBBC1':'Flow'
    }
    
    ensembleStartYear = 1980
    dataDir = r'data\nbbORO\csv'

    for pattern in ['1986','1997']:

        patternDir = fr'{dataDir}\{pattern}'

        scalings = glob(rf'{patternDir}\*')

        for scaling in scalings:
            
            hindcastFiles = glob(rf'{scaling}\*hefs*.csv')

            scaleFactor = scaling.split('\\')[-1].split('_')[1].replace('sf','')

            simHistFile = glob(rf'{dataDir}\{pattern}*{scaleFactor}.csv')[0]

            assert len(simHistFile)>0, 'missing simulated historcal file'

            trueDf = pd.read_csv(simHistFile, header = [0])
            trueDf = trueDf.drop(index=0, axis=1)

            trueDf = trueDf.set_index('GMT')
            trueDf.index = pd.DatetimeIndex(trueDf.index)
            trueDf.index.name = ''
            trueDf.index = trueDf.index.tz_localize('UTC').tz_convert('US/Pacific')
            trueDf.index = pd.DatetimeIndex(
                [i.replace(tzinfo=None) for i in trueDf.index], 
                name='date'
            )
            trueDf = trueDf[list(sites.keys())]
            trueDf = trueDf.astype(float)*1000

            print('Currently Processing hefs files...')

            nbbMerge = pd.DataFrame()
            oroMerge = pd.DataFrame()

            for hindcastFile in hindcastFiles:
                
                fileDate = hindcastFile.split('\\')[-1].split('_')[0]
                
                csvSites  = pd.read_csv(
                    hindcastFile, 
                    header = None, 
                    nrows=1
                ).iloc[:,1:].stack().to_list()

                csvVariables = pd.read_csv(
                    hindcastFile, 
                    header = None, 
                    nrows=1, 
                    skiprows=1
                ).iloc[:,1:].stack().to_list()
                

                numEnsembles = pd.DataFrame(
                    data = {'sites':csvSites,'tsType':csvVariables}
                ).value_counts()
                
                ensembleYears = []
                for i in numEnsembles.index:
                    ensembleYears.extend(
                        [i for i in range(ensembleStartYear, ensembleStartYear+numEnsembles[i])]
                    )
                    
                fileDates = [fileDate] * len(ensembleYears)

                idx=pd.MultiIndex.from_tuples(
                    tuple(zip(csvSites, csvVariables, ensembleYears, fileDates)),  
                    names = ['site','tsType', 'year', 'fileDate']
                )

                idxReadCsv = idx[idx.get_level_values(0) != 'DUMMY']
                
                data = pd.read_csv(
                    hindcastFile, 
                    skiprows=2, 
                    header=None, 
                    names = idxReadCsv, 
                    index_col=0, 
                    parse_dates=True
                )


                data = data.fillna(0.0)

                data.columns.names = ['site','tsType', 'year', 'fileDate']

                data.index = data.index.tz_localize('UTC').tz_convert('US/Pacific')

                data.index = pd.DatetimeIndex(
                    [i.replace(tzinfo=None) for i in data.index], 
                    name='date'
                )

                data = data.stack(level=[0,1,3])
                data.index.names = ['date','site','tsType','fileDate']
                data = data * 1000
                data = data.loc[data.index.get_level_values('site').isin(sites.keys()),:]

                grouped = data.groupby(['site'])

                print('Currently Writing to feather...')    

                for site, group in grouped:

                    site = site[0]

                    group.index = group.index.droplevel(['site','tsType'])

                    mergeDf = pd.DataFrame(index = group.index.get_level_values('date'))
                    mergeDf = mergeDf.merge(trueDf[[site]], left_index=True, right_index=True, how='left')
                    mergeDf.index = group.index

                    group = pd.concat([mergeDf, group], axis=1)
                    group.columns = group.columns.astype(str)

                    if site == 'NBBC1':
                        nbbMerge = pd.concat([nbbMerge, group])
                    else:
                        oroMerge = pd.concat([oroMerge, group])

            nbbMerge.reset_index().to_feather(rf'data\nbbORO\\{pattern}_NBBC1_{scaleFactor}.feather')
            oroMerge.reset_index().to_feather(rf'data\nbbORO\\{pattern}_ORDC1_{scaleFactor}.feather')

            del oroMerge, nbbMerge, group, data, grouped, trueDf
            gc.collect()

if __name__ == '__main__':
    main()