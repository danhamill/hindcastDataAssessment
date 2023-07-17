import streamlit as st
import pandas as pd
import altair as alt
from src.dataWrangler import EnsembleDataReaderStreamlit, getIssueDates, RobustnessTestPctDiff
from src.plots import pctDiffPlot, getEnsembleChart
import os


@st.cache_data
def loadScaleFactorData(selected_pattern, selected_scaleFactor):
    r_edr = EnsembleDataReaderStreamlit(pattern=selected_pattern, scaleFactor=selected_scaleFactor)
    allData = r_edr.loadData()
    return allData

st.title('Percent Difference Test')


selected_pattern = st.sidebar.selectbox("Choose a pattern", ['1986','1997'])
selected_scaleFactor = st.sidebar.selectbox("Choose a scale Factor", list(range(200,510,10)))

st.sidebar.header("Robustness Testing")


get_scale_factor_data = st.sidebar.button("Click to get robstness testing data")

if get_scale_factor_data:

    allData = loadScaleFactorData(selected_pattern=selected_pattern, selected_scaleFactor=selected_scaleFactor)



    # st.altair_chart(pctDiffPlot, use_container_width=True)


st.sidebar.header("Individual Forecast Plotting")
selected_forecast = st.sidebar.selectbox("Choose an Individual Forecast Date", getIssueDates(selected_pattern))
get_indiviudal_forecast_data = st.sidebar.button("Click to get Individual Forecast Data",)
get_individual_forecast_plot = st.sidebar.button("Click to plot Individual forecast Data")
reset_data = st.sidebar.button("Click to reset")

# if get_individual_forecast_plot:
with st.form("test"):
    
    sliderForecast = st.selectbox("Choose a Forecast to plot", getIssueDates(selected_pattern))
    submitted = st.form_submit_button("Update Plot")

if submitted:
    allData = loadScaleFactorData(selected_pattern=selected_pattern, selected_scaleFactor=selected_scaleFactor)
    ensembleChart = getEnsembleChart(allData, sliderForecast, 'grey' )
    st.altair_chart(ensembleChart, use_container_width=True)
    



if get_indiviudal_forecast_data:
    allData = loadScaleFactorData(selected_pattern, selected_scaleFactor)
    forecast = allData.loc[allData.forecastDate == selected_forecast, :]
    st.table(forecast)

col1, col2 = st.columns(2)

with col1:
    exceedProb = st.text_input("Exceedance probability (0-100)")
    exceedProbTest = st.button("Run exceeance Probability Test") 
with col2: 
    nDays = st.text_input("NDay Volume to Calculate")

st.write('Must fill out both fields before starting test!')

if exceedProbTest:
    allData = loadScaleFactorData(selected_pattern=selected_pattern, selected_scaleFactor=selected_scaleFactor)
    testObj = RobustnessTestPctDiff(allData, nDays )
    rt = testObj.calculate()
    pctDiffPlot = pctDiffPlot(rt, nDays)
    summary = testObj.pctDiffStats(rt)

    st.header(f'Percent Difference Summary statistics for {nDays}-day volumes.')
    st.table(summary.reset_index())

    memberTable, pctDiffTable = testObj.pctDiffNEP(rt, int(exceedProb))

    st.header('Member Table')
    st.table(memberTable)

    st.header('NEP Percent Difference Magnitude')
    st.table(pctDiffTable)
if reset_data:
    st.runtime.legacy_caching.clear_cache()
    reset_data = False
