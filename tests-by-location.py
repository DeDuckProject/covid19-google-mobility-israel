import pandas as pd
import datetime as dt
import matplotlib

from annotations import annotate

matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

useTestsDataInsteadOfTested = True # If this is true, the plots will be based upon total tests and NOT tested individuals (affects tests plot, and positive rate plot)

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

# IMPORTANT: before running the script make sure you download the dataset and place in /data:
if useTestsDataInsteadOfTested:
    # https://data.gov.il/dataset/covid-19/resource/8a21d39d-91e3-40db-aca1-f73f7ab1df69/download/corona_city_table_ver_001.csv
    mohTestsByLoc = pd.read_csv('data/corona_city_table_ver_001.csv')
    mohTestsByLoc = mohTestsByLoc.rename(columns={'Date': 'date', 'City_Name': 'town', 'Cumulative_verified_cases': 'accumulated_cases',
                          'Cumulated_number_of_tests': 'accumulated_tested'})
    israelDataCsv = mohTestsByLoc.filter(
        items=['date', 'town', 'accumulated_tested', 'accumulated_cases'])
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

def getTownsByHighestAccumulatedCases(numOfTownsToSelect):
    total = 0
    selectedTowns = []
    for town in towns:
        isCurrentTown = israelDataCsv['town'] == town  # filter only current town
        townData = israelDataCsv[isCurrentTown]
        accum = townData.accumulated_tested.iloc[-1]
        total += accum
        selectedTowns.append((town, accum))
    towns_sorted_by_second = sorted(selectedTowns, key=lambda tup: tup[1])[::-1]
    print ('total tests/tested individuals: {}'.format(total))
    return list(map(lambda x: x[0], towns_sorted_by_second[0:numOfTownsToSelect]))

# filter From date if needed
dateFilter = israelDataCsv['date'] > dt.datetime(2020, 8, 2) # Starting from 2.8 since its a sunday, and groupby will work better
israelDataCsv = israelDataCsv[dateFilter]

rollingMeanWindowSize = 7

fig, ax = plt.subplots()

# TODO make sure works:
def groupByWeek(df):
    df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
    df = df.groupby([pd.Grouper(key='date', freq='W-SUN')])['accumulated_tested', 'accumulated_cases', 'accumulated_hospitalized'].sum().reset_index().sort_values('date')
    return df

def plotByTown(towns, which, shouldGroup):
    if shouldGroup:
        prefix = 'Weekly'
        suffix_title = ' - weekly (for week starting at...)*'
        plt.figtext(0.8, 0.1, "*data for last week may be incomplete.", ha="center")
    else:
        prefix = 'Daily'
        suffix_title = ' - daily'
    if which == 'tests':
        column = 'accumulated_tested'
        if useTestsDataInsteadOfTested:
            testString = 'Tests'
        else:
            testString = 'tested individuals'
        title = '{} per town'.format(testString) + suffix_title
        ylabel = '{} number of {}'.format(prefix, testString)
    else:
        if which == 'cases':
            column = 'accumulated_cases'
            title = 'Cases per town' + suffix_title
            ylabel = '{} number of cases'.format(prefix)
        else:
            if which == 'hospitalized':
                column = 'accumulated_hospitalized'
                title = 'Hospitalized per town' + suffix_title
                ylabel = '{} number of hospitalizations'.format(prefix)
            else:
                ax.yaxis.set_major_formatter(mtick.PercentFormatter())
                title = 'Positivity rate per town' + suffix_title
                ylabel = '{} positive rate'.format(prefix)
    i = 0
    # Plot by category
    for town in towns:
        isCurrentTown = israelDataCsv['town'] == town  # filter only current town
        townData = israelDataCsv[isCurrentTown]
        townData.accumulated_cases = townData.accumulated_cases.diff().fillna(0)
        townData.accumulated_tested = townData.accumulated_tested.diff().fillna(0)
        townData.accumulated_hospitalized = townData.accumulated_hospitalized.diff().fillna(0)
        if shouldGroup:
            townData = groupByWeek(townData)
        x = townData.date
        if which == 'positive-rate':
            new_cases = townData.accumulated_cases
            new_tests = townData.accumulated_tested
            y = (new_cases / new_tests) * 100
        else:
            y = townData[column]

        # rolling average:
        if not shouldGroup:
            y = y.rolling(window=rollingMeanWindowSize).mean()
        label = town[::-1]
        ax.plot(x, y, label=label, linewidth=1)
        if shouldGroup:
            ax.plot(x, y, 'C{}o'.format(i), alpha=0.5) # plot dots on lines
        i += 1

    plt.title(title)
    plt.ylabel(ylabel)

# Main plots to run: (should choose one)
townsToShow = getTownsByHighestAccumulatedCases(10)
# plotByTown(townsToShow, 'cases', False) # plot new cases
# plotByTown(townsToShow, 'tests', False) # plot new tests
# plotByTown(townsToShow, 'hospitalized', True) # plot new hospitalized
# plotByTown(townsToShow, 'positive-rate', False) # plot positive rate - daily (very inaccurate)
plotByTown(townsToShow, 'positive-rate', True) # plot positive rate - weekly
annotate(ax, [10, 10])

plt.xlabel('Date')
plt.ylim(0)

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.grid(True)
fig.autofmt_xdate()
plt.show()
