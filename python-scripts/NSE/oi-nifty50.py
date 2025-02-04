import aiohttp
import asyncio
import requests
import json
import math
import time
from tabulate import tabulate
from datetime import datetime

def strRed(skk):         return "\033[91m {}\033[00m".format(skk)
def strGreen(skk):       return "\033[92m {}\033[00m".format(skk)
def strYellow(skk):      return "\033[93m {}\033[00m".format(skk)
def strLightPurple(skk): return "\033[94m {}\033[00m".format(skk)
def strPurple(skk):      return "\033[95m {}\033[00m".format(skk)
def strCyan(skk):        return "\033[96m {}\033[00m".format(skk)
def strLightGray(skk):   return "\033[97m {}\033[00m".format(skk)
def strBlack(skk):       return "\033[98m {}\033[00m".format(skk)
def strBold(skk):        return "\033[1m {}\033[00m".format(skk)

def round_nearest(x, num=50): return int(math.ceil(float(x)/num)*num)
def nearest_strike_bnf(x): return round_nearest(x, 100)
def nearest_strike_nf(x): return round_nearest(x, 50)

url_oc      = "https://www.nseindia.com/option-chain"
url_bnf     = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
url_nf      = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
url_indices = "https://www.nseindia.com/api/allIndices"

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8',
    'accept-encoding': 'gzip, deflate, br'
}

cookies = dict()

# Showing Header in structured format with Last Price and Nearest Strike
def print_header(index="",currprice=0,nearest=0,nf_open=0,nf_high=0,nf_low=0,expiry_date=None):
    if(currprice > nf_open):
        currprice = strGreen(str(currprice))
    else:
        currprice = strRed(str(currprice))
        
    header_string = strPurple( index + " => ") \
                    + strLightPurple(" Expiry Date:") + strBold(expiry_date) \
                    + strLightPurple(" Nearest Strike:") + strBold(str(nearest)) \
                    + strLightPurple(" Last Price:") + strBold(currprice) \
                    + strLightPurple(" Today Open:") + strBold(str(nf_open)) \
                    + strLightPurple(" Today Low:") + strBold(strRed(str(nf_low))) \
                    + strLightPurple(" Today High:") + strBold(strGreen(str(nf_high)))
    print(header_string)

def print_hr():
    print(strYellow("|".rjust(155,"-")))

def color_code(value):
    if int(value) < 1:
        return strRed(value)
    elif int(value) > 1:
        return strGreen(value)
    else:
        return value

def analysePCR(pcr):    
    returnMSG = None
    if (pcr > 4):
        returnMSG = strGreen("Extreamly Bullish")
    elif (4 > pcr > 1):
        returnMSG = strGreen("Bullish")
    elif (pcr == 1):
        returnMSG = strYellow("Sideways")
    elif (1 > pcr > 0.4):
        returnMSG = strRed("Bearish")
    elif (0.4 > pcr):
        returnMSG = strRed("Extreamly Bearish")
    
    return returnMSG  

def set_cookie():
    sess = requests.Session()
    request = sess.get(url_oc, headers=headers, timeout=5)
    return dict(request.cookies)

async def get_data(url, session):
    global cookies
    async with session.get(url, headers=headers, timeout=5, cookies=cookies) as response:
        if response.status == 401:
            cookies = set_cookie()
            async with session.get(url, headers=headers, timeout=5, cookies=cookies) as response:
                return await response.text()
        elif response.status == 200:
            return await response.text()
        return ""

async def fetch_all_data():
    async with aiohttp.ClientSession() as session:
        indices_data = await get_data(url_indices, session)
        bnf_data = await get_data(url_bnf, session)
        nf_data = await get_data(url_nf, session)
    return indices_data, bnf_data, nf_data

