from __future__ import annotations
import pandas as pd
import altair as alt
from typing import List
from .dataWrangler import RobustnessTestPctDiff
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
    x=alt.X("times:T").axis(title="Time (PST)"),
    y=alt.Y("flow:Q").axis(title="Flow (CFS)")
    )

    selection = alt.selection_point(fields = ["member"], bind="legend")
    domain = [str(i) for i in range(1980,2021)]
    range_ = [ensembleColor]*41
    ensChart = alt.Chart(ens).mark_line( strokeWidth=0.5).encode(
        x=alt.X("times:T").axis(title="Time (PST)", format='%d %b %Y'),
        y=alt.Y("flow:Q").axis(title="Flow (CFS)"),
        color = alt.Color("member").legend(columns=2, symbolLimit=41).scale(domain=domain, range = range_),
        opacity= alt.condition(selection, alt.value(1), alt.value(0.05))
    ).add_params(
        selection
    )

    chart = alt.layer(ensChart, detChart).properties(height=500)

    return chart


def getEnsembleChartSingleMember(df: pd.DataFrame, forecastDate: str, ensembleColor: str) -> alt.Chart:
    
    det, ens = getEnsemblePlotData(df, forecastDate )

    detChart = alt.Chart(det).mark_line(color='black').encode(
    x=alt.X("times:T").axis(title="Time (PST)"),
    y=alt.Y("flow:Q").axis(title="Flow (CFS)")
    )

    selection = alt.selection_point(fields = ["member"], bind="legend")
    domain = [f'1986_{i}' for i in range(210,510,10)]
    range_ = [ensembleColor]*41
    ensChart = alt.Chart(ens).mark_line( strokeWidth=0.5).encode(
        x=alt.X("times:T").axis(title="Time (PST)", format='%d %b %Y %H'),
        y=alt.Y("flow:Q").axis(title="Flow (CFS)"),
        color = alt.Color("member").legend(columns=2, symbolLimit=41).scale(domain=domain, range = range_),
        opacity= alt.condition(selection, alt.value(1), alt.value(0.05))
    ).add_params(
        selection
    )

    chart = alt.layer(ensChart, detChart).properties(height=500)

    return chart

def pctDiffPlot(testObj: RobustnessTestPctDiff):
    
    data = testObj.calculate()

    data= data.drop(testObj.reservoir_name, axis=1).stack()
    data.index.names = ['forecastDate','times', 'member']
    data.name = 'pctDiff'

    data = data.reset_index()

    chart = alt.Chart(data).mark_boxplot(extent='min-max').encode(
        x = 'forecastDate',
        y=alt.Y('pctDiff').axis(format='%')
    )
    
    return chart

def pctVolHeatmap(testObj: RobustnessTestPctDiff, scaleFactor: int | str) -> List[alt.Chart, pd.DataFrame]:

    rt = testObj.calculate()

    heatmapDf = rt.drop(testObj.reservoir_name, axis=1)

    tmp = heatmapDf.reset_index().drop('forecastDate', axis=1).set_index('times').stack()
    tmp.index.names = ['forecastDate', 'member']
    tmp.name = 'pctDif'
    tmp = tmp.reset_index()

    c = alt.Chart(tmp, width=1500, height=750).mark_rect().encode(
        x=alt.X('member:O'),
        y=alt.Y('yearmonthdate(forecastDate):O').axis(format='%d %b %Y'),
        color=alt.Color('pctDif:Q').scale(
            scheme='redblue', domainMax=3, domainMin=-3)
    )

    text = c.mark_text(baseline='middle').encode(
        alt.Text('pctDif', format = '0.0%'),
        color = alt.condition(
            abs(alt.datum.pctDif) > 0.5,
            alt.value('black'),
            alt.value('white')
        )
    )
    merge = (c + text).properties(title =f"Determinstic: {scaleFactor}")

    return [merge, heatmapDf]