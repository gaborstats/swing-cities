from requests import get
from bs4 import BeautifulSoup
import pandas as pd
 
# orszag, fovaros, pop adatokat gyujteni
#df = table2
df = pd.read_csv('cities-geodata.csv', sep = ";", decimal = ".")
df = df.rename(columns={'city': 'varos'})
df.varos = [x.lower() for x in df.varos]  
df["tagok"] = 0
df["csoport"] = ""
df["leiras"] = ""
#df = df.iloc[0:2]
df.head()

# varos alapjan fb adatokat kinyerni
# kezelni a hianyzo adatokats
# terkep megoldas: geoadatok szerzese, terkep csomag


# 0. varosra kereses:
def varosra_keres(city = "budapest"):
    headers = {'User-Agent':'Chrome 83 (Toshiba; Intel(R) Core(TM) i3-2367M CPU @ 1.40 GHz)'\
           'Windows 7 Home Premium',
           'Accept':'text/html,application/xhtml+xml,application/xml;'\
           'q=0.9,image/webp,*/*;q=0.8'}
    fb = "facebook public group west coast swing members"
    keyword = fb + " " + city
    url = "https://google.com/search?q="+keyword
    raw = get(url, timeout = 3, headers=headers).text
    soup = BeautifulSoup(raw, 'html.parser')
    return soup

# 1. mentsuk el a fb csop cimet


def csop_nev(soup = "soup"):
    import re
    kod = "BNeawe vvjwJb AP7Wnd"
    soup_csop = soup.find_all("div", {'class':kod})
    
    fb_csoportok = []
    for i in soup_csop:
        nev = i.get_text()
        
        nev = re.sub(r'[^\w\s]','',nev) # strip punctuation: remove everything except words and space 
        nev = re.sub(r'\_','',nev) # remove underscore as well
        
        fb_csoportok.append(nev.lower())
    return fb_csoportok

# 2. mentsuk el a csop leirasokat

def csop_leiras(soup = "soup"):
    
    kod = "BNeawe s3v9rd AP7Wnd"
    soup_szoveg = soup.find_all('div', {'class':kod})
    szoveg = []
    for m in soup_szoveg:
         szoveg.append(m.get_text())   
    from collections import OrderedDict
    szoveg = list(OrderedDict.fromkeys(szoveg))  # remove duplicates    
    szoveg = [x.lower() for x in szoveg]
    return szoveg


# 3. egyesitsuk a csoportneveket a leirasokkal
def nev_es_leiras(x = "fb_csoportok", y = "szoveg"):
    dat = pd.DataFrame(list(zip(x, y)), columns=["csop", "leiras"])
    return dat


# 4. hol szerep a leirasban a "members" es nevben a city?
def df_frissitese(dat = "dat", city = "city"):
    import numpy as np
    import re
    # helyes talalat kivalasztasa
    for g in range(0,len(dat.leiras)):
        if ("members" in dat.leiras[g]) and (city in dat.csop[g]):
            helyes_leiras = (dat.leiras[g])
            helyes_csop = (dat.csop[g])
            #print(re.findall(r'\d+', dat.leiras[g]))
            try:
                uj_tag = (re.findall(r'\d+', dat.leiras[g]))
                uj_tag = int(uj_tag[0])
                break
            except:
                uj_tag = np.nan
                
        else:
            helyes_leiras = np.nan
            helyes_csop = np.nan
            uj_tag = np.nan
        
    # store results in df
    df.set_index('varos', inplace=True)
    df.loc[city,'tagok']=uj_tag
    df.loc[city,'csoport']=helyes_csop
    df.loc[city,'leiras']=helyes_leiras
    df.reset_index('varos', drop = False, inplace=True)
    
    return df


# 5. osszesito fuggveny 

def scrape_members(df = "df"):
    k = 1
    for city in df["varos"]:
        print(str(k) + ". " + city)
        soup = varosra_keres(city = city)
        fb_csoportok = csop_nev(soup = soup)
        szoveg = csop_leiras(soup = soup)
        dat = nev_es_leiras(x = fb_csoportok, y = szoveg)
        df_friss = df_frissitese(dat = dat, city = city)
        k += 1
    return df_friss


df_friss = scrape_members(df = df)

df_ment = df_friss[['varos','pop', 'tagok', 'latitude', 'longitude']]
df_ment.loc[:,"tagok"] = df_ment.loc[:,"tagok"].fillna(0.0).astype(int) # legyenek a tagszamok integerek
df_ment.loc[:,'varos'] = df_ment.loc[:,'varos'].str.title() # big capital letter for cities

#import os
#os.getcwd()
df_ment.to_csv(r"C:\Users\Gabor\Documents\03_Programming\04_Projects\01_WCS-cities\\WCS-members.csv", index=False, sep = ";")
