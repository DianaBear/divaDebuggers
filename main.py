import ee
import geemap
import pandas as pd
import matplotlib.pyplot as plt


#authenticating eatrth api
ee.Authenticate()
ee.Initialize()

#the south carolina region
sc_bbox = ee.Geometry.Rectangle([-83, 32, -78, 35])  # [W, S, E, N]

#loading the dataset
modis = ee.ImageCollection('MODIS/061/MOD13Q1') \
            .filterBounds(sc_bbox) \
            .filterDate('2018-01-01', '2023-12-31') \
            .select('NDVI')  # Use 'EVI' if you prefer

#mean NDVI calculation function
def mean_ndvi(image):
    mean_dict = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=sc_bbox,
        scale=250
    )
    return image.set('mean_ndvi', mean_dict.get('NDVI'))

ndvi_mean = modis.map(mean_ndvi)


#converting into pandas
ndvi_list = ndvi_mean.getInfo()['features']
dates = [f['properties']['system:time_start'] for f in ndvi_list]
values = [f['properties']['mean_ndvi'] for f in ndvi_list]

ndvi_df = pd.DataFrame({
    'date': pd.to_datetime(dates, unit='ms'),
    'ndvi': values
})

# detecting bloom periods
threshold = 0.5  # NDVI above this may indicate bloom
ndvi_df['bloom'] = ndvi_df['ndvi'] > threshold

# plotting the results
plt.figure(figsize=(12,6))
plt.plot(ndvi_df['date'], ndvi_df['ndvi'], label='Mean NDVI', color='purple')


plt.scatter(ndvi_df[ndvi_df['bloom']]['date'], ndvi_df[ndvi_df['bloom']]['ndvi'], color='orange', label='Potential Bloom')


plt.xlabel('date')
plt.ylabel('ndvi')

plt.title('potential bloom periods in south carolina')
plt.legend()
plt.grid(True)
plt.show()

# saving to csv
ndvi_df.to_csv('SC_NDVI_2018_2023.csv', index=False)
print("CSV saved: SC_NDVI_2018_2023.csv")
