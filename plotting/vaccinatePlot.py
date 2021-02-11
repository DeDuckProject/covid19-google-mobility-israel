import matplotlib
from pandas.tseries.offsets import DateOffset
import pandas as pd
import numpy as np
from annotations import annotateVaccines
from colors import getColorForAge
from dataHandling.vaccinatedData import getVaccinatedData, getPopulationForAgeGroup, datagov_source_text_vaccinated, \
    getTotalPopulation

matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

# global style
plt.style.use('Solarize_Light2')
matplotlib.rcParams['axes.titlesize'] = 16
matplotlib.rcParams['axes.labelsize'] = 12

fig, ax = plt.subplots()

rollingMeanWindowSize = 7

def plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, firstOrSecond, accum = True, percent = True, area = False, offset = False, gradient = False, rollingAverage = False):
    if percent:
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        plt.ylim(0, 100)
        title = 'Israel - Vaccinated percent from age group'
    else:
        title = 'Israel - Vaccinated individuals by age group'

    if firstOrSecond == 1:
        title += '(first dose)'
    else:
        title += '(second dose)'

    plt.title(title)

    yStacks = []
    i=0
    for ageGroup in age_groups:
        def is_all_group():
            return ageGroup=='all'
        if is_all_group():
            onlyAgeGroup = vaccinatedData.groupby([pd.Grouper(key='date', freq='D')])[
                'first_dose', 'second_dose'].sum().reset_index().sort_values(
                'date')
            # onlyAgeGroup = vaccinatedData[vaccinatedData['age_group'] == ageGroup]
        else:
            onlyAgeGroup = vaccinatedData[vaccinatedData['age_group'] == ageGroup]
        if (offset):
            onlyAgeGroup['date'] = onlyAgeGroup['date'] + DateOffset(days=-21)
            onlyAgeGroup = onlyAgeGroup.iloc[21:]
            lineStyle = 'dashed'
        else:
            lineStyle = 'solid'

        if firstOrSecond==1:
            key = 'first_dose'
        else:
            key = 'second_dose'

        label = "{} ({})".format(ageGroup, key)

        if (accum):
            onlyAgeGroup['first_dose'] = onlyAgeGroup['first_dose'].cumsum()
            onlyAgeGroup['second_dose'] = onlyAgeGroup['second_dose'].cumsum()
        if (gradient):
            onlyAgeGroup['first_dose'] = onlyAgeGroup['first_dose'].diff().fillna(0)
            onlyAgeGroup['second_dose'] = onlyAgeGroup['second_dose'].diff().fillna(0)

        x = onlyAgeGroup['date']
        y = onlyAgeGroup[key]
        if (firstOrSecond == 'both'):
            onlyAgeGroup['second_dose'] = onlyAgeGroup['second_dose'].shift(-21)
            y = (onlyAgeGroup['second_dose'] / onlyAgeGroup['first_dose']) * 100
            label=ageGroup
        else:
            if percent:
                if is_all_group():
                    y = (y / getTotalPopulation()) * 100
                else:
                    y = (y / getPopulationForAgeGroup(ageGroup)) * 100

        if (rollingAverage):
            y = y.rolling(window=rollingMeanWindowSize).mean()
        if not area:
            age = getColorForAge(i) if not is_all_group() else 'k'
            ax.plot(x, y, label=label, linewidth=1.5, color=age, linestyle=lineStyle)
        yStacks.append(y)
        i+=1

    colors = [getColorForAge(x) for x in range(9)]
    if area:
        ax.stackplot(x, yStacks, labels=age_groups, colors=colors)
    plt.xlabel('Date')
    plt.ylabel('Vaccinated for age group')

def plot_both_doses():
    age_groups.append('all')
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, True, True, False)
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, True, True, False, True)
    plt.title('Israel - Vaccinated percent from age group (both doses)')
    annotateVaccines(ax, [95, 5])

def plot_both_doses_diff():
    age_groups.append('all')
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 'both')
    plt.title('Israel - percent taken 2nd dose')

def plot_one_dose():
    age_groups.append('all')
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1)
    # plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2)
    annotateVaccines(ax, [95, 5])

def plot_one_dose_gradient():
    age_groups.append('all')
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, accum=False, percent=False, rollingAverage=True, gradient=True)
    # plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, accum=False, percent=False, rollingAverage=True)
    annotateVaccines(ax, [15000, 5])

def plot_area_graphs():
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, False, False, True)
    # plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, False, False, True)
    annotateVaccines(ax, [150000, 5])
[vaccinatedData, age_groups] = getVaccinatedData()

# plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, False, False, True)
# plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, False, False, True)

# plot_one_dose()
plot_both_doses()
# plot_both_doses_diff()
# plot_one_dose_gradient()
# plot_area_graphs()

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="large")
plt.figtext(0.2, 0.05, datagov_source_text_vaccinated, ha="center")

plt.grid(True)
plt.show()
