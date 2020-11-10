import pandas as pd
import datetime as dt
import os
from enum import Enum

useTestsDataInsteadOfTested = True # If this is true, the plots will be based upon total tests and NOT tested individuals (affects tests plot, and positive rate plot)

class MetricToChooseTowns(Enum):
    HIGHEST_ACCUMULATED_CASES_NOT_NORMALIZED = 1
    HIGHEST_WEEKLY_INCREASE_IN_POSITIVITY_RATE = 2
    HIGHEST_WEEKLY_PCT_CHANGE_IN_POSITIVITY_RATE = 3
    HIGHEST_WEEKLY_INCREASE_IN_CASES = 4

class MetricToPlot(Enum):
    TESTS = 1
    CASES = 2
    POSITIVE_RATE = 3
    HOSPITALIZED = 4

# Read population data:
populationData = pd.read_csv('../data-non-ignore/64edd0ee-3d5d-43ce-8562-c336c24dbc1f.csv', encoding='hebrew')
populationData = populationData.filter(items=['סמל_ישוב', 'סהכ'])\
    .rename(columns={'סמל_ישוב': 'City_Code', 'סהכ': 'total_population'})

def getPopulationByCityCode(cityCode):
    filterByCityCode = populationData['City_Code'] == cityCode
    population = populationData[filterByCityCode].total_population
    if (population.size > 0):
        return population.iloc[0]
    else:
        return 1 # Workaround. some town don't have population data

# IMPORTANT: before running the script make sure you download the dataset and place in /data:
if useTestsDataInsteadOfTested:
    # https://data.gov.il/dataset/covid-19/resource/8a21d39d-91e3-40db-aca1-f73f7ab1df69/download/corona_city_table_ver_008.csv
    main_csv_filename = '../data/corona_city_table_ver_008.csv'
    mohTestsByLoc = pd.read_csv(main_csv_filename)
    mohTestsByLoc = mohTestsByLoc.rename(columns={'Date': 'date', 'City_Name': 'town', 'Cumulative_verified_cases': 'accumulated_cases',
                          'Cumulated_number_of_tests': 'accumulated_tested'})
    israelDataCsv = mohTestsByLoc.filter(
        items=['date', 'town', 'City_Code', 'accumulated_tested', 'accumulated_cases'])
    israelDataCsv['accumulated_hospitalized'] = 0 # dummy. no hospitalizations here
else:
    # Haven't used this or maintained
    # https://data.gov.il/dataset/f54e79b2-3e6b-4b65-a857-f93e47997d9c/resource/d07c0771-01a8-43b2-96cc-c6154e7fa9bd/download/geographic-summary-per-day-2020-10-14.csv
    main_csv_filename = '../data-non-ignore/geographic-summary-per-day-2020-10-14.csv'
    mohTestsByLoc = pd.read_csv(main_csv_filename)
    # filter data:
    israelDataCsv = mohTestsByLoc.filter(
        items=['date', 'town', 'town_code', 'agas_code', 'accumulated_tested', 'accumulated_cases',
               'accumulated_hospitalized'])

dateFetched = dt.datetime.fromtimestamp(os.path.getmtime(main_csv_filename)).strftime("%d/%m/%y")
datagov_source_text = 'Israel covid-19 dataset.\nhttps://data.gov.il/dataset/covid-19 Accessed: {}'.format(
    dateFetched)

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

def getMohDf(filterDates = True):
    dateFilter = israelDataCsv['date'] > dt.datetime(2020, 8, 2)  # Starting from 2.8 since its a sunday, and groupby will work better
    if filterDates:
        return israelDataCsv[dateFilter]
    else:
        return israelDataCsv

def getCompleteTownList():
    return towns

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
            if (byWhichMetric == MetricToChooseTowns.HIGHEST_WEEKLY_INCREASE_IN_POSITIVITY_RATE or byWhichMetric == MetricToChooseTowns.HIGHEST_WEEKLY_PCT_CHANGE_IN_POSITIVITY_RATE):
                townData.accumulated_cases = townData.accumulated_cases.diff().fillna(0)
                townData.accumulated_tested = townData.accumulated_tested.diff().fillna(0)
                townData = groupByWeek(townData)
                new_cases = townData.accumulated_cases
                new_tests = townData.accumulated_tested
                y = (new_cases / new_tests) * 100
                if byWhichMetric == MetricToChooseTowns.HIGHEST_WEEKLY_PCT_CHANGE_IN_POSITIVITY_RATE:
                    y = y.pct_change().fillna(0)
                else:
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

def groupByWeek(df):
    df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
    df = df.groupby([pd.Grouper(key='date', freq='W-SUN')])['accumulated_tested', 'accumulated_cases', 'accumulated_hospitalized'].sum().reset_index().sort_values('date')
    return df