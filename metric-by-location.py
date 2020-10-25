import pandas as pd
import datetime as dt
import matplotlib
from enum import Enum

from annotations import annotate
from colors import getColorByIndex

matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

useTestsDataInsteadOfTested = True # If this is true, the plots will be based upon total tests and NOT tested individuals (affects tests plot, and positive rate plot)

class MetricToChooseTowns(Enum):
    HIGHEST_ACCUMULATED_CASES_NOT_NORMALIZED = 1
    HIGHEST_WEEKLY_INCREASE_IN_POSITIVITY_RATE = 2
    HIGHEST_WEEKLY_INCREASE_IN_CASES = 3

class MetricToPlot(Enum):
    TESTS = 1
    CASES = 2
    POSITIVE_RATE = 3
    HOSPITALIZED = 4

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

# Read population data:
populationData = pd.read_csv('64edd0ee-3d5d-43ce-8562-c336c24dbc1f.csv', encoding='hebrew')
populationData = populationData.filter(items=['סמל_ישוב', 'סהכ'])\
    .rename(columns={'סמל_ישוב': 'City_Code', 'סהכ': 'total_population'})

def getPopulationByCityCode(cityCode):
    filterByCityCode = populationData['City_Code'] == cityCode
    return populationData[filterByCityCode].total_population.iloc[0]

# IMPORTANT: before running the script make sure you download the dataset and place in /data:
if useTestsDataInsteadOfTested:
    # https://data.gov.il/dataset/covid-19/resource/8a21d39d-91e3-40db-aca1-f73f7ab1df69/download/corona_city_table_ver_004.csv
    mohTestsByLoc = pd.read_csv('data/corona_city_table_ver_004.csv')
    mohTestsByLoc = mohTestsByLoc.rename(columns={'Date': 'date', 'City_Name': 'town', 'Cumulative_verified_cases': 'accumulated_cases',
                          'Cumulated_number_of_tests': 'accumulated_tested'})
    israelDataCsv = mohTestsByLoc.filter(
        items=['date', 'town', 'City_Code', 'accumulated_tested', 'accumulated_cases'])
    israelDataCsv['accumulated_hospitalized'] = 0 # dummy. no hospitalizations here
else:
    # https://data.gov.il/dataset/f54e79b2-3e6b-4b65-a857-f93e47997d9c/resource/d07c0771-01a8-43b2-96cc-c6154e7fa9bd/download/geographic-summary-per-day-2020-10-14.csv
    mohTestsByLoc = pd.read_csv('data/geographic-summary-per-day-2020-10-14.csv')
    # filter data:
    israelDataCsv = mohTestsByLoc.filter(
        items=['date', 'town', 'town_code', 'agas_code', 'accumulated_tested', 'accumulated_cases',
               'accumulated_hospitalized'])

# Get rid of '<15' values:
israelDataCsv.accumulated_tested = israelDataCsv.accumulated_tested.replace(to_replace=r'^<15$', value='15', regex=True).astype(int)
israelDataCsv.accumulated_cases = israelDataCsv.accumulated_cases.replace(to_replace=r'^<15$', value='0', regex=True).astype(int)
israelDataCsv.accumulated_hospitalized = israelDataCsv.accumulated_hospitalized.replace(to_replace=r'^<15$',
                                                                                            value='0',
                                                                                            regex=True).astype(int)
israelDataCsv.date = pd.to_datetime(israelDataCsv.date) # translate string date to date

if not useTestsDataInsteadOfTested:
    # Group towns: towns are divided into sections (which are noted by agas_code). this groups them:
    israelDataCsv = israelDataCsv.groupby(['town','date']).agg({'accumulated_tested': 'sum', 'accumulated_cases': 'sum', 'accumulated_hospitalized': 'sum'}).reset_index()

towns = israelDataCsv['town'].unique()

def getTownsBy(numOfTownsToSelect, byWhichMetric, filterLowerThan=0):
    total = 0
    selectedTowns = []
    for town in towns:
        isCurrentTown = israelDataCsv['town'] == town  # filter only current town
        townData = israelDataCsv[isCurrentTown]
        if filterLowerThan > getPopulationByCityCode(townData.City_Code.iloc[0]):
            continue
        if byWhichMetric == MetricToChooseTowns.HIGHEST_ACCUMULATED_CASES_NOT_NORMALIZED:
            metric = townData['accumulated_tested'].iloc[-1]
        else:
            if byWhichMetric == MetricToChooseTowns.HIGHEST_WEEKLY_INCREASE_IN_POSITIVITY_RATE:
                townData.accumulated_cases = townData.accumulated_cases.diff().fillna(0)
                townData.accumulated_tested = townData.accumulated_tested.diff().fillna(0)
                townData = groupByWeek(townData)
                new_cases = townData.accumulated_cases
                new_tests = townData.accumulated_tested
                y = (new_cases / new_tests) * 100
                y = y.diff().fillna(0)
                metric = y.iloc[-1]
            else:
                if byWhichMetric == MetricToChooseTowns.HIGHEST_WEEKLY_INCREASE_IN_CASES:
                    townData.accumulated_cases = townData.accumulated_cases.diff().fillna(0)
                    townData = groupByWeek(townData)
                    y = townData.accumulated_cases.diff().fillna(0)
                    y = y.diff().fillna(0)
                    metric = y.iloc[-1]
        total += metric
        selectedTowns.append((town, metric))
    towns_sorted_by_second = sorted(selectedTowns, key=lambda tup: tup[1])[::-1]
    print ('total tests/tested individuals: {}'.format(total))
    return list(map(lambda x: x[0], towns_sorted_by_second[0:numOfTownsToSelect]))

# filter From date if needed
dateFilter = israelDataCsv['date'] > dt.datetime(2020, 8, 2) # Starting from 2.8 since its a sunday, and groupby will work better
israelDataCsv = israelDataCsv[dateFilter]

rollingMeanWindowSize = 7

fig, ax = plt.subplots()

def groupByWeek(df):
    df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
    df = df.groupby([pd.Grouper(key='date', freq='W-SUN')])['accumulated_tested', 'accumulated_cases', 'accumulated_hospitalized'].sum().reset_index().sort_values('date')
    return df

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

plt.xlabel('Date')
plt.ylim(0)

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="x-large")

plt.grid(True)
fig.autofmt_xdate()
plt.show()
