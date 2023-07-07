import pandas as pd
from dataWrangler import EnsembleDataReaderStreamlit


def loadScaleFactorData(selected_pattern: str, selected_scaleFactor: int):
    r_edr = EnsembleDataReaderStreamlit(pattern=selected_pattern, scaleFactor=selected_scaleFactor)
    allData = r_edr.loadData()
    return allData

def main():
 

    df = loadScaleFactorData('1986', 200)
    df = df.loc[df.forecastDate == '1986020112', :]
    df = df.drop(['forecastDate','times'], axis=1)

    df.to_clipboard(index=False, header=False)



if __name__ =='__main__':
    main()