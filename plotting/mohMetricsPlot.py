import matplotlib

from annotations import annotate, annotateEndLockdown2
from colors import getColorByIndex
from dataHandling.mohData import MetricToPlot, MetricToChooseTowns, datagov_source_text, useTestsDataInsteadOfTested, \
    getMohDf, getCompleteTownList, getPopulationByCityCode, populationData, getTownsBy, groupByWeek

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

israelDataCsv = getMohDf()
towns = getCompleteTownList()

rollingMeanWindowSize = 7

fig, ax = plt.subplots()

def plotByTown(towns, which, shouldGroup=False, shouldNormalize=False, shouldPlotCountry = True):
    per_capita = 1000
    column=''
    if shouldGroup:
        prefix = 'Weekly'
        suffix_title = ' - weekly (for week starting at...)*'
        plt.figtext(0.8, 0.1, "*data for last week may be incomplete.", ha="center")
    else:
        prefix = 'Daily'
        suffix_title = ' - daily'
    if which == MetricToPlot.TESTS:
        column = 'accumulated_tested'
        if useTestsDataInsteadOfTested:
            testString = 'Tests'
        else:
            testString = 'tested individuals'
        title = '{} per town'.format(testString) + suffix_title
        ylabel = '{} number of {}'.format(prefix, testString)
    else:
        if which == MetricToPlot.CASES:
            column = 'accumulated_cases'
            title = 'Cases per town' + suffix_title
            ylabel = '{} number of cases'.format(prefix)
        else:
            if which == MetricToPlot.HOSPITALIZED:
                column = 'accumulated_hospitalized'
                title = 'Hospitalized per town' + suffix_title
                ylabel = '{} number of hospitalizations'.format(prefix)
            else:
                ax.yaxis.set_major_formatter(mtick.PercentFormatter())
                title = 'Positivity rate per town' + suffix_title
                ylabel = '{} positive rate'.format(prefix)
    if shouldNormalize:
        ylabel += ' per {} people'.format(per_capita)
        title += ' per capita'
    i = 0
    # Plot by category
    for town in towns:
        isCurrentTown = israelDataCsv['town'] == town  # filter only current town
        townData = israelDataCsv[isCurrentTown]
        townTotalPopulation = getPopulationByCityCode(townData.City_Code.iloc[0])
        plotMetricForLocation(townData, which, column, i, per_capita, shouldGroup, shouldNormalize, town, townTotalPopulation)
        i += 1

    if shouldPlotCountry:
        # plt country avg:
        countryData = israelDataCsv.groupby(['date']).agg(
            {'accumulated_tested': 'sum', 'accumulated_cases': 'sum', 'accumulated_hospitalized': 'sum'}).reset_index()
        countryPopulation = populationData['total_population'].sum()
        plotMetricForLocation(countryData, which, column, i, per_capita, shouldGroup, shouldNormalize, 'ישראל',
                              countryPopulation, 'k--')

    plt.title(title)
    plt.ylabel(ylabel)


def plotMetricForLocation(locationData, which, column, i, per_capita, shouldGroup, shouldNormalize, locationName, population, plotStyle=''):
    color = getColorByIndex(i) if plotStyle == '' else '#000000'
    locationData.accumulated_cases = locationData.accumulated_cases.diff().fillna(0)
    locationData.accumulated_tested = locationData.accumulated_tested.diff().fillna(0)
    locationData.accumulated_hospitalized = locationData.accumulated_hospitalized.diff().fillna(0)
    if shouldGroup:
        locationData = groupByWeek(locationData)
    x = locationData.date
    if which == MetricToPlot.POSITIVE_RATE:
        new_cases = locationData.accumulated_cases
        new_tests = locationData.accumulated_tested
        y = (new_cases / new_tests) * 100
    else:
        y = locationData[column]
        if shouldNormalize:
            y = y * (per_capita / population)
    # rolling average:
    if not shouldGroup:
        y = y.rolling(window=rollingMeanWindowSize).mean()
    label = locationName[::-1]
    ax.plot(x, y, plotStyle, label=label, linewidth=1, color=color)
    if shouldGroup:
        ax.plot(x, y, 'o', alpha=0.5, color=color)  # plot dots on lines

# Main plots to run: (should choose one)
townsToShow = getTownsBy(10, MetricToChooseTowns.HIGHEST_ACCUMULATED_CASES_NOT_NORMALIZED)
# townsToShow = getTownsBy(10, MetricToChooseTowns.HIGHEST_WEEKLY_INCREASE_IN_POSITIVITY_RATE, 10000)
# townsToShow = getTownsBy(10, MetricToChooseTowns.HIGHEST_WEEKLY_PCT_CHANGE_IN_POSITIVITY_RATE, 10000)
# townsToShow = getTownsBy(10, MetricToChooseTowns.HIGHEST_WEEKLY_INCREASE_IN_CASES)
# townsToShow = ['בני ברק', 'מודיעין עילית', 'אלעד', 'ביתר עילית', 'עמנואל'] # temp list to check
shouldNormalize = True
shouldPlotCountry = True

plotByTown(townsToShow, MetricToPlot.CASES, False, shouldNormalize=shouldNormalize, shouldPlotCountry=shouldPlotCountry) # plot new cases
# plotByTown(townsToShow, MetricToPlot.TESTS, False, shouldNormalize=shouldNormalize, shouldPlotCountry=shouldPlotCountry) # plot new tests
# plotByTown(townsToShow, MetricToPlot.HOSPITALIZED, True, shouldNormalize=shouldNormalize, shouldPlotCountry=shouldPlotCountry) # plot new hospitalized
# plotByTown(townsToShow, MetricToPlot.POSITIVE_RATE, False, shouldPlotCountry=shouldPlotCountry) # plot positive rate - daily (very inaccurate)
# plotByTown(townsToShow, MetricToPlot.POSITIVE_RATE, True, shouldPlotCountry=shouldPlotCountry) # plot positive rate - weekly
annotate(ax, [10, 10])
annotateEndLockdown2(ax, [10, 10])

plt.xlabel('Date')
plt.ylim(0)
plt.figtext(0.2, 0.1, datagov_source_text, ha="center")

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="x-large")

plt.grid(True)
fig.autofmt_xdate()
plt.show()
