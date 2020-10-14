import pandas as pd
import ssl
import matplotlib
import urllib.request
import json
import numpy as np
matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

# IMPORTANT: this is a big file. before running the script make sure you download it and place in the root folder:
# https://data.gov.il/dataset/f54e79b2-3e6b-4b65-a857-f93e47997d9c/resource/d07c0771-01a8-43b2-96cc-c6154e7fa9bd/download/geographic-summary-per-day-2020-10-11.csv
mohTestsByLoc = pd.read_csv('geographic-summary-per-day-2020-10-11.csv')

#filter data:
# isIsrael = mohTestsByLoc['country_region_code'] == 'IL' # filter only israel
# israelDataCsv = mohTestsByLoc[isIsrael]
israelDataCsv = mohTestsByLoc.filter(items=['date', 'town', 'town_code', 'agas_code', 'accumulated_tested', 'accumulated_cases'])
israelDataCsv = israelDataCsv.replace(to_replace=r'^<15$', value='15', regex=True) # turn '<15' to 15
israelDataCsv.accumulated_tested = israelDataCsv.accumulated_tested.astype(int)
israelDataCsv.accumulated_cases = israelDataCsv.accumulated_cases.astype(int)

# print (israelDataCsv)
# list sub regions 1,2:
# townCodes = israelDataCsv['town_code'].unique()
towns = israelDataCsv['town'].unique()
towns_codes = israelDataCsv['town_code'].unique()
agas_codes = israelDataCsv['agas_code'].unique()

def getTownsByHighestAccumulatedCases(numOfTownsToSelect):
    selectedTowns = []
    # TODO this is incomplete. for each town, all agas_code sections should be aggragated and only then find out...:
    for town in towns:
        isCurrentTown = israelDataCsv['town'] == town  # filter only current town
        townData = israelDataCsv[isCurrentTown]
        accum = townData.accumulated_cases.iloc[-1]
        selectedTowns.append((town, accum))
    towns_sorted_by_second = sorted(selectedTowns, key=lambda tup: tup[1])
    return list(map(lambda x: x[0], towns_sorted_by_second[0:numOfTownsToSelect]))

# filter From date if needed
# dateFilter = israelDataCsv['date'] > '2020-08-15'
# israelDataCsv = israelDataCsv[dateFilter]

rollingMeanWindowSize = 3

fig, ax = plt.subplots()
# ax.xaxis.set_major_locator(months)
# ax.xaxis.set_minor_locator(days)
# ax.yaxis.set_major_formatter(mtick.PercentFormatter())

def plotByTown(towns):
    # Plot by category
    for town in towns:
        isCurrentTown = israelDataCsv['town'] == town  # filter only current town
        townData = israelDataCsv[isCurrentTown]
        x = townData.date
        y = townData.accumulated_tested
        y = y.diff().fillna(0)

        # rolling average:
        # y = y.rolling(window=rollingMeanWindowSize).mean()
        label = town
        ax.plot(x, y, label=label, linewidth=1)

    plt.title('Tests per town')

# Main plots to run: (should choose one)
plotByTown(getTownsByHighestAccumulatedCases(10)) # plot by category

plt.xlabel('Date')
plt.ylabel('Number of tests')
# plt.ylim(-100, 100)

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.grid(True)
fig.autofmt_xdate()
plt.show()
