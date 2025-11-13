from src.dataWrangler import EnsembleDataReaderStreamlit
import pandas as pd

reservoir_name = 'FOLC1F'
all_nep_results = []  # Collect all NEP values across all scenarios
ndays = [1,2,3,5]
exceedProbs = [50, 75, 90]
patterns = ['1986','1997']
output_file = r'output\folsom_ESRD_nep_results_comprehensive.xlsx'
CFS_TO_ACREFEET = 3600 / 43560  # Conversion factor from cfs to acre-feet

for scale_factor in range(200,510, 10):
    for pattern in patterns:

        reader = EnsembleDataReaderStreamlit(
            pattern = pattern, scaleFactor=scale_factor, reservoir_name='FOLC1F', data_directory=r'data\Folsom'
        )

        data = reader.loadData().set_index(['forecastDate','times'])
        
        for exceedProb in exceedProbs:
            for nDay in ndays:
                for forecastDate, group in data.groupby('forecastDate'):
                    group.index = group.index.droplevel('forecastDate')
                    if not group.index.get_level_values('times').is_monotonic_increasing:
                        group = group.sort_index()
                    # Accumulate Volume (cfs)
                    group = group.astype(float).cumsum(axis=0)
                    
                    # convert to acre-feet
                    group = group * CFS_TO_ACREFEET  # cfs to acre-feet
                    # Select nDay Volume
                    nDayTimeStamp = group.index.min()+ pd.DateOffset(hours=int(nDay)*24-1)

                    # Calculate pct difference
                    subGroup = group.loc[group.index == nDayTimeStamp, [str(i) for  i in range(1980, 2021)]]

                    if not subGroup.empty:
                        dist = subGroup.stack()

                        idxQuantile = (dist.sort_values()[::-1] <= dist.quantile(exceedProb/100)).idxmax()
                        valueQuantile = dist[idxQuantile]
                        
                        # Store the NEP value with metadata
                        all_nep_results.append({
                            'forecastDate': forecastDate,
                            'pattern': pattern,
                            'scaleFactor': scale_factor,
                            'nDay': nDay,
                            'exceedanceProb': exceedProb,
                            'nepValue': valueQuantile
                        })

        print(f"Completed Pattern: {pattern}, Scale Factor: {scale_factor}")

# Convert all results to DataFrame
nep_results_df = pd.DataFrame(all_nep_results)
print("Total dataset shape:", nep_results_df.shape)

# Create pivot table for easier excel analysis
pivot_df = nep_results_df.pivot(index=['forecastDate', 'pattern', 'scaleFactor'], 
                                columns=['nDay','exceedanceProb'],
                                values='nepValue').sort_index(level=['pattern','scaleFactor','forecastDate'], axis=0)

print("\nPivot table created successfully!")
print("Pivot table shape:", pivot_df.shape)
print("\nPivot table sample:")
print(pivot_df.head())

# Save results to Excel
pivot_df.to_excel(output_file)
print(f"\nResults saved to: {output_file}")








