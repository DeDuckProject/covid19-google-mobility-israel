import pandas as pd
import datetime as dt
import os

reproduction_coeff = 'data-non-ignore/results_unnormalized_out.csv'
reproductionDf = pd.read_csv(reproduction_coeff)

dateFetched = dt.datetime.fromtimestamp(os.path.getmtime(reproduction_coeff)).strftime("%d/%m/%y")
repro_source_text = 'Rt Calculation by Asaf Peer.\nhttps://github.com/asafpr/covid-model Accessed: {}'.format(
    dateFetched)

def getReproductionDf():
    return reproductionDf