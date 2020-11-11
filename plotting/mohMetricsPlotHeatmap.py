import matplotlib
import pandas as pd
import datetime as dt
import numpy as np

from annotations import annotate, annotateEndLockdown2
from colors import getColorByIndex, getTrafficLightCmap
from dataHandling.mohData import MetricToPlot, MetricToChooseTowns, datagov_source_text, useTestsDataInsteadOfTested, \
    getMohDf, getCompleteTownList, getPopulationByCityCode, populationData, getTownsBy, groupByWeek

matplotlib.use('TkAgg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Date formatting for X-axis
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator() # every day

# global style
matplotlib.rcParams['axes.titlesize'] = 16
# matplotlib.rcParams['axes.labelsize'] = 12

israelDataCsv = getMohDf(False)
# israelDataCsv = groupByWeek(israelDataCsv)
towns = getCompleteTownList()

rollingMeanWindowSize = 7

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    # cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    # cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     # textcolors=["black", "black"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts

fig, ax = plt.subplots()

def plotHeatMap(towns):
    filterByTowns = israelDataCsv[israelDataCsv['town'].isin(towns)]
    filterByTowns = filterByTowns[filterByTowns['date'] > dt.datetime(2020, 3, 15)]  # Starting from 15.3 since its a sunday, and groupby will work better
    filterByTowns = filterByTowns.filter(
        items=['date', 'town', 'accumulated_tested', 'accumulated_cases'])
    heatMapArray = []
    for town in towns:
        filterByTown = filterByTowns[filterByTowns['town'] == town]
        filterByTown.accumulated_cases = filterByTown.accumulated_cases.diff().fillna(0)
        filterByTown.accumulated_tested = filterByTown.accumulated_tested.diff().fillna(0)
        filterByTown = groupByWeek(filterByTown, True)
        listOfDates = filterByTown['date'].unique()
        new_cases = filterByTown.accumulated_cases
        new_tests = filterByTown.accumulated_tested
        y = (new_cases / new_tests) * 100
        heatMapArray.append(y.fillna(0).to_numpy())

    heatmapNpArray = np.array(heatMapArray)
    townLabels = [(lambda x: x[::-1])(x) for x in towns]
    listOfDates = [(lambda x: pd.to_datetime(str(x)).strftime("%d/%m"))(x) for x in listOfDates]
    # colorMap = "YlGn"
    # colorMap = "Wistia"
    # colorMap = "YlOrRd"
    colorMap = getTrafficLightCmap()
    # colorMap = "BuGn"
    im = heatmap(heatmapNpArray, townLabels, listOfDates, ax=ax,
                 cmap=colorMap, cbarlabel="pct pos. / tests")
    texts = annotate_heatmap(im, valfmt="{x:.1f}")

    fig.tight_layout()
    plt.title('Positive % by week')
    plt.show()

numOfTownsToPlot = 25
# Main plots to run: (should choose one)
# townsToShow = getTownsBy(numOfTownsToPlot, MetricToChooseTowns.HIGHEST_ACCUMULATED_CASES_NOT_NORMALIZED)
# townsToShow = getTownsBy(numOfTownsToPlot, MetricToChooseTowns.HIGHEST_WEEKLY_INCREASE_IN_POSITIVITY_RATE, 10000)
# townsToShow = getTownsBy(numOfTownsToPlot, MetricToChooseTowns.HIGHEST_WEEKLY_PCT_CHANGE_IN_POSITIVITY_RATE, 10000)
townsToShow = getTownsBy(numOfTownsToPlot, MetricToChooseTowns.HIGHEST_WEEKLY_INCREASE_IN_CASES)

plotHeatMap(townsToShow)
# plt.xlabel('Date')
# plt.ylim(0)
# plt.figtext(0.2, 0.1, datagov_source_text, ha="center")
#
# # Put a legend to the right of the current axis
# plt.subplots_adjust(right=0.75)
# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="x-large")

# plt.grid(True)
# fig.autofmt_xdate()
