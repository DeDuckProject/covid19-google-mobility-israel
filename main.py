import pandas as pd
import ssl
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

#fixing ssl issue with url fetching from https
ssl._create_default_https_context = ssl._create_unverified_context

#get new data from google
# googleMobilityCsv = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv')
# googleMobilityCsv.to_pickle('Global_Mobility_Report.pkl')

#load downloaded csv from local cache
googleMobilityCsv= pd.read_pickle('Global_Mobility_Report.pkl')

isIsrael = googleMobilityCsv['country_region_code']=='IL'
israelDataCsv = googleMobilityCsv[isIsrael]
israelDataCsv = israelDataCsv.filter(items=['date', 'sub_region_1', 'sub_region_2', 'retail_and_recreation_percent_change_from_baseline', 'grocery_and_pharmacy_percent_change_from_baseline', 'parks_percent_change_from_baseline', 'transit_stations_percent_change_from_baseline', 'workplaces_percent_change_from_baseline', 'residential_percent_change_from_baseline'])\
    .rename(columns={"retail_and_recreation_percent_change_from_baseline": "retail", "grocery_and_pharmacy_percent_change_from_baseline": "grocery", "parks_percent_change_from_baseline": 'parks', 'transit_stations_percent_change_from_baseline': 'transit', 'workplaces_percent_change_from_baseline': 'workplace', 'residential_percent_change_from_baseline': 'residential'})
# print (israelDataCsv)

# list sub regions 1,2:
subRegions1 = israelDataCsv['sub_region_1'].unique()
subRegions1 = np.delete(subRegions1, [0])
subRegions2 = israelDataCsv['sub_region_2'].unique()
subRegions2 = np.delete(subRegions2, [0])
# print ('subRegions1', subRegions1)
# print ('subRegions2', subRegions2)

# Filter weekends:
israelDataCsv['date'] = pd.to_datetime(israelDataCsv['date'])
israelDataCsv['day_of_week'] = israelDataCsv['date'].dt.dayofweek
isBDay = israelDataCsv['day_of_week'] > 5
israelDataCsv = israelDataCsv[isBDay]

# filter From date
# dateFilter = israelDataCsv['date'] > '2020-09-15'
# israelDataCsv = israelDataCsv[dateFilter]

categories = ['retail', 'grocery', 'parks', 'transit', 'workplace', 'residential']

# googleMobilityCsv.head()
fig, ax = plt.subplots()

for subRegion in subRegions1:
    isRegion = israelDataCsv['sub_region_1']==subRegion
    onlyRegion = israelDataCsv[isRegion]
    isNoSubRegion2 = israelDataCsv['sub_region_2']!=israelDataCsv['sub_region_2'] # remove rows with sub_region_2
    onlyRegion = onlyRegion[isNoSubRegion2]
    x = onlyRegion.date
    y = onlyRegion.residential
    # plt.plot(x, y, label=subRegion, linewidth=0.5)
    # ax.xaxis.set_major_locator(months)
    # ax.xaxis.set_minor_locator(days)
    ax.plot(x, y, label=subRegion, linewidth=0.5)

# for subRegion in subRegions2:
#     isRegion = israelDataCsv['sub_region_2']==subRegion
#     onlyRegion = israelDataCsv[isRegion]
#     x = onlyRegion.date
#     y = onlyRegion.residential
#     ax.plot(x, y, label=subRegion, linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Change in mobility')
# plt.ylim(-100, 100)

plt.title('Changes in behaviour by regions')

# Put a legend to the right of the current axis
# box = ax.get_position()
# ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

# plt.legend(loc='lower left', fancybox=True, shadow=True)
plt.grid(True)
fig.autofmt_xdate()
plt.show()

print ('done')
