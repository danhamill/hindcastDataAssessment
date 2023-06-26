import pandas as pd
import altair as alt
alt.data_transformers.disable_max_rows()

def getEnsemblePlotData(df: pd.DataFrame, forecastDate: str) -> list[pd.DataFrame]:
    plotDf = df.groupby('forecastDate').get_group(forecastDate)
    plotDf = plotDf.set_index(['forecastDate','times']).stack()
    plotDf.index.names = ['forecastDate','times', 'member']
    plotDf.name = 'flow'
    plotDf = plotDf.reset_index()

    det = plotDf.loc[plotDf.member == 'FOLC1F', :]
    ens = plotDf.loc[plotDf.member != 'FOLC1F', :]
    return det, ens

def getEnsembleChart(df: pd.DataFrame, forecastDate: str, ensembleColor: str) -> alt.Chart:
    
    det, ens = getEnsemblePlotData(df, forecastDate )

    detChart = alt.Chart(det).mark_line(color='black').encode(
    x=alt.X("times\:T").axis(title="Time (PST)"),
    y=alt.Y("flow\:Q").axis(title="Flow (CFS)")
    )

    selection = alt.selection_point(fields = ["member"], bind="legend")
    domain = [str(i) for i in range(1980,2021)]
    range_ = [ensembleColor]*41
    ensChart = alt.Chart(ens).mark_line( strokeWidth=0.5).encode(
        x=alt.X("times\:T").axis(title="Time (PST)"),
        y=alt.Y("flow\:Q").axis(title="Flow (CFS)"),
        color = alt.Color("member").legend(columns=2, symbolLimit=41).scale(domain=domain, range = range_),
        opacity= alt.condition(selection, alt.value(1), alt.value(0.2))
    ).add_params(
        selection
    )

    chart = alt.layer(ensChart, detChart)

    return chart


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