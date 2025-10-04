# import ee
# import geemap
import pandas as pd
import matplotlib.pyplot as plt

# what does this code do.... 
# authenticates and initializes the earth engine api
# south carolina is the area of interest
# Pulls modis data from the last 5 years
# gets the mean ndvi from the last 15 days
# Stores NDVI values in pandas
# shows potential bloom periods from the last 5
# will plot the data
# will export the data into a csv file 

# authenticating earth api... when running this code for the first time id run this section only once
ee.Authenticate()
ee.Initialize()

# the south carolina region
sc_bbox = ee.Geometry.Rectangle([-83, 32, -78, 35])

# loading the dataset
modis = (ee.ImageCollection('MODIS/061/MOD13Q1')
         .filterBounds(sc_bbox)
         .filterDate('2018-01-01', '2023-12-31')
         .select('NDVI'))



# mean ndvi calculation function
def mean_ndvi(image):
    mean_dict = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=sc_bbox,
        scale=250
    )
    return image.set('mean_ndvi', mean_dict.get('NDVI'))



# map the function over the collection
ndvi_mean = modis.map(mean_ndvi)



# converting into pandas
ndvi_list = ndvi_mean.getInfo()['features']
dates = [f['properties']['system:time_start'] for f in ndvi_list]
values = [f['properties']['mean_ndvi'] for f in ndvi_list]

ndvi_df = pd.DataFrame({
    'date': pd.to_datetime(dates, unit='ms'),
    'ndvi': values
})



# detecting bloom periods
threshold = 0.5 
ndvi_df['bloom'] = ndvi_df['ndvi'] > threshold



# plotting the bloom highlights
plt.figure(figsize=(12,6))

# mean ndvi line
plt.plot(ndvi_df['date'], ndvi_df['ndvi'], color='purple', label='Mean NDVI')

# potential bloom points
plt.scatter(ndvi_df[ndvi_df['bloom']]['date'], 
            ndvi_df[ndvi_df['bloom']]['ndvi'], 
            color='orange', label='Potential Bloom')

# high bloom points
high_bloom = ndvi_df['ndvi'] > 0.7
plt.scatter(ndvi_df[high_bloom]['date'], 
            ndvi_df[high_bloom]['ndvi'], 
            color='yellow', label='High Bloom')

plt.xlabel('date')
plt.ylabel('ndvi')
plt.title('potential bloom periods in south carolina 2018-2023')
plt.legend()
plt.grid(True)
plt.show()

# saving to csv
ndvi_df.to_csv('SC_NDVI_2018_2023.csv', index=False)
print("CSV saved as SC_NDVI_2018_2023.csv")
