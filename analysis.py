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

with open(path+"holidays.txt") as f:
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
cred = credentials.Certificate(path+"firestore-access.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# Individual Quotes
with open(path+"nifty50.txt") as f:
    nifty50 = f.readlines()

stock_p = {}

for i in nifty50:
    ticker = i.strip()
    doc = db.collection(ticker).document(curr).get().to_dict()
    stock_p[ticker] = float(doc['pChange'])

sorted_p = sorted(stock_p.items(), key=lambda x: x[1], reverse=True)
print(sorted_p)

nifty50_doc = db.collection('NIFTY50').document(curr).get().to_dict()
nifty50_p = float(nifty50_doc['pChange'])

def nifty50_filter(p):
    global nifty50_p
    if nifty50_p > p[1]:
        return 0
    else:
        return 1

filtered_p = list(filter(nifty50_filter, sorted_p))
print(filtered_p)

content = curr+" Max gainers\n"
for i in filtered_p:
    content += i[0]+ " "+ str(i[1]) + "%\n"

content += "NIFTY 50 " + str(nifty50_p) + "%\n"

if len(filtered_p) < 10:
    for i in range(len(filtered_p),(10-len(filtered_p))):
        content += sorted_p[i][0]+ " "+ str(sorted_p[i][1]) + "%\n"

url = os.getenv("DISCORD_HOOK")
myobj = {"content": content}
x = requests.post(url, data = myobj)
