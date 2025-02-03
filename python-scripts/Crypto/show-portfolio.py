import coinswitchapi
import json
import sys
from tabulate import tabulate
from decimal import * 
from datetime import datetime

sys.set_int_max_str_digits(10002)

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
def printhr():           print(strYellow("|".rjust(150,"-")))

def print_header(portfolioname="",datetime=0,invested=0,curvalue=0,profitloss=0,profitlossper=0):
    portfolio_name = strPurple(portfolioname.rjust(75))
    print(portfolio_name)
    printhr()
    
    if(Decimal(profitloss) > 0):
        profitloss = strGreen(profitloss)
        profitlossper = strGreen(profitlossper)
    else:
        profitloss = strRed(profitloss)
        profitlossper = strRed(profitlossper)
        
    header_string = strLightPurple(" Date Time:") + strBold(datetime) \
                    + strLightPurple(" Invested:") + strBold(invested + " \u20B9") \
                    + strLightPurple(" Current Value:") + strBold(curvalue + " \u20B9") \
                    + strLightPurple(" Profit/Loss:") + strBold(profitloss + " \u20B9") \
                    + strLightPurple(" Profit/Loss %:") + strBold(profitlossper)
    print(header_string)

def color_code(value):
    if int(value) < 1:
        return strRed(value)
    elif int(value) > 1:
        return strGreen(value)
    else:
        return value

  
if __name__ == '__main__': 
    
    portfolio_data = coinswitchapi.getPortfolio()
    portfolio_json = json.loads(portfolio_data.text)
    
    invested = 0.0
    curvalue = 0.0 
    profitloss = 0.0
    profitlossper = 0.0  
    data_array = []
    data_array_header = ['NAME','CODE','UNITS','BUY-AVG-PRICE \u20B9','INVESTMENT-VALUE \u20B9','CURR-PRICE \u20B9','CURRENT-VALUE \u20B9','PROFIT-LOSS \u20B9','PROFIT-LOSS-%']
    for item in portfolio_json['data']: 
        profit_loss = Decimal(item["current_value"]) - Decimal(item["invested_value"]) 
        profit_loss_per = 100 - (Decimal(item["current_value"]) * 100)/Decimal(item["invested_value"])
        
        if(profit_loss > 0):
            profit_loss = strGreen(profit_loss)
            profit_loss_per = strGreen(profit_loss_per)
        else:
            profit_loss = strRed(profit_loss)
            profit_loss_per = strRed(profit_loss_per)
        
        if(item["currency"] == "INR"):
            invested = Decimal(item["invested_value"])
            curvalue = Decimal(item["current_value"])
            profitloss = curvalue - invested
            profitlossper = 100 - (curvalue*100)/invested
            
            invested = f'{invested:.2f}'
            curvalue = f'{curvalue:.2f}'
            profitloss = f'{profitloss:.2f}'
            profitlossper = f'{profitlossper:.2f}'
        else:
            row_data = [item["name"],
                        item["currency"],
                        item["main_balance"],
                        Decimal(item["buy_average_price"]),
                        Decimal(item["invested_value"]),
                        item["sell_rate"],
                        Decimal(item["current_value"]),
                        profit_loss,
                        profit_loss_per                  
                    ]
                
            data_array.append(row_data)
            data_array = sorted(data_array, key=lambda name: name[1])
    

    # Printing Data On Screen
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
    print('\033c')
    printhr()
    print_header("CoinSwitch Portfolio", dt_string, invested, curvalue, profitloss, profitlossper)
    printhr()
    print(tabulate(data_array, headers=data_array_header, floatfmt=".6f", tablefmt="simple"))
    printhr()