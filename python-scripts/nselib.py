# Libraries
import requests
import json
import math
import time 
from tabulate import tabulate
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Urls for fetching Data
url_oc      = "https://www.nseindia.com/option-chain"
url_bnf     = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
url_nf      = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
url_indices = "https://www.nseindia.com/api/allIndices"

# Headers
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'}

data_array_header = ['TIME','CE-OI','CE-CHANGE-OI','CE-IV','CE-LTP','PCR-OI','STRIKE-PRICE','PCR-COI','PE-LTP','PE-IV','PE-CHANGE-OI','PE-OI','CONCLUSION']

# # Define the retry strategy
retry_strategy = Retry(
    total=4,  # Maximum number of retries
    status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
)

# requests.adapters.DEFAULT_RETRIES = 3
requests.adapters.max_retries = retry_strategy
sess = requests.Session()
cookies = dict()

# Python program to print
# colored text and background
def strRed(skk):         return "\033[91m {}\033[00m".format(skk)
def strGreen(skk):       return "\033[92m {}\033[00m".format(skk)
def strYellow(skk):      return "\033[93m {}\033[00m".format(skk)
def strLightPurple(skk): return "\033[94m {}\033[00m".format(skk)
def strPurple(skk):      return "\033[95m {}\033[00m".format(skk)
def strCyan(skk):        return "\033[96m {}\033[00m".format(skk)
def strLightGray(skk):   return "\033[97m {}\033[00m".format(skk)
def strBlack(skk):       return "\033[98m {}\033[00m".format(skk)
def strBold(skk):        return "\033[1m {}\033[0m".format(skk)

# Method to get nearest strikes
def round_nearest(x,num=50): return int(math.ceil(float(x)/num)*num)
def nearest_strike_bnf(x): return round_nearest(x,100)
def nearest_strike_nf(x): return round_nearest(x,50)

# Local methods
def set_cookie():
    request = sess.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)

def set_header(url_indices):
    global bnf_ul
    global nf_ul
    global bnf_nearest
    global nf_nearest
    response_text = get_data(url_indices)
    data = json.loads(response_text)
    for index in data["data"]:
        if index["index"]=="NIFTY 50":
            nf_ul = index["last"]
            print("nifty")
        if index["index"]=="NIFTY BANK":
            bnf_ul = index["last"]
            print("banknifty")
    bnf_nearest=nearest_strike_bnf(bnf_ul)
    nf_nearest=nearest_strike_nf(nf_ul)
    
def get_data(url):
    set_cookie()
    response = sess.get(url, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==401):
        set_cookie()
        response = sess.get(url_nf, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==200):
        return response.text
    return ""

# Showing Header in structured format with Last Price and Nearest Strike
def print_header(index="",ul=0,nearest=0,expiry_date=None):
    header_string = strPurple( index.ljust(12," ") + " => ") \
                    + strLightPurple(" Expiry Date: ") + strBold(expiry_date) \
                    + strLightPurple(" Last Price: ") + strBold(str(ul)) \
                    + strLightPurple(" Nearest Strike: ") + strBold(str(nearest))
    print(header_string)

def print_hr():
    print(strYellow("|".rjust(150,"-")))

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

def color_code(value):
    if int(value) < 1:
        return strRed(value)
    elif int(value) > 1:
        return strGreen(value)
    else:
        return value
    
# Fetching CE and PE data based on Nearest Expiry Date
def print_oi(num,step,nearest,url,expiry_date=None):
    current_time = datetime.now().strftime("%H:%M:%S")
    
    strike = nearest - (step*num)
    start_strike = nearest - (step*num)
    response_text = get_data(url)
    data = json.loads(response_text)
    if expiry_date is None:
        currExpiryDate = data["records"]["expiryDates"][0]
    else:
        currExpiryDate = expiry_date
    
    data_array = []
    data_array_header = ['TIME','CE-OI','CE-CHANGE-OI','CE-IV','CE-LTP','PCR-OI','STRIKE-PRICE','PCR-COI','PE-LTP','PE-IV','PE-CHANGE-OI','PE-OI','CONCLUSION']
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:            
            if item["strikePrice"] == strike and item["strikePrice"] < start_strike+(step*num*2):
                pcrvalue_coi = 0 
                if(int(item["CE"]["changeinOpenInterest"]) == 0):
                    pcrvalue_coi = 0
                else:
                    pcrvalue_coi = round(item["PE"]["changeinOpenInterest"]/item["CE"]["changeinOpenInterest"],2)
                    
                pcrvalue_oi = 0
                if(int(item["CE"]["openInterest"]) == 0):
                    pcrvalue_oi = 0
                else:
                    pcrvalue_oi = round(item["PE"]["openInterest"]/item["CE"]["openInterest"],2)  
                
                row_data = [current_time,
                            item["CE"]["openInterest"],
                            color_code(item["CE"]["changeinOpenInterest"]),
                            item["CE"]["impliedVolatility"],
                            item["CE"]["lastPrice"],
                            str(pcrvalue_oi),
                            item["strikePrice"],
                            str(pcrvalue_coi),
                            item["PE"]["lastPrice"],
                            item["PE"]["impliedVolatility"],
                            color_code(item["PE"]["changeinOpenInterest"]),
                            item["PE"]["openInterest"],
                            analysePCR(pcrvalue_coi)]
                
                data_array.append(row_data)
                strike = strike + step

    print(tabulate(data_array, headers=data_array_header))
    
