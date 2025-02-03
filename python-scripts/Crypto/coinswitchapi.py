import os
import requests
import json
import time
import logging
import auth.CoinSwitchAPIAuth
from urllib.parse import urlparse, urlencode, unquote_plus
from cryptography.hazmat.primitives.asymmetric import ed25519

logging.basicConfig(level=logging.INFO)

API_AUTH_DICT = auth.CoinSwitchAPIAuth.API_AUTH
BASE_URL = "https://coinswitch.co"

def printJSONPretty(response_text):
    response_json = json.loads(response_text.text)
    print(json.dumps(response_json, indent=4))
    
def validateKey():
    params = {}
    endpoint = "/trade/api/v2/validate/keys"
    method = "GET"
    payload = {}

    secret_key = API_AUTH_DICT.get("API_SECRET")
    
    unquote_endpoint = endpoint
    if method == "GET" and len(params) != 0:
        endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
        unquote_endpoint = unquote_plus(endpoint)

    signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)

    request_string = bytes(signature_msg, 'utf-8')
    secret_key_bytes = bytes.fromhex(secret_key)
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
    signature_bytes = secret_key.sign(request_string)
    signature = signature_bytes.hex()

    final_url = BASE_URL + endpoint

    headers_local = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': API_AUTH_DICT.get("API_KEY")
    }

    final_url = BASE_URL + endpoint
    print("final_url =>",final_url)
    response = requests.request("GET", final_url, headers=headers_local, json=payload)
    
    return response  
        
def testConnection():    
    endpoint = "/trade/api/v2/ping"
    
    final_url = BASE_URL + endpoint
    print("final_url =>",final_url)
    
    response = requests.request("GET", final_url)
    
    return response

def makeApiCall(method, endpoint, payload={}, params={}):
    secret_key = API_AUTH_DICT.get("API_SECRET")
    
    unquote_endpoint = endpoint
    if method == "GET" and len(params) != 0:
        endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
        unquote_endpoint = unquote_plus(endpoint)

    signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)
    request_string = bytes(signature_msg, 'utf-8')
    secret_key_bytes = bytes.fromhex(secret_key)
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
    signature_bytes = secret_key.sign(request_string)
    signature = signature_bytes.hex()
    
    final_url = BASE_URL + endpoint

    headers_local = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': API_AUTH_DICT.get("API_KEY")
    }    
    
    response = requests.request("GET", final_url, headers=headers_local, json=payload) 

    return response    

def getActiveCoins(exchange):
    endpoint = "/trade/api/v2/coins"
    params = {
        "exchange": exchange,
    }
    payload = {}
    
    response = makeApiCall('GET', endpoint, payload, params)
    printJSONPretty(response)
    
    return response    

def getAllTickers(exchange):
    endpoint = "/trade/api/v2/24hr/all-pairs/ticker"    
    params = {
        "exchange": exchange,
    }
    payload = {}
    
    response = makeApiCall('GET', endpoint, payload, params)
    printJSONPretty(response)
    
    return response   
    
def getCoinTicker(exchange, symbol):
    endpoint = "/trade/api/v2/24hr/ticker"    
    params = {
        "exchange": exchange,
        "symbol": symbol
    }
    payload = {}
    
    response = makeApiCall('GET', endpoint, payload, params)
    printJSONPretty(response)
    
    return response   
    
    
def getPortfolio(): 
    endpoint = "/trade/api/v2/user/portfolio"    
    payload = {}
    params = {}
    
    response = makeApiCall('GET', endpoint, payload, params)
    printJSONPretty(response)
    
    return response                


if __name__ == '__main__': 
   
    conTest = testConnection()    
    printJSONPretty(conTest)
    
    # keyValidate = validateKey()    
    
    # activeCoins = getActiveCoins("coinswitchx")
        
    # allTickers = getAllTickers("coinswitchx")
        
    # coinTicker = getCoinTicker("coinswitchx","BTC/INR")
            
    # myPortfolio = getPortfolio()
        
    