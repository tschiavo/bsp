import pytz

from datetime import datetime, timedelta

from pytz import timezone

eastern = timezone('US/Eastern')
utc = timezone('UTC')

utc_dt = utc.localize(datetime(2014, 10, 13, 0, 52, 13))

loc_dt = utc_dt.astimezone(eastern)


print str(utc_dt)
print str(loc_dt)
