import matplotlib
import datetime
from pandas.tseries.offsets import DateOffset

from annotations import annotateEndLockdown2, annotate
from colors import getColorByIndex
from dataHandling.googleMobilityData import getCountryData, allCategories, groupByWeek, google_source_text

matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

# global style
matplotlib.rcParams['axes.titlesize'] = 16
matplotlib.rcParams['axes.labelsize'] = 12

fig, ax = plt.subplots()
# ax.xaxis.set_major_locator(months)
# ax.xaxis.set_minor_locator(days)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

rollingMeanWindowSize = 7

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
# plotRegularTimeline(countryDf, allCategories, subRegions1, subRegions2, category)
plot1st2ndLockdownComparison(countryDf, [allCategories[5]])

plt.ylabel('Change in presence')
# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="large")

plt.grid(True)
plt.show()
