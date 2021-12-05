from m5stack import *
import urequests, network, json, machine, time
from micropython import const


p1 = machine.Pin(27)
p1.init(p1.OUT)
p1.value(1)
tcounter = 0

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
if not sta_if.isconnected():
    # Set your WiFi SSID and password here
    sta_if.connect('[WIFI_NAME]]', '[WIFI_PASSWORD]')
    while not sta_if.isconnected():
        utime.sleep(1)

lcd.clear() 
# Setting the display mode to landscape
lcd.orient(lcd.LANDSCAPE)
lcd.fill(0x000000)

symbols = []
prices = []
changes = []
currentTemp = ""
currentWind = ""
currentWeather = ""

lcd.font(lcd.FONT_DejaVu24)

#Index to iterate through coins
index = 0

def getTemp():
    global currentTemp
    global currentWind
    global currentWeather

    response = urequests.get('http://dataservice.accuweather.com/currentconditions/v1/[PLACE_KEY]?apikey=[APIKEY]&details=true')
    parsed = response.json()
    currentTemp = str(parsed[0]["RealFeelTemperature"]["Metric"]["Value"])
    currentWind = str(parsed[0]["Wind"]["Speed"]["Metric"]["Value"])
    currentWeather = parsed[0]["WeatherText"]

def getPrices():
    global symbols
    global prices
    global changes
    global finalText

    symbols = []
    prices = []
    changes = []

    url = 'https://api.nomics.com/v1/currencies/ticker?key=ad2e1abd5fbcb6de85b64d1e0a939b2bba440cf9&ids=BTC,ENJ,DOGE,SHIB&interval=1h&convert=CAD&per-page=100&page=1'
    response = urequests.get(url)
    parsed = response.json()

for item in parsed:
        symbols.append(item["name"])
        _priceString = item["price"]
        _price = float(item["price"])
        _price = round(_price, 6)
        # I want to show 6 digits after '.' if the price is smaller than 0.0009 otherwise it will show the scientific format, 4.7e-10 kind of the text
        if _price > 0.0009:
            prices.append(_price)
        else:
            prices.append('{:.6f}'.format(_price)[0:8])
        _change = float(item["1h"]["price_change_pct"])
        changes.append(_change)

def showData():
    global index

    lcd.clear()
    lcd.print(symbols[index], 10, 10, 0xFFFFFF) 
    lcd.print('CA$'+str(prices[index]), 10, 35, 0xFFFFFF)
    _percent = round(changes[index] ,4)
    _percentColor = 0x0F6608
    if _percent < 0:
        _percentColor = 0x8B1F08

    lcd.print(str(_percent)+'%', 10, 60, _percentColor)
    lcd.print('______________',10,61)
    lcd.print('T: '+currentTemp+ ', W: ' + currentWind , 10, 90, 0xEEEEEE)
    lcd.print(currentWeather, 10, 110, 0xEEEEEE)
    if index < len(symbols) - 1:
        index += 1
    else:
        index = 0    

def count(timer):
    global tcounter
    if tcounter & 1:
        p1.value(0)
    else:
        p1.value(1)
    tcounter += 1
    # Refresh display every 5 seconds
    if (tcounter % 5) == 0:
        showData()
    # Refresh price data every 10 minutes
    if (tcounter % 600) == 0:
        getPrices()
    # Refresh weather data every hour
    if (tcounter % 3600) == 0:
        tcounter = 0
        getTemp()
    
getPrices()
getTemp()
showData()

timer = machine.Timer(2)
timer.init(period=1000, mode=timer.PERIODIC, callback=count)
