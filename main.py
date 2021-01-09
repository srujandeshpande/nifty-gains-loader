from nsetools import Nse
import pytz
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

nse = Nse()

with open('holidays.txt') as f:
    holidays = f.readlines()

ist = pytz.timezone("Asia/Calcutta")
curr = datetime.now(ist).strftime("%Y-%m-%d")

#Checking if it is a holiday
for i in holidays:
    if(i[:-1] == curr):
        exit()

with open('nifty50.txt') as f:
    nifty50 = f.readlines()

for j in nifty50:
    ticker = j.strip()
    quote = nse.get_quote(ticker)
    print(quote['pChange'])

quote = nse.get_index_quote('NIFTY 50')
print(quote)


cred = credentials.Certificate('./firestore-access.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

