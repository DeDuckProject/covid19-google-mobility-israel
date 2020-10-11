import pandas as pd
import ssl
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

#fixing ssl issue with url fetching from https
ssl._create_default_https_context = ssl._create_unverified_context

#get new data from google - comment this out to disable downloading every time
googleMobilityCsv = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv')
googleMobilityCsv.to_pickle('Global_Mobility_Report.pkl')

#load downloaded csv from local cache - un-comment this to use the already downloaded data
# googleMobilityCsv= pd.read_pickle('Global_Mobility_Report.pkl')

#filter data:
isIsrael = googleMobilityCsv['country_region_code']=='IL' # filter only israel
israelDataCsv = googleMobilityCsv[isIsrael]
israelDataCsv = israelDataCsv.filter(items=['date', 'sub_region_1', 'sub_region_2', 'retail_and_recreation_percent_change_from_baseline', 'grocery_and_pharmacy_percent_change_from_baseline', 'parks_percent_change_from_baseline', 'transit_stations_percent_change_from_baseline', 'workplaces_percent_change_from_baseline', 'residential_percent_change_from_baseline'])\
    .rename(columns={"retail_and_recreation_percent_change_from_baseline": "retail", "grocery_and_pharmacy_percent_change_from_baseline": "grocery", "parks_percent_change_from_baseline": 'parks', 'transit_stations_percent_change_from_baseline': 'transit', 'workplaces_percent_change_from_baseline': 'workplace', 'residential_percent_change_from_baseline': 'residential'})

# list sub regions 1,2:
subRegions1 = israelDataCsv['sub_region_1'].unique()
subRegions1 = np.delete(subRegions1, [0])
subRegions2 = israelDataCsv['sub_region_2'].unique()
subRegions2 = np.delete(subRegions2, [0])

# Filter out weekends:
israelDataCsv['date'] = pd.to_datetime(israelDataCsv['date'])
israelDataCsv['day_of_week'] = israelDataCsv['date'].dt.dayofweek
isBDay = israelDataCsv['day_of_week'] > 5
israelDataCsv = israelDataCsv[isBDay]

# filter From date if needed
# dateFilter = israelDataCsv['date'] > '2020-08-15'
# israelDataCsv = israelDataCsv[dateFilter]

categories = ['retail', 'grocery', 'parks', 'transit', 'workplace', 'residential']

# set category to plot here:
category = 'residential'

fig, ax = plt.subplots()

for subRegion in subRegions1:
    isRegion = israelDataCsv['sub_region_1']==subRegion
    onlyRegion = israelDataCsv[isRegion]
    isNoSubRegion2 = israelDataCsv['sub_region_2']!=israelDataCsv['sub_region_2'] # remove rows with sub_region_2
    onlyRegion = onlyRegion[isNoSubRegion2]
    x = onlyRegion.date
    y = onlyRegion[category]
    # plt.plot(x, y, label=subRegion, linewidth=0.5)
    # ax.xaxis.set_major_locator(months)
    # ax.xaxis.set_minor_locator(days)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.plot(x, y, label=subRegion, linewidth=1)

# for subRegion in subRegions2:
#     isRegion = israelDataCsv['sub_region_2']==subRegion
#     onlyRegion = israelDataCsv[isRegion]
#     x = onlyRegion.date
#     y = onlyRegion.residential
#     ax.plot(x, y, label=subRegion, linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Change in presence')
# plt.ylim(-100, 100)

plt.title('Changes in presence (from baseline) for: ' + category)

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.grid(True)
fig.autofmt_xdate()
plt.show()
