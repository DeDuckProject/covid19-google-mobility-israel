import matplotlib
import numpy as np
import datetime
from pandas.tseries.offsets import DateOffset

from annotations import annotateEndLockdown2, annotate
from colors import getColorByIndex
from dataHandling.vaccinatedData import getVaccinatedData, getPopulationForAgeGroup, datagov_source_text_vaccinated

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

fig, ax = plt.subplots()
# ax.xaxis.set_major_locator(months)
# ax.xaxis.set_minor_locator(days)
# ax.yaxis.set_major_formatter(mtick.PercentFormatter())

rollingMeanWindowSize = 7

def plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, firstOrSecond, accum = True, percent = True, area = False):
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
    for ageGroup in age_groups:
        onlyAgeGroup = vaccinatedData[vaccinatedData['age_group'] == ageGroup]
        if firstOrSecond==1:
            key = 'first_dose'
        else:
            key = 'second_dose'
        if (accum):
            onlyAgeGroup['first_dose_accum'] = onlyAgeGroup['first_dose'].cumsum()
            onlyAgeGroup['second_dose_accum'] = onlyAgeGroup['second_dose'].cumsum()
            key += '_accum'

        x = onlyAgeGroup['date']
        y = onlyAgeGroup[key]
        if percent:
            y = (y / getPopulationForAgeGroup(ageGroup)) * 100

        if not area:
            ax.plot(x, y, label=ageGroup, linewidth=1)
        yStacks.append(y)

    if area:
        ax.stackplot(x, yStacks, labels=age_groups)
    plt.xlabel('Date')
    plt.ylabel('Vaccinated for age group')

[vaccinatedData, age_groups] = getVaccinatedData()

plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, True, True, False)
# plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, True, True, False)

# plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, False, False, True)
# plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, False, False, True)

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="large")
plt.figtext(0.2, 0.05, datagov_source_text_vaccinated, ha="center")

plt.grid(True)
plt.show()
