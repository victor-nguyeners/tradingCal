# tradingCal
A slight change to the pandas market calendars. Shows a few different things I needed. The options days reflect dailies available, generally for QQQ/SPY,
as they have options that expire on monday/wednesdays as well.



#Usage

from tradingCal import TradingCal as tcal

#This will use today's date as the start and + 1 year
cal = tcal().build_full_calendar()

#Alternatively you can put your own dates in

cal = tcal().build_full_calendar(start='01-01-2022', end='12-31-2022')


business_days = tcal().get_business_days()
schedule = tcal().get_trading_schedule(start='01-01-2022')

