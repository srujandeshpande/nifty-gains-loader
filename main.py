import requests
import pytz
from datetime import datetime

with open('holidays.txt') as f:
    holidays = f.readlines()

ist = pytz.timezone("Asia/Calcutta")
curr = datetime.now(ist).strftime("%Y-%m-%d")

#Checking if it is a holiday
for i in holidays:
    if(i[:-1] == curr):
        pass
    else:
        exit()

nifty50_url = 'https://www.nseindia.com/api/equity-stockIndices?csv=true&index=NIFTY%2050'

nifty50_data = requests.get(nifty50_url)
open('nifty50_data.csv', 'wb').write(nifty50_data.content)


