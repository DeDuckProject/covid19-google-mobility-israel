import datetime

# 1st lockdown started on 22.3.20. Point of reference: stay at home orders https://he.wikipedia.org/wiki/%D7%9E%D7%92%D7%A4%D7%AA_%D7%94%D7%A7%D7%95%D7%A8%D7%95%D7%A0%D7%94_%D7%91%D7%99%D7%A9%D7%A8%D7%90%D7%9C#%D7%9E%D7%A8%D7%A5_-_%D7%A1%D7%92%D7%A8_%D7%A8%D7%90%D7%A9%D7%95%D7%9F
# 3rd lockdown started on 27.12.20. Point of reference: stay at home orders
lockdownStartDaysText = '22.3.20, 18.9.20, 27.12.20'
# 1st lockdown ended on 5.5.20. Point of reference: the removal of 100m residential limitation. https://www.calcalist.co.il/local/articles/0,7340,L-3816890,00.html
# 3rd lockdown ended on 7.2.21. Point of reference: stay at home orders. Source: https://www.haaretz.co.il/health/corona/1.9517663
lockdownEndDaysText = '5.5.20, 18.10.20, 7.2.21'


lockdownStart = [datetime.date(2020,3,22),datetime.date(2020,9,18),datetime.date(2020,12,27)]
lockdownEnd = [datetime.date(2020,5,5),datetime.date(2020,10,18),datetime.date(2021,2,7)]

def getLockdownShiftInDays(fromLockdown, toLockdown, startOrEnd ='start'):
    target = lockdownStart if startOrEnd == 'start' else lockdownEnd
    res = target[fromLockdown] - target[toLockdown]
    return res.days

def getLockdownLengthInDays(whichLockdown):
    res = lockdownEnd[whichLockdown] - lockdownStart[whichLockdown]
    return res.days