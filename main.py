import pandas as pd
from pandas.tseries.offsets import DateOffset
import ssl
import os
import datetime
import matplotlib
import numpy as np

from annotations import annotate, annotateEndLockdown2
from colors import getColorByIndex

matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Flags:
shouldRemoveWeekends = True

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

# global style
matplotlib.rcParams['axes.titlesize'] = 16
matplotlib.rcParams['axes.labelsize'] = 12

#fixing ssl issue with url fetching from https
ssl._create_default_https_context = ssl._create_unverified_context

#get new data from google - comment this out to disable downloading every time
google_mobilty_pickle_filename = 'Global_Mobility_Report.pkl'
# googleMobilityCsv = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv')
# googleMobilityCsv.to_pickle(google_mobilty_pickle_filename)

#load downloaded csv from local cache - un-comment this to use the already downloaded data

googleMobilityCsv = pd.read_pickle(google_mobilty_pickle_filename)
dateFetched = datetime.datetime.fromtimestamp(os.path.getmtime(google_mobilty_pickle_filename)).strftime("%d/%m/%y")
google_source_text = 'Google LLC "Google COVID-19 Community Mobility Reports".\nhttps://www.google.com/covid19/mobility/ Accessed: {}'.format(
    dateFetched)

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
        notSunday = countryData['day_of_week'] != 6 # Remove sun if needed
        if country == 'Israel':
            countryData = countryData[notFriday & notSaturday]
        else:
            countryData = countryData[notSaturday & notSunday]

    # filter From date if needed
    # dateFilter = countryData['date'] > '2020-08-15'
    # countryData = countryData[dateFilter]

    return [countryData, subRegions1, subRegions2]

# category:      0         1          2        3          4            5
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
    countryName = countryDf['country_region'].iloc[0]
    x = countryData.date
    y = countryData[category]
    # rolling average:
    y = y.rolling(window=rollingMeanWindowSize).mean()
    ax.plot(x, y, 'k--', label='{} average'.format(countryName), linewidth=1)

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

def plotCountryDataByCategories(countryDf, shouldGroupWeek, categories, labelOverride = '', i = 0, transformDateToDaysFrom=''):
    countryName = countryDf['country_region'].iloc[0]
    # Plot by category
    for cat in categories:
        color = getColorByIndex(i)
        isNoSubRegion1 = countryDf['sub_region_1'] != countryDf['sub_region_1']  # filter only country non-region data
        countryData = countryDf[isNoSubRegion1]
        if shouldGroupWeek:
            countryData = groupByWeek(countryData)
        if transformDateToDaysFrom!='':
            countryData.date = (countryData.date - datetime.datetime.strptime(transformDateToDaysFrom, '%Y-%d-%m')).dt.days
        x = countryData.date
        y = countryData[cat]

        # rolling average:
        y = y.rolling(window=rollingMeanWindowSize).mean()
        label = '{}'.format(cat)
        if cat == allCategories[5]:
            label += ' (time)'
        else:
            label += ' (visitors)'
        label += labelOverride
        ax.plot(x, y, label=label, linewidth=1, color=color)
        if shouldGroupWeek:
            ax.plot(x, y, 'C{}o'.format(i), alpha=0.5, color=color)  # plot dots on lines
        i+=1

    plt.title('Changes in presence (from baseline) for {}'.format(countryName))

def plot1st2ndLockdownComparison(countryDf, categories):
    # Compare end of 1st and 2nd lockdowns:
    countryDfDateOffset = countryDf.copy(deep=True)
    countryDfDateOffset.date = countryDfDateOffset.date + DateOffset(months=5, days=13) # 1st lockdown ended on 5.5.20. Point of reference: the removal of 100m residential limitation. https://www.calcalist.co.il/local/articles/0,7340,L-3816890,00.html
    # filtering dates of 1st and 2nd
    countryDfDateOffset = countryDfDateOffset[countryDfDateOffset['date'] < '2021-01-15']
    countryDf = countryDf[countryDf['date'] > '2020-08-01']
    ax.axvline(x=0, linestyle='solid', alpha=0.8, color='#000000')  # mark 0 point

    plotCountryDataByCategories(countryDfDateOffset, False, categories, ' 1st lockdown', i=2, transformDateToDaysFrom='2020-18-10')  # plot by category
    plotCountryDataByCategories(countryDf, False, categories, ' 2nd lockdown', i=3, transformDateToDaysFrom='2020-18-10')  # plot by category

    plt.xlim(-100, 100)
    plt.xlabel('Days from lockdown end (ease of leaving-home restriction) - 5.5, 18.10')
    plt.figtext(0.7, 0.01, google_source_text, ha="center")

def plotRegularTimeline(countryDf, categories, subRegions1, subRegions2, category):
    # Can choose plot from here as well:
    # plotByRegions(countryDf, subRegions1, subRegions2, category, False) # plot districts
    # plotByRegions(countryDf, subRegions1, subRegions2, category, True) # plot cities
    plotCountryDataByCategories(countryDf, False, categories) # plot by category

    annotate(ax, [-80, -85])
    annotateEndLockdown2(ax, [-80, -85])
    plt.xlabel('Date')
    plt.figtext(0.7, 0.1, google_source_text, ha="center")
    fig.autofmt_xdate()

# set category to plot here:
category = allCategories[5]

[countryDf, subRegions1, subRegions2] = getCountryData('Israel')

# Main plots to run: (should choose one)
plotRegularTimeline(countryDf, allCategories, subRegions1, subRegions2, category)
# plot1st2ndLockdownComparison(countryDf, [allCategories[5]])

plt.ylabel('Change in presence')
# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="large")

plt.grid(True)
plt.show()