# Finding highest Open Interest of People's in CE based on CE data         
def highest_oi_CE(num,step,nearest,url,expiry_date=None):
    strike = nearest - (step*num)
    start_strike = nearest - (step*num)
    response_text = get_data(url)
    data = json.loads(response_text)    
    if expiry_date is None:
        currExpiryDate = data["records"]["expiryDates"][0]
    else:
        currExpiryDate = expiry_date
            
    max_oi = 0
    max_oi_strike = 0
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if item["strikePrice"] == strike and item["strikePrice"] < start_strike+(step*num*2):
                if item["CE"]["openInterest"] > max_oi:
                    max_oi = item["CE"]["openInterest"]
                    max_oi_strike = item["strikePrice"]
                strike = strike + step
    return max_oi_strike

# Finding highest Open Interest of People's in PE based on PE data 
def highest_oi_PE(num,step,nearest,url,expiry_date=None):
    strike = nearest - (step*num)
    start_strike = nearest - (step*num)
    response_text = get_data(url)
    data = json.loads(response_text)
    if expiry_date is None:
        currExpiryDate = data["records"]["expiryDates"][0]
    else:
        currExpiryDate = expiry_date
    max_oi = 0
    max_oi_strike = 0
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if item["strikePrice"] == strike and item["strikePrice"] < start_strike+(step*num*2):
                if item["PE"]["openInterest"] > max_oi:
                    max_oi = item["PE"]["openInterest"]
                    max_oi_strike = item["strikePrice"]
                strike = strike + step
    return max_oi_strike

def print_nifty_optionchain(expiry_date=None):
    set_header(url_indices)
    print('\033c')
    print_hr()
    print_header("Nifty",nf_ul,nf_nearest,expiry_date)
    print_hr()
    print_oi(10,50,nf_nearest,url_nf,expiry_date)
    print_hr()
    
    # Finding Highest OI in Call Option In Nifty
    nf_highestoi_CE = highest_oi_CE(10,50,nf_nearest,url_nf,expiry_date)

    # Finding Highet OI in Put Option In Nifty
    nf_highestoi_PE = highest_oi_PE(10,50,nf_nearest,url_nf,expiry_date)   
    
    print(strCyan(str("Major Support in Nifty:")) + str(nf_highestoi_PE))
    print(strCyan(str("Major Resistance in Nifty:")) + str(nf_highestoi_CE)) 
    
    print()
    print(strYellow('NOTE: Please use this program after 11:00 AM for more accurecy!!'))
    
def print_banknifty_optionchain(expiry_date=None): 
    set_header(url_indices)
    print('\033c')    
    print_hr() 
    print_header("Bank Nifty",bnf_ul,bnf_nearest,expiry_date)
    print_hr()
    print_oi(10,100,bnf_nearest,url_bnf,expiry_date)
    print_hr()

    # Finding Highest OI in Call Option In Bank Nifty
    bnf_highestoi_CE = highest_oi_CE(10,100,bnf_nearest,url_bnf,expiry_date)

    # Finding Highest OI in Put Option In Bank Nifty
    bnf_highestoi_PE = highest_oi_PE(10,100,bnf_nearest,url_bnf,expiry_date)

    print(strPurple(str("Major Support in Bank Nifty:")) + str(bnf_highestoi_PE))
    print(strPurple(str("Major Resistance in Bank Nifty:")) + str(bnf_highestoi_CE))  
    
    print()
    print(strYellow('NOTE: Please use this program after 11:00 AM for more accurecy!!'))
    
# Finding PRC Value For Provided Strick Price and Expiry Date
def get_strikeprice_pcr(strike_price,url,expiry_date=None):
    current_time = datetime.now().strftime("%H:%M:%S")
    
    response_text = get_data(url)
    data = json.loads(response_text)
    
    if expiry_date is None:
        currExpiryDate = data["records"]["expiryDates"][0]
    else:
        currExpiryDate = expiry_date 
           
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:            
            if item["strikePrice"] == strike_price:                
                pcrvalue_coi = 0 
                if(int(item["CE"]["changeinOpenInterest"]) == 0):
                    pcrvalue_coi = 0
                else:
                    pcrvalue_coi = round(item["PE"]["changeinOpenInterest"]/item["CE"]["changeinOpenInterest"],2)
                    
                pcrvalue_oi = 0
                if(int(item["CE"]["openInterest"]) == 0):
                    pcrvalue_oi = 0
                else:
                    pcrvalue_oi = round(item["PE"]["openInterest"]/item["CE"]["openInterest"],2)                    
                
                row_data = [current_time,
                            item["CE"]["openInterest"],
                            color_code(item["CE"]["changeinOpenInterest"]),
                            item["CE"]["impliedVolatility"],
                            item["CE"]["lastPrice"],
                            str(pcrvalue_oi),
                            item["strikePrice"],
                            str(pcrvalue_coi),
                            item["PE"]["lastPrice"],
                            item["PE"]["impliedVolatility"],
                            color_code(item["PE"]["changeinOpenInterest"]),
                            item["PE"]["openInterest"],
                            analysePCR(pcrvalue_coi)]                
                
                return row_data
            
        