import pandas as pd
import datetime as dt
import os

# Read population data:


# IMPORTANT: before running the script make sure you download the dataset and place in /data:
# https://data.gov.il/dataset/f54e79b2-3e6b-4b65-a857-f93e47997d9c/resource/57410611-936c-49a6-ac3c-838171055b1f/download/vaccinated-per-day-2021-02-13.csv
main_csv_filename = '../data/vaccinated-per-day-2021-02-13.csv'
israelVaccinatedData = pd.read_csv(main_csv_filename)
israelVaccinatedData = israelVaccinatedData.rename(columns={'VaccinationDate': 'date'})

dateFetched = dt.datetime.fromtimestamp(os.path.getmtime(main_csv_filename)).strftime("%d/%m/%y")
datagov_source_text_vaccinated = 'Israel covid-19 dataset.\nhttps://data.gov.il/dataset/covid-19 Accessed: {}'.format(
    dateFetched)

# Get rid of '<15' values:
israelVaccinatedData['first_dose'] = israelVaccinatedData['first_dose'].replace(to_replace=r'^<15$', value='15', regex=True).astype(int)
israelVaccinatedData['second_dose'] = israelVaccinatedData['second_dose'].replace(to_replace=r'^<15$', value='0', regex=True).astype(int)
israelVaccinatedData.date = pd.to_datetime(israelVaccinatedData.date) # translate string date to date

age_groups = ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
# Population per age from https://www.cbs.gov.il/he/publications/doclib/2020/2.shnatonpopulation/st02_03.pdf :
popForAgeThousand = [3263.9, 1267.5, 1179.6, 1068.8, 824.4, 729.5, 450.5, 219.6, 50.1]

def getPopulationForAgeGroup(age_group):
    return popForAgeThousand[age_groups.index(age_group)] * 1000

def getTotalPopulation():
    return sum(popForAgeThousand) * 1000

def getVaccinatedData():
    return [israelVaccinatedData, age_groups]