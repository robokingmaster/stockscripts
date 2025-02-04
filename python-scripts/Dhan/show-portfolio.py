import time
import asyncio
import json
import logging
import auth.DhanAPIAuth
from decimal import * 
from datetime import datetime
from dhanhq import dhanhq
from tabulate import tabulate
from urllib.parse import urlparse, urlencode, unquote_plus
from cryptography.hazmat.primitives.asymmetric import ed25519

logging.basicConfig(level=logging.INFO)

API_AUTH_DICT = auth.DhanAPIAuth.API_AUTH
BASE_URL = "https://api.dhan.co"                                                                                                                                                                       

logging.info(f"Initializing Connection") 
dhan = dhanhq(API_AUTH_DICT.get("CLIENT_ID"),API_AUTH_DICT.get("ACCESS_TOKEN"))

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
def printhr():           print(strYellow("|".rjust(165,"-")))

def print_header(portfolioname="", datetime=0, invested=0, curvalue=0, profitloss=0, profitlossper=0):
    portfolio_name = strPurple(portfolioname.rjust(75))
    print(portfolio_name)
    printhr()
    
    if(Decimal(profitloss) > 0.0):
        profitloss = strGreen(profitloss)
        profitlossper = strGreen(profitlossper)
    else:
        profitloss = strRed(profitloss)
        profitlossper = strRed(profitlossper)
        
    header_string = strLightPurple(" Date Time:") + strBold(datetime) \
                    + strLightPurple(" Invested:") + strBold(str(invested) + " \u20B9") \
                    + strLightPurple(" Current Value:") + strBold(str(curvalue) + " \u20B9") \
                    + strLightPurple(" Profit/Loss:") + strBold(str(profitloss) + " \u20B9") \
                    + strLightPurple(" Profit/Loss %:") + strBold(str(profitlossper))
    print(header_string)

def color_code(value):
    if int(value) < 1:
        return strRed(value)
    elif int(value) > 1:
        return strGreen(value)
    else:
        return value

def color_text(strtext, color):
    if(color == "RED"):
        return strRed(strtext)
    elif(color == "GREEN"):
        return strGreen(strtext)
    else:
        return strtext

async def print_holdings():    
    while True:
        holdings = dhan.get_holdings()
        print(json.dumps(holdings, indent=4))
        TOTAL_INVESTMENT = 0.0
        CURRENT_VALUE = 0.0
        TOTAL_PROFIT_LOSS = 0.0
        TOTAL_PROFITLOSS_PER = 0.0
        
        data_array = []
        data_array_header = ['EXCHANGE','TRADING-SYMBOL','SYMBOL-CODE','UNITS','BUY-AVG-PRICE \u20B9','INVESTMENT \u20B9','CURR-PRICE \u20B9','CURRENT-VALUE \u20B9','PROFIT-LOSS \u20B9','PROFIT-LOSS-%']
        for item in holdings['data']: 
            invested = round(float(item["totalQty"]) * float(item["avgCostPrice"]), 2)
            curvalue = round(float(item["totalQty"]) * float(item["lastTradedPrice"]), 2)
            
            TOTAL_INVESTMENT = TOTAL_INVESTMENT + invested
            CURRENT_VALUE = CURRENT_VALUE + curvalue
            
            profit_loss = curvalue - invested
            profit_loss_per = 100 - (curvalue * 100)/invested
            
            textcolor = ""
            
            if(profit_loss > 0):                
                profit_loss_per = abs(profit_loss_per)
                textcolor = "GREEN"
            else:                
                profit_loss_per = abs(profit_loss_per)  
                textcolor = "RED"       
            
            row_data = [color_text(item["exchange"], textcolor),
                        color_text(item["tradingSymbol"], textcolor),
                        color_text(item["isin"], textcolor),
                        color_text(item["totalQty"], textcolor),
                        color_text(float(item["avgCostPrice"]), textcolor),
                        color_text(invested, textcolor),
                        color_text(float(item["lastTradedPrice"]), textcolor),
                        color_text(curvalue, textcolor),
                        color_text(profit_loss, textcolor),
                        color_text(profit_loss_per, textcolor)               
                    ]
                
            data_array.append(row_data)
            data_array = sorted(data_array, key=lambda tradingSymbol: tradingSymbol[1])
                
        TOTAL_PROFIT_LOSS = CURRENT_VALUE - TOTAL_INVESTMENT
        TOTAL_PROFITLOSS_PER = 100 - (CURRENT_VALUE * 100)/TOTAL_INVESTMENT
                        
        # Printing Data On Screen
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        
        print('\033c')
        printhr()
        print_header("Dhan Portfolio", dt_string, round(TOTAL_INVESTMENT, 2), round(CURRENT_VALUE, 2), round(TOTAL_PROFIT_LOSS, 2), round(abs(TOTAL_PROFITLOSS_PER), 2))
        printhr()
        print(tabulate(data_array, headers=data_array_header, floatfmt=".2f", tablefmt="simple"))
        printhr()
        
        for i in range(30, 0, -1):
            print(strBold(strLightGray(f"\rFetching data in {i} seconds...")), end="")
            time.sleep(1)
        print(strBold(strCyan("\nFetching new data... Please wait.")))
        await asyncio.sleep(1)
            
async def main():
    await print_holdings()

asyncio.run(main())