# Process the fetched data
def process_indices_data(data):
    global bnf_ul, nf_ul, bnf_nearest, nf_nearest, nf_open, nf_high, nf_low, bnf_open, bnf_high, bnf_low
    data = json.loads(data)    
    for index in data["data"]:
        if index["index"] == "NIFTY 50":
            nf_ul = index["last"]
            nf_open = index["open"] 
            nf_high = index["high"]
            nf_low = index["low"]
        if index["index"] == "NIFTY BANK":
            bnf_ul = index["last"]
            bnf_open = index["open"] 
            bnf_high = index["high"]
            bnf_low = index["low"]            
    bnf_nearest = nearest_strike_bnf(bnf_ul)
    nf_nearest = nearest_strike_nf(nf_ul)    

def process_oi_data(data, nearest, step, num):
    global expiryDate
    data = json.loads(data)
    currExpiryDate = data["records"]["expiryDates"][0]  
    expiryDate = data["records"]["expiryDates"][0]  
    oi_data = []
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if nearest - step*num <= item["strikePrice"] <= nearest + step*num:
                oi_data.append((
                    item["strikePrice"], 
                    item["CE"]["openInterest"], 
                    item["PE"]["openInterest"], 
                    item["CE"]["impliedVolatility"], 
                    item["PE"]["impliedVolatility"], 
                    item["CE"]["lastPrice"],
                    item["PE"]["lastPrice"],
                    item["CE"]["changeinOpenInterest"],
                    item["PE"]["changeinOpenInterest"]
                ))
    return oi_data

def print_oi_data(index_name, index_data, previous_data=None):    
    # set_header(url_indices)
    print('\033c')
    print_hr()
    print_header(index_name, nf_ul, nf_nearest, nf_open, nf_high, nf_low, expiryDate)
    print_hr()
    
    # print(nifty_data)
    
    data_array = []
    data_array_header = ['CE-OI','CE-CHANGE-OI','CE-IV','CE-LTP','PCR-OI','STRIKE-PRICE','PCR-COI','PE-LTP','PE-IV','PE-CHANGE-OI','PE-OI','CONCLUSION']
    
    for i, (strike, ce_oi, pe_oi, ce_iv, pe_iv, ce_lp, pe_lp, ce_cioi, pe_cioi) in enumerate(index_data):
        pcrvalue_coi = 0 
        if(int(ce_cioi) == 0):
            pcrvalue_coi = 0
        else:
            pcrvalue_coi = round(pe_cioi/ce_cioi,2)
            
        pcrvalue_oi = 0
        if(int(ce_oi) == 0):
            pcrvalue_oi = 0
        else:
            pcrvalue_oi = round(pe_oi/ce_oi,2)  
        
        row_data = [
                ce_oi,
                color_code(ce_cioi),
                ce_iv,
                ce_lp,
                str(pcrvalue_oi),
                strike,
                str(pcrvalue_coi),
                pe_lp,
                pe_iv,
                color_code(pe_cioi),
                pe_oi,
                analysePCR(pcrvalue_coi)
            ]
        
        data_array.append(row_data)

    print(tabulate(data_array, headers=data_array_header))      
        
    print_hr()    

def calculate_support_resistance(oi_data):
    highest_oi_ce = max(oi_data, key=lambda x: x[1])
    highest_oi_pe = max(oi_data, key=lambda x: x[2])
    return highest_oi_ce[0], highest_oi_pe[0]

async def update_data():
    global cookies
    prev_nifty_data = None
    while True:
        cookies = set_cookie()
        indices_data, bnf_data, nf_data = await fetch_all_data()

        process_indices_data(indices_data)

        nifty_oi_data = process_oi_data(nf_data, nf_nearest, 50, 10)
        support_nifty, resistance_nifty = calculate_support_resistance(nifty_oi_data)

        print(strBold(strCyan(f"\nMajor Support and Resistance Levels:")))
        print(f"Nifty Support: {strYellow(support_nifty)}, Nifty Resistance: {strYellow(resistance_nifty)}")

        print_oi_data("Nifty 50", nifty_oi_data, prev_nifty_data)

        prev_nifty_data = nifty_oi_data

        for i in range(30, 0, -1):
            print(strBold(strLightGray(f"\rFetching data in {i} seconds...")), end="")
            time.sleep(1)
        print(strBold(strCyan("\nFetching new data... Please wait.")))
        await asyncio.sleep(1)
    
async def main():
    await update_data()

asyncio.run(main())