from bidi.algorithm import get_display
import arabic_reshaper
import re
import datetime
import time
import sqlite3
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def persian(txt):
    converted=arabic_reshaper.reshape(txt)
    return get_display(converted)


db=sqlite3.connect("housing.db")
curs=db.cursor()
myquery='CREATE TABLE IF NOT EXISTS details (ad_id INTEGER, published_date TEXT ,'\
    'description TEXT,'\
    'price TEXT,'\
    'location TEXT,'\
    'area TEXT,'\
    'bedroomes INTEGER,'\
    'parkings INTEGER,'\
    'url TEXT,'\
    'phoneNumber TEXT,'\
    'agancy TEXT,'\
    'building_age INTEGER,'\
    'PRIMARY KEY(ad_id))'
    
    
    
curs.execute(myquery)


#ch = webdriver.Chrome(ChromeDriverManager().install())
#ch.get("https://kilid.com/buy/tehran-saadat_abad?listingTypeId=1&location=273080")

options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.maximize_window() 
driver.get("https://kilid.com/buy/tehran-saadat_abad?listingTypeId=1&location=273080")
info=driver.find_elements(By.XPATH,'//a[contains(@href,"detail")]')


cnt=0
price=list()
published_time=list()
building_age=list()
area=list()
description=list()
location=list()
building_type=list()
urls=list()
ad_id=list()
agancy=list()
parkings=list()
bedrooms=list()
phone_list=list()


while (driver):
    cnt+=1
    del info[6:9]
    time.sleep(2)
    urls=[elem.get_attribute('href')for elem in info]
    #for item in info:
        #print(item.text)
        
    for url in urls:
        #print (url)
        tempurl=url.split('/')
        ad_id.append(tempurl[-1])
    #ad_id=ad_id[:6]+ad_id[9:23]

    for item in info :
        
        temp=(persian(item.text)).split('\n')
        if len(temp)>2: 
            #price.append(re.findall('\d+\.+\d|\d+',temp[2]))  
            price.append(temp[2])                     
            published_time.append(temp[0])
            description.append(temp[1])
            location.append(temp[3])
            building_type.append(temp[4])
            area.append((temp[5].strip('ﺮﺘﻣ')))
 
            if 'ﮓﻨﯿﮐﺭﺎﭘ' in temp[6] :
                parkings.append(temp[6].strip('ﮓﻨﯿﮐﺭﺎﭘ'))           
            else:
                parkings.append("-1")
                
                
            if 'ﺏﺍﻮﺧ' in temp[7]:    
                bedrooms.append(temp[7].strip('ﺏﺍﻮﺧ'))
            else:
                bedrooms.append("-1")
            
            
    for indPrice,elemPrice in enumerate(price):
        
        tempPrice=elemPrice.split(' ')
        if len(tempPrice)>2: 
            if tempPrice[1]=='ﺩﺭﺎﯿﻠﯿﻣ': 
                price[indPrice]=(float(tempPrice[2])*1000)
            else:
                price[indPrice]=(float(tempPrice[2]))        
        else:
            price[indPrice]=-1  
            
            
                
    for ind,elemTime in enumerate(published_time):
        
        tempTime=elemTime.split(' ')
        if tempTime[1]=='ﺖﻋﺎﺳ':
            delta=datetime.timedelta(hours=int(tempTime[2]))   
        elif tempTime[1]=='روز':
            delta=datetime.timedelta(days=int(tempTime[2]))
        elif tempTime[1]=='ﻪﻘﯿﻗﺩ':
            delta=datetime.timedelta(hours=0)
        else:
            delta=datetime.timedelta(days=30)
        
        published_time[ind]=(datetime.datetime.now(datetime.UTC)-delta).strftime('%d-%m-%Y')
        
        
        
        
    for ind,elemArea in enumerate(area):
        
        tempArea=elemArea.split(' ')
        area[ind]=int(tempArea[1])




    for ind,elemBedroom in enumerate(bedrooms):
        
        tempBedroom=elemBedroom.split(' ')
        if elemBedroom!="-1":
            bedrooms[ind]=int(tempBedroom[1])
        else:
            bedrooms[ind]=-1
        
        
        
    for ind,elemParking in enumerate(parkings):
        tempParking=elemParking.split(' ')
        if elemParking!="-1":
            parkings[ind]=int(tempParking[1])
        else:
            parkings[ind]=-1      
        
        
    #print('-'*50)
    #print(ad_id)
    #print('-'*50)
    #print(published_time)
    #print('-'*50)
    #print(price)
    #print('-'*50)
    #print(description)
    #print('-'*50)
    #print(location)
    #print('-'*50)
    #print(building_type)
    #print('-'*50)
    #print(area)
    #print('-'*50)
    #print(parkings)
    #print('-'*50)
    #print(bedrooms)
    #print('-'*50)

    
    
    for ind,u in enumerate(urls):
        driver.maximize_window()
        driver.get(u)
        perAdinfo=driver.find_element(By.XPATH,'//button[contains(@class,"focus:outline-none text-white")]')
        agancyDriver=driver.find_elements(By.XPATH,'//div[contains(@class,"flex flex-row space-x-2 rtl:space-x-reverse")]')
        agancyInfo=[agitem.text for agitem in agancyDriver]
        agancey_getter=persian(agancyInfo[1].split('\n')[1])
        ageDriver=driver.find_elements(By.XPATH,'//ul[contains(@class,"flex flex-wrap gap-2 p-0 m-0 list-none")]')
        age_info=[item.text for item in ageDriver]
        age_getter=age_info[0].split('\n')
        if any('ساله'in indx for indx in age_getter):
            
            building_age.append(age_getter[-1].strip('ُساله'))
            
        else:
            building_age.append(0)    
        perAdinfo.click()
        time.sleep(2)
        canceling=driver.find_element(By.XPATH,'//button[contains(@class,"w-1/2 btn btn-md btn-grey-outline")]')
        canceling.click()
        phone_list.append(perAdinfo.text)
        agancy.append(agancey_getter)
        
    #print(building_age)

    for ind, item in enumerate(ad_id):
        query='INSERT OR REPLACE INTO details VALUES({},"{}","{}",{},"{}",{},{},{},"{}","{}","{}",{}) '.format(item,
        published_time[ind],persian(description[ind]),price[ind],
        persian(location[ind]),area[ind],bedrooms[ind],parkings[ind],
        urls[ind],phone_list[ind],persian(agancy[ind]),int(building_age[ind]))
        curs.execute(query)

   
    
    
    page_url="https://kilid.com/buy/tehran-saadat_abad?listingTypeId=1&location=273080&page={}".format(cnt)
     
    driver.get(page_url)
    info=driver.find_elements(By.XPATH,'//a[contains(@href,"detail")]')

db.commit()
curs.close()
db.close()    
    
    
    
    
#for p in price:
    #numbers.append(re.findall('\d+\.\d+|\d+', p))
#print(numbers)