import streamlit as st
import pandas as pd
import altair as alt
from src.dataWrangler import EnsembleDataReader, getIssueDates, RobustnessTestPctDiff
from src.plots import pctDiffPlot
import os


@st.cache_data
def loadScaleFactorData(selected_pattern, selected_scaleFactor):
    r_edr = EnsembleDataReader(pattern=selected_pattern, scaleFactor=selected_scaleFactor)
    scale_factor_dss_paths = r_edr.getSingleScaleFactorDssPaths()
    allData = r_edr.compileAllData(scale_factor_dss_paths)
    return allData

st.title('Percent Difference Test')


selected_pattern = st.sidebar.selectbox("Choose a pattern", ['1986','1997'])
selected_scaleFactor = st.sidebar.selectbox("Choose a scale Factor", list(range(200,510,10)))

st.sidebar.header("Robustness Testing")


get_scale_factor_data = st.sidebar.button("Click to get robstness testing data")

if get_scale_factor_data:

    allData = loadScaleFactorData(selected_pattern=selected_pattern, selected_scaleFactor=selected_scaleFactor)


col1, col2 = st.columns(2)

with col1:
    exceedProb = st.text_input("Exceedance probability (0-100)")
    exceedProbTest = st.button("Run exceeance Probability Test") 
with col2: 
    nDays = st.text_input("NDay Volume to Calculate")

st.write('Must fill out both fields before starting test!')

if exceedProbTest:
    allData = loadScaleFactorData(selected_pattern=selected_pattern, selected_scaleFactor=selected_scaleFactor)
    testObj = RobustnessTestPctDiff(allData, exceedProb, nDays )
    rt = testObj.calculate()
    pctDiffPlot = pctDiffPlot(rt, nDays)
    summary = testObj.pctDiffStats(rt)

    st.header(f'Percent Difference Summary statistics for {nDays}-day volumes.')
    st.table(summary.reset_index())
    # st.altair_chart(pctDiffPlot, use_container_width=True)


st.sidebar.header("Individual Forecast Plotting")
selected_forecast = st.sidebar.selectbox("Choose an Individual Forecast Date", getIssueDates(selected_pattern))
get_indiviudal_forecast_data = st.sidebar.button("Click to get Individual Forecast Data",)
reset_data = st.sidebar.button("Click to reset")



if get_indiviudal_forecast_data:
    edr = EnsembleDataReader(pattern = selected_pattern, scaleFactor=selected_scaleFactor)
    st.sidebar.text(f'Input DSS File is: {os.path.basename(edr.dssFile)}')
    selected_ensemble_pathnames = edr.getSingleForecastDssPaths(fPartPattern=selected_forecast)
    selected_determinsitic_pathnames = edr.getDeterminsticDSSPaths()

    mergeData = edr.compileData(selected_ensemble_pathnames, selected_determinsitic_pathnames)
    getData = False
    if isinstance(mergeData,pd.DataFrame):    
        st.table(mergeData)

if reset_data:
    st.runtime.legacy_caching.clear_cache()
    reset_data = False