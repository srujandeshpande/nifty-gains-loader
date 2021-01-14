from nsetools import Nse
import pytz
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import sys

path = sys.argv[0][:-7]

nse = Nse()

with open(path + "holidays.txt") as f:
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
cred = credentials.Certificate(path + "firestore-access.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# Individual Quotes
with open(path + "nifty50.txt") as f:
    nifty50 = f.readlines()

doc = db.collection("meta").document("dates").get()
if doc.exists:
    data = doc.to_dict()
    if len(data["dates"]) < 5:
        if curr in data["dates"]:
            exit()
        data["dates"].append(curr)
    else:
        drop = data["dates"][0]
        for i in range(4):
            data["dates"][i] = data["dates"][i + 1]
        data["dates"][4] = curr
        for k in nifty50:
            ticker = k.strip()
            db.collection(ticker).document(drop).delete()
        db.collection("NIFTY50").document(drop).delete()
else:
    data = {"dates": [curr]}
db.collection("meta").document("dates").set(data)


# Nifty Quote
for j in nifty50:
    ticker = j.strip()
    quote = nse.get_quote(ticker)
    data = {
        "open": quote["open"],
        "close": quote["closePrice"],
        "pChange": quote["pChange"],
        "date": curr,
    }
    db.collection(ticker).document(curr).set(data)

quote = nse.get_index_quote("NIFTY 50")
data = {
    "lastPrice": quote["lastPrice"],
    "change": quote["change"],
    "pChange": quote["pChange"],
    "date": curr,
}
db.collection("NIFTY50").document(curr).set(data)
