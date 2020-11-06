import pandas as pd
import ssl
import os
import datetime
import numpy as np

# Flags:
shouldRemoveWeekends = True

#fixing ssl issue with url fetching from https
ssl._create_default_https_context = ssl._create_unverified_context

google_mobilty_pickle_filename = './data/Global_Mobility_Report.pkl'
#get new data from google - uncomment this to enable downloading every time
# googleMobilityCsv = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv')
# googleMobilityCsv.to_pickle(google_mobilty_pickle_filename)

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

def groupByWeek(df):
    df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
    df = df.groupby([pd.Grouper(key='date', freq='W-SUN')])['retail', 'grocery', 'parks', 'transit', 'workplace', 'residential'].mean().reset_index().sort_values('date')
    return df