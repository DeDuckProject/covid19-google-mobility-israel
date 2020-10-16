import pandas as pd
import datetime as dt
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

# IMPORTANT: this is a big file. before running the script make sure you download it and place in the root folder:
# https://data.gov.il/dataset/f54e79b2-3e6b-4b65-a857-f93e47997d9c/resource/d07c0771-01a8-43b2-96cc-c6154e7fa9bd/download/geographic-summary-per-day-2020-10-14.csv
mohTestsByLoc = pd.read_csv('geographic-summary-per-day-2020-10-14.csv')

#filter data:
# isIsrael = mohTestsByLoc['country_region_code'] == 'IL' # filter only israel
# israelDataCsv = mohTestsByLoc[isIsrael]
israelDataCsv = mohTestsByLoc.filter(items=['date', 'town', 'town_code', 'agas_code', 'accumulated_tested', 'accumulated_cases', 'accumulated_hospitalized'])
# Get rid of '<15' values:
israelDataCsv.accumulated_tested = israelDataCsv.accumulated_tested.replace(to_replace=r'^<15$', value='15', regex=True).astype(int)
israelDataCsv.accumulated_cases = israelDataCsv.accumulated_cases.replace(to_replace=r'^<15$', value='0', regex=True).astype(int)
israelDataCsv.accumulated_hospitalized = israelDataCsv.accumulated_hospitalized.replace(to_replace=r'^<15$', value='0', regex=True).astype(int)
israelDataCsv.date = pd.to_datetime(israelDataCsv.date) # translate string date to date

# Group towns: towns are divided into sections (which are noted by agas_code). this groups them:
israelDataCsv = israelDataCsv.groupby(['town','date']).agg({'accumulated_tested': 'sum', 'accumulated_cases': 'sum', 'accumulated_hospitalized': 'sum'}).reset_index()

towns = israelDataCsv['town'].unique()

def getTownsByHighestAccumulatedCases(numOfTownsToSelect):
    selectedTowns = []
    for town in towns:
        isCurrentTown = israelDataCsv['town'] == town  # filter only current town
        townData = israelDataCsv[isCurrentTown]
        accum = townData.accumulated_cases.iloc[-1]
        selectedTowns.append((town, accum))
    towns_sorted_by_second = sorted(selectedTowns, key=lambda tup: tup[1])[::-1]
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
        suffix_title = ' - weekly (for week starting at...)'
    else:
        prefix = 'Daily'
        suffix_title = ' - daily'
    if which == 'tests':
        column = 'accumulated_tested'
        title = 'Tested per town' + suffix_title
        ylabel = '{} number of tested individuals'.format(prefix)
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

def annotate():
    # Annotate
    x_line_annotation = '2020-09-18'
    x_text_annotation = '2020-09-19'
    ax.axvline(x=x_line_annotation, linestyle='dashed', alpha=0.5, color='#6BADEF')
    ax.text(x=x_text_annotation, y=10, s='2nd lockdown', alpha=0.7, color='#000000')

# Main plots to run: (should choose one)
townsToShow = getTownsByHighestAccumulatedCases(10)
plotByTown(townsToShow, 'cases', False) # plot new cases
# plotByTown(townsToShow, 'tests', True) # plot new tests
# plotByTown(townsToShow, 'hospitalized', True) # plot new hospitalized
# plotByTown(townsToShow, 'positive-rate', False) # plot positive rate - daily (very inaccurate)
# plotByTown(townsToShow, 'positive-rate', True) # plot positive rate - weekly
annotate()

plt.xlabel('Date')
plt.ylim(0)

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.grid(True)
fig.autofmt_xdate()
plt.show()
