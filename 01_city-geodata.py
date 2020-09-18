import re
import wikipedia
from requests import get
from bs4 import BeautifulSoup

# check string for spec character
def check_punctuation(tag = "lat1"):
    try:
        p = re.search("\.", tag).start()
        tag = tag[:p]
    except:
        pass
    return tag

# function 1: check geodata string length
def check_int_length(string = "lat1"):
    string = check_punctuation(tag = string)     
    if len(string)<1:
        string2 = string.zfill(2)
    elif len(string)<2:
        string2 = string.zfill(2)
    elif len(string)>2:
        string2 = string[0:2]
    else:
        string2 = string
    return string2

# function 2: clean geodata
def clean_geodata(rawstring = "rawstring"):
   
    result = re.search("°", rawstring)
    j = result.start()
    lat1 = (rawstring[:j])
    lat1 = check_int_length(string = lat1)
    
    result2 = re.search("′", rawstring)
    k = result2.start()
    lat2 = (rawstring[j+1:k])
    lat2 = check_int_length(string = lat2)
    
    try:
        result3 = re.search("″", rawstring)
        l = result3.start()
        lat3 = (rawstring[k+1:l])
        lat3 = check_int_length(string = lat3)
    except:
        lat3 = "00"        
    
    lat_str = lat1 + lat2 + lat3
    lat_dec = (lat_str[0:2] + "." + lat_str[2:])
    lat_int = float(lat_dec)   
    return lat_int

# get list of cities with pop data
import pandas as pd
url = "https://en.wikipedia.org/wiki/List_of_cities_in_the_European_Union_by_population_within_city_limits"
table = pd.read_html(url)[1]
table = table.drop(['Reference', 'Photography', 'Date of census'], axis=1)
#table = table.drop([5,6])
table = table.iloc[0:2]

headers = {'User-Agent':'Chrome 83 (Toshiba; Intel(R) Core(TM) i3-2367M CPU @ 1.40 GHz)'\
       'Windows 7 Home Premium',
       'Accept':'text/html,application/xhtml+xml,application/xml;'\
       'q=0.9,image/webp,*/*;q=0.8'}

    
#latitude = {}
#longitude = {}
# function 3: get geodata for cities
def get_city_geodata(df = "df"):
    latitude = {}
    longitude = {}
    for i in range(len(df)):
        print(str(i) + ". " + df.City.iloc[i])
        wikipedia.set_lang("en")
        city = wikipedia.page(df.City.iloc[i] + ", " + df["Member State"].iloc[i]) 
        raw = get(city.url, timeout = 1, headers=headers).text
        soup = BeautifulSoup(raw, 'html.parser')
        # ha tobb van, akkor a hosszabbat valassza ki (pl. Naples)
        lat = soup.find("span", class_ = 'latitude').text
        lon = soup.find("span", class_ = 'longitude').text
        lat_f = clean_geodata(lat)
        lon_f = clean_geodata(lon)
        latitude.update({df.City.iloc[i]: lat_f})
        longitude.update({df.City.iloc[i]: lon_f})
    df['Latitude'] = df['City'].map(latitude)
    df['Longitude'] = df['City'].map(longitude)
    return df

table2 = get_city_geodata(df = table)

# some cleaning
table2 = table2.rename(columns={'Officialpopulation': 'pop', 'Member State': 'orszag', 'City': 'varos'})
table2.columns = [x.lower() for x in table2.columns]
df.varos = [x.lower() for x in df.varos]

#table2.to_csv(r"C:\Users\Gabor\Documents\03_Programming\04_Projects\01_WCS-cities\\cities-geodata.csv", 
 #               index=False, sep = ";", decimal = ",")
