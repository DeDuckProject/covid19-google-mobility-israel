import matplotlib
import numpy as np
import datetime
from pandas.tseries.offsets import DateOffset

from annotations import annotateEndLockdown2, annotate
from colors import getColorByIndex
from dataHandling.googleMobilityData import getCountryData, allCategories, groupByWeek, google_source_text, signature
from dataHandling.lockdownInfo import lockdownStartDaysText, lockdownEndDaysText, getLockdownShiftInDays, \
    getLockdownLengthInDays

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

def plot_region(category, comparison, countryData, onlyRegion, subRegion):
    x = onlyRegion.date.reset_index(drop=True)
    if comparison:
        regionVal = onlyRegion[category].fillna(0).astype(np.int64).reset_index(drop=True)
        countryVal = countryData[category].fillna(0).astype(np.int64).reset_index(drop=True)
        y = regionVal - countryVal
    else:
        y = onlyRegion[category]
    # rolling average:
    y = y.rolling(window=rollingMeanWindowSize).mean()
    ax.plot(x, y, label=subRegion, linewidth=1)

def plotByRegions(countryDf, subRegions1, subRegions2, category, cities, comparison = False):
    # Plot country avg:
    isNoSubRegion1 = countryDf['sub_region_1']!=countryDf['sub_region_1'] # filter only israel non-region data
    countryData = countryDf[isNoSubRegion1]
    countryName = countryDf['country_region'].iloc[0]
    x = countryData.date
    y = countryData[category]
    # rolling average:
    y = y.rolling(window=rollingMeanWindowSize).mean()
    if not comparison:
        ax.plot(x, y, 'k--', label='{} average'.format(countryName), linewidth=1)
    else:
        ax.plot(x, y - y, 'k--', label='{} average'.format(countryName), linewidth=1)

    if not cities:
        # Plot sub-regions_1 (districts)
        for subRegion in subRegions1:
            isRegion = countryDf['sub_region_1']==subRegion
            onlyRegion = countryDf[isRegion]
            isNoSubRegion2 = countryDf['sub_region_2']!=countryDf['sub_region_2'] # remove rows with sub_region_2
            onlyRegion = onlyRegion[isNoSubRegion2]
            plot_region(category, comparison, countryData, onlyRegion, subRegion)
    else:
        # Plot sub-regions_2 (cities)
        for subRegion in subRegions2:
            isRegion = countryDf['sub_region_2']==subRegion
            onlyRegion = countryDf[isRegion]
            plot_region(category, comparison, countryData, onlyRegion, subRegion)

    title = 'Changes in presence (from baseline) for: ' + category
    if comparison:
        title += ' (difference from country avg.)'
    plt.title(title)

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
        ax.plot(x, y, label=label, linewidth=1.5, color=color)
        # ax.fill_between(x, 0, y, color=color, alpha=0.2, where=[x<getLockdownLengthInDays(i-2)])
        if shouldGroupWeek:
            ax.plot(x, y, 'C{}o'.format(i), alpha=0.5, color=color)  # plot dots on lines
        i+=1

    plt.title('Changes in presence (from baseline) for {}'.format(countryName))

