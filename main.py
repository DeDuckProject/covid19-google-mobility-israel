import pandas as pd
import ssl
import matplotlib
import numpy as np

from annotations import annotate

matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Flags:
shouldRemoveWeekends = True

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

#fixing ssl issue with url fetching from https
ssl._create_default_https_context = ssl._create_unverified_context

#get new data from google - comment this out to disable downloading every time
# googleMobilityCsv = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv')
# googleMobilityCsv.to_pickle('Global_Mobility_Report.pkl')

#load downloaded csv from local cache - un-comment this to use the already downloaded data
googleMobilityCsv = pd.read_pickle('Global_Mobility_Report.pkl')

def getCountryData(country):
    #filter data:
    isCountryFilter = googleMobilityCsv['country_region']==country # filter only country
    countryData = googleMobilityCsv[isCountryFilter]
    countryData = countryData.filter(items=['country_region', 'date', 'sub_region_1', 'sub_region_2', 'retail_and_recreation_percent_change_from_baseline', 'grocery_and_pharmacy_percent_change_from_baseline', 'parks_percent_change_from_baseline', 'transit_stations_percent_change_from_baseline', 'workplaces_percent_change_from_baseline', 'residential_percent_change_from_baseline'])\
        .rename(columns={"retail_and_recreation_percent_change_from_baseline": "retail", "grocery_and_pharmacy_percent_change_from_baseline": "grocery", "parks_percent_change_from_baseline": 'parks', 'transit_stations_percent_change_from_baseline': 'transit', 'workplaces_percent_change_from_baseline': 'workplace', 'residential_percent_change_from_baseline': 'residential'})

    # list sub regions 1,2:
    subRegions1 = countryData['sub_region_1'].unique()
    subRegions1 = np.delete(subRegions1, [0])
    subRegions2 = countryData['sub_region_2'].unique()
    subRegions2 = np.delete(subRegions2, [0])

    # Filter out weekends:
    # NOTE: filters out Friday+Saturday, which is proper for Israel, not necessarily to other countries.
    if shouldRemoveWeekends:
        countryData['date'] = pd.to_datetime(countryData['date'])
        countryData['day_of_week'] = countryData['date'].dt.dayofweek
        notSaturday = countryData['day_of_week'] != 5 # Remove sat
        notFriday = countryData['day_of_week'] != 4 # Remove fri
        countryData = countryData[notFriday & notSaturday]

    # filter From date if needed
    # dateFilter = countryData['date'] > '2020-08-15'
    # countryData = countryData[dateFilter]

    return [countryData, subRegions1, subRegions2]

# category:   0         1          2        3          4            5
allCategories = ['retail', 'grocery', 'parks', 'transit', 'workplace', 'residential']

rollingMeanWindowSize = 7

fig, ax = plt.subplots()
# ax.xaxis.set_major_locator(months)
# ax.xaxis.set_minor_locator(days)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

def groupByWeek(df):
    df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
    df = df.groupby([pd.Grouper(key='date', freq='W-SUN')])['retail', 'grocery', 'parks', 'transit', 'workplace', 'residential'].mean().reset_index().sort_values('date')
    return df

def plotByRegions(countryDf, subRegions1, subRegions2, category, cities):
    # Plot country avg:
    isNoSubRegion1 = countryDf['sub_region_1']!=countryDf['sub_region_1'] # filter only israel non-region data
    countryData = countryDf[isNoSubRegion1]
    x = countryData.date
    y = countryData[category]
    # rolling average:
    y = y.rolling(window=rollingMeanWindowSize).mean()
    ax.plot(x, y, 'k--', label='Israel average', linewidth=1)

    if not cities:
        # Plot sub-regions_1 (districts)
        for subRegion in subRegions1:
            isRegion = countryDf['sub_region_1']==subRegion
            onlyRegion = countryDf[isRegion]
            isNoSubRegion2 = countryDf['sub_region_2']!=countryDf['sub_region_2'] # remove rows with sub_region_2
            onlyRegion = onlyRegion[isNoSubRegion2]
            x = onlyRegion.date
            y = onlyRegion[category]

            # rolling average:
            y = y.rolling(window=rollingMeanWindowSize).mean()
            ax.plot(x, y, label=subRegion, linewidth=1)
    else:
        # Plot sub-regions_2 (cities)
        for subRegion in subRegions2:
            isRegion = countryDf['sub_region_2']==subRegion
            onlyRegion = countryDf[isRegion]
            x = onlyRegion.date
            y = onlyRegion[category]

            # rolling average:
            y = y.rolling(window=rollingMeanWindowSize).mean()
            ax.plot(x, y, label=subRegion, linewidth=1)

    plt.title('Changes in presence (from baseline) for: ' + category)

def plotCountryDataByCategories(countryDf, shouldGroupWeek, categories):
    countryName = countryDf['country_region'].iloc[0]
    i=0
    # Plot by category
    for cat in categories:
        isNoSubRegion1 = countryDf['sub_region_1'] != countryDf['sub_region_1']  # filter only country non-region data
        countryData = countryDf[isNoSubRegion1]
        if shouldGroupWeek:
            countryData = groupByWeek(countryData)
        x = countryData.date
        y = countryData[cat]

        # rolling average:
        y = y.rolling(window=rollingMeanWindowSize).mean()
        label = '{} - {}'.format(countryName, cat)
        if cat == allCategories[5]:
            label += ' (time spent at)'
        else:
            label += ' (visitors)'
        ax.plot(x, y, label=label, linewidth=1)
        if shouldGroupWeek:
            ax.plot(x, y, 'C{}o'.format(i), alpha=0.5)  # plot dots on lines
        i+=1

    plt.title('Changes in presence (from baseline) for {}'.format(countryName))

# set category to plot here:
category = allCategories[2]

[countryDf, subRegions1, subRegions2] = getCountryData('Israel')

# Main plots to run: (should choose one)
# plotByRegions(countryDf, subRegions1, subRegions2, category, False) # plot districts
# plotByRegions(countryDf, subRegions1, subRegions2, category, True) # plot cities
plotCountryDataByCategories(countryDf, False, [allCategories[5]]) # plot by category
annotate(ax, [-80, -85])

plt.xlabel('Date')
plt.ylabel('Change in presence')
# plt.ylim(-100, 100)

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.grid(True)
fig.autofmt_xdate()
plt.show()
