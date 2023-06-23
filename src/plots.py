import pandas as pd
import altair as alt


def pctDiffPlot(data: pd.DataFrame, nDays):

    data= data.drop('FOLC1F', axis=1).stack()
    data.index.names = ['forecastDate','times', 'member']
    data.name = 'pctDiff'

    data = data.reset_index()

    chart = alt.Chart(data).mark_boxplot(extent='min-max').encode(
        x = 'forecastDate',
        column = 'forecastDate',
        y=alt.Y('pctDiff').axis(format='%')
    ).resolve_scale(y='independent', x='independent').properties(width=10)

    # chart = alt.Chart(data).mark_circle().encode(
    #     x= alt.X('member').scale(domain=(1975,2025)),
    #     y = alt.Y('pctDiff').axis(format ='%'),
    #     row='forecastDate'
    # ).resolve_scale(y='independent',x='independent').interactive()
    

    return chart