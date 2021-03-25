import pandas as pd
import datetime as dt
import os

populationFrom2019 = False
populationLatest2021 = True
deductRecovered = False

# IMPORTANT: before running the script make sure you download the dataset and place in /data:
# https://data.gov.il/dataset/f54e79b2-3e6b-4b65-a857-f93e47997d9c/resource/57410611-936c-49a6-ac3c-838171055b1f/download/vaccinated-per-day-2021-03-23.csv
main_csv_filename = '../data/vaccinated-per-day-2021-03-23.csv'
israelVaccinatedData = pd.read_csv(main_csv_filename)
israelVaccinatedData = israelVaccinatedData.rename(columns={'VaccinationDate': 'date'})

dateFetched = dt.datetime.fromtimestamp(os.path.getmtime(main_csv_filename)).strftime("%d/%m/%y")
datagov_source_text_vaccinated = 'Israel covid-19 dataset.\nhttps://data.gov.il/dataset/covid-19 Accessed: {}ֿ'.format(
    dateFetched)
if populationFrom2019:
    datagov_source_text_vaccinated += '\n*0-19 percent vaccinated calculated out of population of 16-19.'

# Get rid of '<15' values:
israelVaccinatedData['first_dose'] = israelVaccinatedData['first_dose'].replace(to_replace=r'^<15$', value='15', regex=True).astype(int)
israelVaccinatedData['second_dose'] = israelVaccinatedData['second_dose'].replace(to_replace=r'^<15$', value='0', regex=True).astype(int)
israelVaccinatedData.date = pd.to_datetime(israelVaccinatedData.date) # translate string date to date

if populationFrom2019:
    age_groups = ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
    # Population per age from https://www.cbs.gov.il/he/publications/doclib/2020/2.shnatonpopulation/st02_03.pdf :
    popForAgeThousand = [3263.9, 1267.5, 1179.6, 1068.8, 824.4, 729.5, 450.5, 219.6, 50.1]
    population16to19 = 566.2
    population10to19 = 1488
else:
    age_groups = ['16-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
    if populationLatest2021:
        # Source https://twitter.com/MaytalYasur/status/1365227269808136194
        popForAgeThousand = [591, 1318, 1206, 1111, 875, 749, 531, 308]
        recoveringForAgeThousand = [68, 125, 92, 75, 53, 31, 14, 7]
    else:
        # Source Weizman institute https://twitter.com/segal_eran/status/1362766210673303552?s=20
        popForAgeThousand = [574, 1278, 1186, 1081, 833, 735, 462, 274]
        recoveringForAgeThousand = [64, 121, 88, 73, 52, 30, 14, 7]


def getPopulationForAgeGroup(age_group, dontIncludeCantvaccinate=True, deductRecovered = deductRecovered):
    if age_group=='0-19' and dontIncludeCantvaccinate:
        inThousands = population16to19
    else:
        inThousands = popForAgeThousand[age_groups.index(age_group)]
    if deductRecovered:
        inThousands = inThousands - recoveringForAgeThousand[age_groups.index(age_group)]

    return inThousands * 1000

def getTotalPopulation(deductRecovered = deductRecovered):
    total = sum(popForAgeThousand)
    if deductRecovered:
        total -= sum(recoveringForAgeThousand)
    return total * 1000

def getVaccinatedData():
    return [israelVaccinatedData, age_groups]