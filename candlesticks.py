import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import sys
import pytz
from datetime import datetime
import requests
from dotenv import load_dotenv
import os

load_dotenv()

path = sys.argv[0][:-11]


# Firestore
cred = credentials.Certificate(path + "firestore-access.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

data_doc = db.collection("meta").document("dates").get().to_dict()
dates = data_doc["dates"]


nifty50_p = (nifty50_close - nifty50_open) / nifty50_open

print(nifty50_p, nifty50_close, nifty50_open)

# Individual Quotes
with open(path + "data/nifty500.txt") as f:
    nifty50 = f.readlines()

stock_p = {}

for i in nifty50:
    ticker = i.strip()
    open_val = float(db.collection(ticker).document(dates[0]).get().to_dict()["open"])
    close_val = float(
        db.collection(ticker).document(dates[-1]).get().to_dict()["close"]
    )
    p_val = (close_val - open_val) / open_val
    if p_val > nifty50_p:
        stock_p[ticker] = float(p_val)

sorted_p = sorted(stock_p.items(), key=lambda x: x[1], reverse=True)
print(sorted_p)

# nifty50_doc = db.collection("NIFTY50").document(dates[-1]).get().to_dict()
# nifty50_p = float(nifty50_doc["pChange"])


# def nifty50_filter(p):
#     global nifty50_p
#     if nifty50_p > p[1]:
#         return 0
#     else:
#         return 1


# filtered_p = list(filter(nifty50_filter, sorted_p))
# print(filtered_p)

content = ""
content += "Date Range: " + str(dates[0]) + " to " + str(dates[-1]) + " \n"
content += "NIFTY 50 " + str(nifty50_p) + "%\n\n"

for i in sorted_p:
    content += i[0] + " " + str(i[1]) + "%\n"

# content += curr + " Max gainers\n"
# for i in sorted_p:
#     content += i[0] + " " + str(i[1]) + "%\n"

# if len(filtered_p) < 10:
#     for i in range(len(filtered_p), (10 - len(filtered_p))):
#         content += sorted_p[i][0] + " " + str(sorted_p[i][1]) + "%\n"

print(content)

url = os.getenv("DISCORD_HOOK")
myobj = {"content": content}
x = requests.post(url, data=myobj)
