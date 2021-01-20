from nsetools import Nse
import pytz
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv()

path = sys.argv[0][:-7]

nse = Nse()


total = 500


def progress(count, total, status=""):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)
    sys.stdout.write("[%s] %s%s ...%s\r" % (bar, percents, "%", status))
    sys.stdout.flush()


# Read the holidays file
with open(path + "holidays.txt") as f:
    holidays = f.readlines()

# Get current date
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


# Get Individual Tickers from file
with open(path + "data/nifty500.txt") as f:
    nifty50 = f.readlines()

# Get Metadata
doc = db.collection("meta").document("dates").get()
if doc.exists:
    data = doc.to_dict()
    if curr in data["dates"]:
        exit()
    if len(data["dates"]) < 5:
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

# Init empty dict for NIFTY 500 data of that day
nifty500_data = {}

# Get Quote for each Ticker
print("Downloading Quotes for each Ticker")
n = 0
for j in nifty50:
    ticker = j.strip()
    progress(n, total, status=ticker)
    quote = nse.get_quote(ticker)
    data = {
        "open": float(quote["open"]) ) if quote["open"] else 0.0,
        "close": float(quote["closePrice"]) ) if quote["close"] else 0.0,
        "pChange": float(quote["pChange"]) if quote["pChange"] else 0.0,
        "date": curr,
    }
    nifty500_data[ticker] = data
    n += 1
    # db.collection(ticker).document(curr).set(data)
print()

# Get Index quote
quote = nse.get_index_quote("NIFTY 500")
nifty500_quote = {
    "lastPrice": quote["lastPrice"],
    "change": quote["change"],
    "pChange": quote["pChange"],
    "date": curr,
}
# Update index quote in database
db.collection("NIFTY500").document(curr).set(nifty500_quote)

# Sort the data by pChange
sorted_p = sorted(nifty500_data.items(), key=lambda x: x[1]["pChange"], reverse=True)
content = "Today's Max Gainers\n"
content += "NIFTY 500: " + str(nifty500_quote["pChange"]) + "\n\n"
for i in sorted_p[:20]:
    content += i[0] + ": " + str(i[1]["pChange"]) + "\n"

# Send Discord message
url = os.getenv("DISCORD_HOOK")
myobj = {"content": content}
x = requests.post(url, data=myobj)

# Upload data to database
print("Uploading data to database")
n = 0
for i in sorted_p:
    progress(n, total, status=i[0])
    db.collection(i[0]).document(curr).set(i[1])
    n += 1
