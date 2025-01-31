import streamlit as st
import pandas as pd
import altair as alt
from src.dataWrangler import EnsembleDataReaderStreamlit, getIssueDates, RobustnessTestPctDiff
from src.plots import pctDiffPlot, getEnsembleChart, pctVolHeatmap
import os
import io

PROJECT_LIST = {
    'FOLSOM': {
        'RESERVOIRS':['FOLSOM'],
        'PATTERNS':['1986','1997']
    },
    'NEW BULLARDS BAR - OROVILLE':{
        'RESERVOIRS':['OROVILLE','NEW BULLARDS BAR'],
        'PATTERNS':['1986','1997']
    }
}

RESERVOIR_NAMES = {
    'FOLSOM':'FOLC1F',
    'OROVILLE':'ORDC1',
    'NEW BULLARDS BAR':'NBBC1'
}

def toExcel(df, nday, pattern, scale):
    (max_row, max_col) = df.shape
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=f'{nday}-Day_{pattern}_Pattern_{scale}_scale')
    workbook = writer.book
    worksheet = writer.sheets[f'{nday}-Day_{pattern}_Pattern_{scale}_scale']
    format1 = workbook.add_format({'num_format': '0.00%'}) 
    worksheet.conditional_format(f"C2:AQ{max_row+1}", {"type": "3_color_scale"})
    worksheet.set_column('C:AQ', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data

@st.cache_data
def loadScaleFactorData(selected_pattern, selected_scaleFactor, reservoir_name, data_directory):
    r_edr = EnsembleDataReaderStreamlit(pattern=selected_pattern, scaleFactor=selected_scaleFactor,
                                        reservoir_name = reservoir_name, data_directory=data_directory)
    allData = r_edr.loadData(), r_edr.featherFile
    return allData

st.set_page_config(layout="wide")
st.title('Hindcast Data Assessment')

selected_project = st.sidebar.selectbox("Choose a Project", PROJECT_LIST.keys())
selected_reservoir = st.sidebar.selectbox('Choose a Reservoir', PROJECT_LIST[selected_project]['RESERVOIRS'])
selected_pattern = st.sidebar.selectbox("Choose a pattern",  PROJECT_LIST[selected_project]['PATTERNS'])
selected_reservoir_name = RESERVOIR_NAMES[selected_reservoir]

if selected_project == "FOLSOM":
    hindcast_scales = list(range(200,510,10))
    data_directory = os.path.join('data','Folsom')
elif selected_project == 'NEW BULLARDS BAR - OROVILLE':
    data_directory =  os.path.join('data', 'nbbORO')
    if selected_pattern == '1997':
        hindcast_scales = ['84','86','88','90','92','94','96','98','100','102','104','106','108','110','120','130']
    elif selected_pattern == '1986':
        hindcast_scales = ['100','102','104','106','108','110','112','114','116','118','120','130','140','150']
                        
selected_scaleFactor = st.sidebar.selectbox("Choose a scale Factor", hindcast_scales)

# st.sidebar.header("Robustness Testing")


# get_scale_factor_data = st.sidebar.button("Click to get robstness testing data")

# if get_scale_factor_data:

#     allData, _ = loadScaleFactorData(selected_pattern=selected_pattern, 
#                                   selected_scaleFactor=selected_scaleFactor,
#                                   reservoir_name = selected_reservoir_name,
#                                   data_directory = data_directory)



    # st.altair_chart(pctDiffPlot, use_container_width=True)


# st.sidebar.header("Individual Forecast Plotting")
# selected_forecast = st.sidebar.selectbox("Choose an Individual Forecast Date", getIssueDates(selected_pattern, selected_project))
# get_indiviudal_forecast_data = st.sidebar.button("Click to get Individual Forecast Data",)
# get_individual_forecast_plot = st.sidebar.button("Click to plot Individual forecast Data")
reset_data = st.sidebar.button("Click to reset")

# if get_individual_forecast_plot:
with st.form("test"):
    
    sliderBar = st.select_slider("Choose a Forecast to plot", getIssueDates(selected_pattern, selected_project))
    # sliderForecast = st.selectbox("Choose a Forecast to plot", getIssueDates(selected_pattern, selected_project))
    submitted = st.form_submit_button("Update Plot")

    if submitted:
        allData, fileName = loadScaleFactorData(selected_pattern=selected_pattern, 
                                    selected_scaleFactor=selected_scaleFactor,
                                    reservoir_name = selected_reservoir_name,
                                    data_directory = data_directory)
        ensembleChart = getEnsembleChart(allData, sliderBar, 'grey', selected_reservoir_name )
        st.text(fr'Reading {os.path.basename(fileName)}')
        st.altair_chart(ensembleChart, use_container_width=True)

nDays = st.text_input("NDay Volume to Calculate")

assessVolumeDifferences = st.button("Assess n-day volume differences") 

if assessVolumeDifferences:

    testObj = RobustnessTestPctDiff(
        selected_pattern=selected_pattern, 
        selected_scaleFactor = selected_scaleFactor, 
        reservoir_name=selected_reservoir_name, 
        data_directory=data_directory, 
        nDays=nDays)
    
    pctDiffPlot_ = pctDiffPlot(testObj)

    heatmap, pctDiff = pctVolHeatmap(testObj, selected_scaleFactor)

    st.text(f'Pattern: {selected_pattern} Reservoir: {selected_reservoir} Scale Factor: {selected_scaleFactor}')

    compound = alt.vconcat(heatmap, pctDiffPlot_).resolve_scale(x='shared')

    st.altair_chart(pctDiffPlot_, use_container_width=True)

    dfExcel = toExcel(pctDiff, nDays, selected_pattern, selected_scaleFactor)

    download2 = st.download_button(
        label='Download Boxplot Data as Excel File',
        data = dfExcel,
        file_name=f'Pattern: {selected_pattern} Reservoir: {selected_reservoir} Scale Factor: {selected_scaleFactor}.xlsx',
    )

    summary = testObj.pctDiffStats()

    st.header(f'Percent Difference Summary statistics for {nDays}-day volumes.')
    st.dataframe(summary.style.apply(
        lambda row: ['background-color: yellow' if row.name == summary.index[0] else '' for _ in row], axis=1),
        use_container_width=True,
    )





    output = pd.DataFrame()

    for scaleFactor in hindcast_scales:

        testObj = RobustnessTestPctDiff(
            selected_pattern=selected_pattern, 
            selected_scaleFactor = scaleFactor, 
            reservoir_name=selected_reservoir_name, 
            data_directory=data_directory, 
            nDays=nDays
        )
        
        tmp = testObj.pctDiffStats().iloc[0:1]

        tmp.index = pd.Index([scaleFactor], name='Scale Factor')

        output = pd.concat([output, tmp])

    st.header(f'Event Median Percent Difference Summary statistics for {nDays}-day volumes for all scale factors.')

    st.dataframe(output, use_container_width=True)

    # output = output.stack().reset_index()
    
    # output.columns = ['Scale Factor', 'NEP', 'value']
    # output.loc[:,'value'] = pd.to_numeric(output.value.str.replace('%',''))/100

    # st.dataframe(output, use_container_width=True)
    # nearest = alt.selection_point(nearest=True, on="pointerover",
    #                           fields=["Scale Factor:O"], empty=False)
    
    # scaleChart = alt.Chart(output).mark_line().encode(
    #     x = alt.X('Scale Factor:O', title='Scale Factor'),
    #     y = alt.Y('value:Q', title=f'{nDays}-day Percent Volume Difference').axis(format='%'),
    #     color = alt.Color('NEP:N', title='NEP'),
    # )

    # selectors = alt.Chart(output).mark_point().encode(
    #     x='Scale Factor:O',
    #     opacity=alt.value(0),
    # ).add_params(
    #     nearest
    # )

    # points = scaleChart.mark_point().encode(
    #     opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    # )

    # text = scaleChart.mark_text(align='left', dx=5, dy=-5).encode(
    #     text=alt.condition(nearest, 'value:Q', alt.value(' '))
    # )

    # aa = alt.layer(
    #     scaleChart, selectors, points, text
    # )



    # st.altair_chart(aa, use_container_width=True)

        


    # memberTable, pctDiffTable = testObj.pctDiffNEP(int(75))

    # st.header('Member Table')
    # st.table(memberTable)

    # st.header('NEP Percent Difference Magnitude')
    # st.table(pctDiffTable)
if reset_data:
    st.runtime.legacy_caching.clear_cache()
    reset_data = False
