import matplotlib
from pandas.tseries.offsets import DateOffset
from matplotlib import cm
from colors import getColorForAge
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
        onlyAgeGroup = vaccinatedData[vaccinatedData['age_group'] == ageGroup]
        if (offset):
            onlyAgeGroup.date = onlyAgeGroup.date + DateOffset(days=-21)
            lineStyle = 'dashed'
        else:
            lineStyle = 'solid'

        if firstOrSecond==1:
            key = 'first_dose'
        else:
            key = 'second_dose'

        label = "{} ({})".format(ageGroup, key)

        if (accum):
            onlyAgeGroup[key] = onlyAgeGroup[key].cumsum()
        if (gradient):
            onlyAgeGroup[key] = onlyAgeGroup[key].diff().fillna(0)

        x = onlyAgeGroup['date']
        y = onlyAgeGroup[key]
        if percent:
            y = (y / getPopulationForAgeGroup(ageGroup)) * 100

        if (rollingAverage):
            y = y.rolling(window=rollingMeanWindowSize).mean()
        if not area:
            ax.plot(x, y, label=label, linewidth=1.5, color=getColorForAge(i), linestyle=lineStyle)
        yStacks.append(y)
        i+=1

    if area:
        ax.stackplot(x, yStacks, labels=age_groups)
    plt.xlabel('Date')
    plt.ylabel('Vaccinated for age group')

def plot_both_doses():
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, True, True, False)
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, True, True, False, True)
    plt.title('Israel - Vaccinated percent from age group (both doses)')

def plot_one_dose():
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1)
    # plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2)

def plot_one_dose_gradient():
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, accum=False, percent=False, rollingAverage=True, gradient=True)
    # plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, accum=False, percent=False, rollingAverage=True)

def plot_area_graphs():
    plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, False, False, True)
    # plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, False, False, True)
[vaccinatedData, age_groups] = getVaccinatedData()

# plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 1, False, False, True)
# plot_vaccinated_accumulation_per_age_group(vaccinatedData, age_groups, 2, False, False, True)

# plot_one_dose()
plot_both_doses()
# plot_one_dose_gradient()
# plot_area_graphs()

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="large")
plt.figtext(0.2, 0.05, datagov_source_text_vaccinated, ha="center")

plt.grid(True)
plt.show()