def plot1st2ndLockdownComparison(countryDf, categories, compareByStart = False, shouldGroupWeek=False):
    # Compare end of 1st and 2nd lockdowns:
    countryDfDateOffset1stLockdown = countryDf.copy(deep=True)
    countryDfDateOffset3rdLockdown = countryDf.copy(deep=True)
    if compareByStart:
        title = 'Days from lockdown start (stay at home orders) - %s' % lockdownStartDaysText
        offsets = [getLockdownShiftInDays(1, 0, 'start'),-getLockdownShiftInDays(2, 1, 'start')]
    else:
        title = 'Days from lockdown end (ease of leaving-home restriction) - %s' % lockdownEndDaysText
        offsets = [getLockdownShiftInDays(1, 0, 'end'), -getLockdownShiftInDays(2, 1, 'end')]
    countryDfDateOffset1stLockdown.date = countryDfDateOffset1stLockdown.date + DateOffset(days=offsets[0])
    countryDfDateOffset3rdLockdown.date = countryDfDateOffset3rdLockdown.date + DateOffset(days=offsets[1])

    # filtering dates of 1st and 2nd
    countryDfDateOffset3rdLockdown = countryDfDateOffset3rdLockdown[countryDfDateOffset3rdLockdown['date'] > '2020-08-01']
    countryDfDateOffset1stLockdown = countryDfDateOffset1stLockdown[countryDfDateOffset1stLockdown['date'] < '2021-01-15']
    countryDf = countryDf[countryDf['date'] > '2020-08-01']

    ax.axvline(x=0, linestyle='solid', alpha=0.8, color='#000000')  # mark 0 point

    if compareByStart:
        plotCountryDataByCategories(countryDfDateOffset1stLockdown, shouldGroupWeek, categories, ' 1st lockdown', i=2, transformDateToDaysFrom='2020-18-09')
        plotCountryDataByCategories(countryDf, shouldGroupWeek, categories, ' 2nd lockdown', i=3, transformDateToDaysFrom='2020-18-09')
        plotCountryDataByCategories(countryDfDateOffset3rdLockdown, shouldGroupWeek, categories, ' 3rd lockdown', i=4, transformDateToDaysFrom='2020-18-09')

        plt.xlim(-25, 100)
    else:
        plotCountryDataByCategories(countryDfDateOffset1stLockdown, shouldGroupWeek, categories, ' 1st lockdown', i=2,
                                    transformDateToDaysFrom='2020-18-10')
        plotCountryDataByCategories(countryDf, shouldGroupWeek, categories, ' 2nd lockdown', i=3,
                                    transformDateToDaysFrom='2020-18-10')
        plotCountryDataByCategories(countryDfDateOffset3rdLockdown, shouldGroupWeek, categories, ' 3rd lockdown', i=4,
                                    transformDateToDaysFrom='2020-18-10')
        plt.xlim(-100, 100)

    drawLockdownLength(compareByStart)
    plt.xlabel(title)
    plt.figtext(0.7, 0.01, google_source_text, ha="center")
    # plt.figtext(0.2, 0.01, signature, ha="center")


def drawLockdownLength(compareByStart):
    if not compareByStart:
        multiply = -1
    else:
        multiply = 1
    ax.axvline(x=multiply*getLockdownLengthInDays(0), linestyle='dashed', alpha=0.5,
               color=getColorByIndex(2))  # mark 1st lockdown
    ax.axvline(x=multiply*getLockdownLengthInDays(1), linestyle='dashed', alpha=0.5,
               color=getColorByIndex(3))  # mark 2nd lockdown
    ax.axvline(x=multiply*getLockdownLengthInDays(2), linestyle='dashed', alpha=0.5,
               color=getColorByIndex(4))  # mark 3rd lockdown


def plotRegularTimeline(countryDf, categories, subRegions1, subRegions2, category):
    # Can choose plot from here as well:
    # plotByRegions(countryDf, subRegions1, subRegions2, category, False) # plot districts
    # plotByRegions(countryDf, subRegions1, subRegions2, category, True) # plot cities
    # plotByRegions(countryDf, subRegions1, subRegions2, category, False, True)  # plot districts - compare
    # plotByRegions(countryDf, subRegions1, subRegions2, category, True, True) # plot cities - compare
    plotCountryDataByCategories(countryDf, False, categories) # plot by category

    annotate(ax, [-80, -85])
    annotateEndLockdown2(ax, [-80, -85])
    plt.xlabel('Date')
    plt.figtext(0.7, 0.1, google_source_text, ha="center")
    # plt.figtext(0.6, 0.5, signature, ha="center")
    fig.autofmt_xdate()

# set category to plot here:
category = allCategories[5]

[countryDf, subRegions1, subRegions2] = getCountryData('Israel')

# Main plots to run: (should choose one)
# plotRegularTimeline(countryDf, allCategories, subRegions1, subRegions2, category)
plot1st2ndLockdownComparison(countryDf, [category])
# plot1st2ndLockdownComparison(countryDf, [category], True)

plt.ylabel('Change in presence')
# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="large")

plt.grid(True)
plt.show()
