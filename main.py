from nsetools import Nse
import pytz
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

nse = Nse()

with open("holidays.txt") as f:
    holidays = f.readlines()

ist = pytz.timezone("Asia/Calcutta")
today = datetime.now(ist)
curr = today.strftime("%Y-%m-%d")

# Checking if it is a holiday
for i in holidays:
    if i[:-1] == curr:
        print("Holiday")
        exit()
# Checking if it is a weekend
if today.weekday() in [5, 6]:
    print("Weekend")
    exit()


# Firestore
cred = credentials.Certificate("./firestore-access.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# Individual Quotes
with open("nifty50.txt") as f:
    nifty50 = f.readlines()

# Nifty Quote
for j in nifty50:
    ticker = j.strip()
    quote = nse.get_quote(ticker)
    data = {
        "open": quote["open"],
        "close": quote["close"],
        "pChange": quote["pChange"],
        "date": curr,
    }
    db.collection(ticker).document(curr).set(data)

quote = nse.get_index_quote("NIFTY 50")
data = {
    "open": quote["open"],
    "close": quote["close"],
    "pChange": quote["pChange"],
    "date": curr,
}
db.collection("NIFTY50").document(curr).set(data)
