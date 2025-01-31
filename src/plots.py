from __future__ import annotations
import pandas as pd
import altair as alt
from typing import List
from .dataWrangler import RobustnessTestPctDiff
alt.data_transformers.disable_max_rows()

def getEnsemblePlotData(df: pd.DataFrame, forecastDate: str, reservoirName) -> list[pd.DataFrame]:
    plotDf = df.groupby('forecastDate').get_group(forecastDate)
    plotDf = plotDf.set_index(['forecastDate','times']).stack()
    plotDf.index.names = ['forecastDate','times', 'member']
    plotDf.name = 'flow'
    plotDf = plotDf.reset_index()

    det = plotDf.loc[plotDf.member == reservoirName, :]
    ens = plotDf.loc[plotDf.member != reservoirName, :]
    return det, ens

def getEnsembleChart(df: pd.DataFrame, forecastDate: str, ensembleColor: str, reservoirName: str) -> alt.Chart:
    
    det, ens = getEnsemblePlotData(df, forecastDate, reservoirName )

    detChart = alt.Chart(det).mark_line().encode(
    x=alt.X("times:T").axis(title="Time (PST)"),
    y=alt.Y("flow:Q").axis(title="Flow (CFS)"),
    color = alt.Color("member", title="Simulated Historical").scale(domain=[reservoirName], range=['red'])
    )

    selection = alt.selection_point(fields = ["member"], bind="legend")
    domain = [str(i) for i in range(1980,2021)]
    range_ = [ensembleColor]*41
    ensChart = alt.Chart(ens).mark_line( strokeWidth=0.5).encode(
        x=alt.X("times:T").axis(title="Time (PST)", format='%d %b %Y'),
        y=alt.Y("flow:Q").axis(title="Flow (CFS)"),
        color = alt.Color("member").legend(columns=2, symbolLimit=43).scale(domain=domain, range = range_),
        opacity= alt.condition(selection, alt.value(1), alt.value(0.05))
    ).add_params(
        selection
    )

    chart = alt.layer(ensChart, detChart).properties(height=500).resolve_scale(color='independent')

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
    data.index.names = ['times','forecastDate', 'member']
    data.name = 'pctDiff'

    data = data.reset_index()

    topFiftyIdx = data.groupby('forecastDate').pctDiff.nlargest(21).index.get_level_values(1)

    topFifty = data.iloc[topFiftyIdx]

    chart = alt.Chart(data).mark_boxplot(extent='min-max').encode(
        x = alt.X('utcyearmonthdate(times):O', title='Forecast Date').axis(format='%d %b %Y'),
        y= alt.Y('pctDiff', title = f'{testObj.nDay}-day Percent Volume Difference').axis(format='%'),
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
        y=alt.Y('member:O'),
        x=alt.X('yearmonthdate(forecastDate):O', title=None).axis(labels=False),
        color=alt.Color('pctDif:Q').scale(
            scheme='redblue', domainMax=3, domainMin=-3)
    )
    text = c.mark_text(baseline='middle').encode(
        alt.Text('pctDif', format = '0.0%'),
        color = alt.condition(
            abs(alt.datum.pctDif) > 0.25,
            alt.value('black'),
            alt.value('white')
        )
    )
    merge = (c + text).properties(title =f"Pattern: {testObj.pattern} \t Reservoir: {testObj.reservoir_name}\t  Hindcast Scale: {testObj.scaleFactor}\tPercent Difference n-day: {testObj.nDay}")

    return [merge, heatmapDf]