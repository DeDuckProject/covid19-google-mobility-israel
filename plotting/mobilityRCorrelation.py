import matplotlib
import pandas as pd
import numpy as np
from scipy import stats
from colors import getColorByIndex
from dataHandling.googleMobilityData import getCountryData, allCategories
from dataHandling.reproductionCalculation import getReproductionDf

matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

reproductionDf = getReproductionDf()
[countryDf, subRegions1, subRegions2] = getCountryData('Israel')

# reproductionDf['date'] = reproductionDf['date'].apply(lambda x: time.mktime(dt.datetime.strptime(x, "%Y-%m-%d").timetuple()))
countryDf['date'] = countryDf['date'].apply(lambda x: x.strftime("%Y-%m-%d"))

rollingMeanWindowSize = 7
fig, ax = plt.subplots()

ax.xaxis.set_major_locator(months)
ax.xaxis.set_minor_locator(days)

def processData(countryDf, reproductionDf):
    isNoSubRegion1 = countryDf['sub_region_1'] != countryDf['sub_region_1']  # filter only country non-region data
    countryData = countryDf[isNoSubRegion1]

    cols = list(countryData.columns.values)
    cols[0], cols[1] = cols[1], cols[0]
    countryData = countryData[cols]
    mergedDf = countryData.set_index('date').join(reproductionDf.set_index('date'), lsuffix='_country',
                                                  rsuffix='_repro', how='inner')
    mergedDf = mergedDf.drop(columns=['sub_region_1', 'sub_region_2', 'country_region'])
    mergedDf['median_gradient'] = np.gradient(mergedDf['median'])
    for category in allCategories:
        mergedDf['{}_gradient'.format(category)] = np.gradient(mergedDf[category])

    df_corr = pd.DataFrame()  # Correlation matrix
    df_p = pd.DataFrame()  # Matrix of p-values
    for x in mergedDf.columns:
        for y in mergedDf.columns:
            corr = stats.pearsonr(mergedDf[x], mergedDf[y])
            df_corr.loc[x, y] = corr[0]
            df_p.loc[x, y] = corr[1]

    print(df_corr)
    print(df_p)

    return [mergedDf, df_corr, df_p]

def calculateCorrelation(mergedDf, category):
    mergedDfFirstWave = mergedDf[mergedDf._get_index_resolvers()['date'] < '2020-06-15']
    sorted = mergedDfFirstWave.sort_values(category)
    # Plot:
    x = sorted[category]
    y = sorted['median']

    # 2deg fit
    px = np.polyfit(x, y, 2)
    return np.poly1d(px)

def plotCorrelation(mergedDf, corrDf, pDf, category):
    sorted = mergedDf.sort_values(category)
    # Plot:
    x = sorted[category]
    y = sorted['median']

    label = '{}'.format(category)
    ax.plot(x, y, 'o', label=label)
    # 1deg fit
    # m, b = np.polyfit(x, y, 1)
    # ax.plot(x, m * x + b, '-')

    # 2deg fit
    px = np.polyfit(x, y, 3)
    p = np.poly1d(px)
    ax.plot(x, p(x), '-')
    plt.xlabel('Change in presence')
    plt.ylabel('Rt')

    plt.title('Correlation between Rt and {}'.format(category))

def plotTimeseries(mergedDf, category):
    yLabel = 'Rt'
    # Plot:
    x = mergedDf._get_index_resolvers()['date']
    y = mergedDf['median']
    # presence_transposed = (mergedDf[category])# / 20 + 3

    ax.plot(x, y, label='source R')
    # ax.plot(x, mergedDf[category], label=category)
    # y += ' / Change in presence {}'.format(category)

    plt.xlabel('Date')
    plt.ylabel(yLabel)

    plt.title('Correlation between Rt and {}'.format(category))
    fig.autofmt_xdate()

def projectR(mergedDf, category, p):
    # mergedDf = mergedDf[mergedDf._get_index_resolvers()['date'] >= '2020-06-15'] # Filter projection
    x = mergedDf._get_index_resolvers()['date']
    y = p(mergedDf[category].rolling(window=rollingMeanWindowSize).mean())
    # y = y.rolling(window=rollingMeanWindowSize).mean()
    ax.plot(x, y, label='projection')
    plt.title('Predicting Rt from "{}" data'.format(category))

chosenCategory = allCategories[3]
[mergedDf, corrDf, pDf] = processData(countryDf,reproductionDf)
# plotCorrelation(mergedDf, corrDf, pDf, chosenCategory)
# plotTimeseries(mergedDf,chosenCategory)

# Try to preditct 2nd wave with 1st wave curve fit:
curveFit = calculateCorrelation(mergedDf, chosenCategory)
plotTimeseries(mergedDf,chosenCategory)
projectR(mergedDf, chosenCategory, curveFit)

# Put a legend to the right of the current axis
plt.subplots_adjust(right=0.75)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="large")

plt.grid(True)
plt.show()
