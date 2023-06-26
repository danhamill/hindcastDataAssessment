import pandas as pd
from dataWrangler import EnsembleDataReader
import gc

def loadScaleFactorData(selected_pattern, selected_scaleFactor):
    r_edr = EnsembleDataReader(pattern=selected_pattern, scaleFactor=selected_scaleFactor)
    scale_factor_dss_paths = r_edr.getSingleScaleFactorDssPaths()
    allData = r_edr.compileAllData(scale_factor_dss_paths)
    return allData


for pattern in ['1986','1997']:
    for scaleFactor in range(200,510,10):

        df = loadScaleFactorData(pattern, scaleFactor)
        df = df.reset_index()
        df.columns = df.columns.astype(str)
        df.to_feather(rf'data\{pattern}_{scaleFactor}.feather')
        del df
        gc.collect()