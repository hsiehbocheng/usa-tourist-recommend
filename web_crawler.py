import csv
import time
import pandas as pd
# 當爬取的網頁為 JavaScript 網頁前端（非伺服器端）生成，需引入 selenium 套件來模擬瀏覽器載入網頁並跑完 JavaScript 程式才能取得資料
from selenium import webdriver
# 引入套件
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import random

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from webdriver_manager.core.utils import ChromeType
import json


# 
def coounty_to_attraction(city, county, state , lat , lng , roll = 10 ):
    # 發出網路請求
    # key_word = city + ' tourist attractions'
    # url = 'https://www.google.com.tw/maps/search/' + key_word + '/@37.7899256,-122.5203015,12z/data=!3m1!4b1?'
    # driver.get(url)

    key_word = city+' ' + county + ' '+ state +' tourist attractions'
    # 發出網路請求
    
    driver.get('https://www.google.com.tw/maps/search/'+ key_word +'/@40.7359618,-74.0388916,13z/data=!3m1!4b1?')
# https://www.google.com.tw/maps/@42.2214911,-106.0950428,4.19z?
    # 選到元素後，送出查詢參數並按送出
    # search_input = driver.find_element(By.CSS_SELECTOR, '#searchboxinput')
    # search_btn = driver.find_element(By.CSS_SELECTOR, '#searchbox-searchbutton')

    # search_input.send_keys(city+' ' + county + ' '+ state +' tourist attractions')
    # search_btn.click()

    time.sleep(6)
    pane = driver.find_element( By.XPATH ,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')
    for i in range(roll):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane )
        time.sleep(2)
    # 取出網頁整頁內容
    page_content = driver.page_source
    # 將 HTML 內容轉換成 BeautifulSoup 物件，html.parser 為使用的解析器
    soup = BeautifulSoup(page_content, 'html.parser')
    site_list = []
    elements1 = soup.find_all(class_="Nv2PK THOPZb CpccDe")
    row_list = []
    if len(elements1) == 0:
        elements1 = soup.find_all(class_="Nv2PK tH5CWc THOPZb")

    for e in elements1:
        
        type_ = 'None'
        intro = 'None'
        star_reviews = 'None'
        review_count = 'None'

        if pd.isna(e.find_all('div')[1].find('span',class_='ZkP5Je')):
            continue
        else:
            #從搜尋清單抓到的資料
            try:
                site = e.get('aria-label')
                star_reviews = e.find_all('div')[1].find('span',class_='ZkP5Je').get('aria-label')
                stars = float(star_reviews.split('stars')[0])
                review_count = int(star_reviews.split('stars')[1].split('Reviews')[0].replace(",",""))
                url = e.find('a').get('href')
                if(review_count<100):
                    pass
            except:
                pass
            try:
                #一個一個點開才爬到的資料
                driver.get(url)
                soup_url = BeautifulSoup(driver.page_source)

                type_ = soup_url.find('div',class_='skqShb').find('div',jsan="7.fontBodyMedium,t-OOXHCmHQ_5Q").find('button',class_='DkEaL u6ijk').text
            except:
                type_ = 'None'
            try:
                intro = soup_url.find('div',class_="WeS02d fontBodyMedium").find('div',class_="PYvSYb").find_all('span')[0].text
            except:
                intro = 'None'
            try:
                review = tuple(x.text for x in soup_url.find_all('div',class_='MyEned'))
                
                site_list.append(site)
                row_list.append({'site':site,
                                'city': city,
                                'county': county,
                                'state': state,
                                'stars':stars,
                                'reviews':review_count,
                                'type':type_,
                                'introduce':intro,
                                'review':review,
                                'url':url,
                                'lat':lat,
                                'lng':lng})
                print(f'--- {site}')
            except:
                pass
    return row_list, site_list

def site_to_trending(key_word, city, county, state, date , lat , lng ):
    driver.get("https://www.reddit.com/r/travel/search/?q="+key_word +'&restrict_sr=1&sr_nsfw=&t=all')

    # 有下拉極限 只能加載出250則左右的貼文
    
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollBy(0,500000)")
        time.sleep(2)
        if last_height == driver.execute_script("return document.body.scrollHeight"):
            break
    try:
        html = driver.page_source
        page_elements = BeautifulSoup(html, 'html.parser').find('div' ,{ "class": 'QBfRw7Rj8UkxybFpX-USO'})
        trending_ele = page_elements.find_all('span' , {'class':'_vaFo96phV6L5Hltvwcox'})
        articla_num = int(len( trending_ele ) /3)
        upvotes = 0
        comments = 0
        def num_trans(x):
            num = 0
            if x.endswith('k'):
                num = float( x[ : len(x) - 1 ]) * 1000
            else:
                num = int( x )
            return num
        for n in range(articla_num):
            num_0 = trending_ele[ n * 3 ].text.split(' ')[ 0 ]
            num_1 = trending_ele[ n * 3 + 1 ].text.split(' ')[ 0 ]
            upvotes += num_trans(num_0)
            comments += num_trans(num_1)
        return {'site': key_word,
                'date': date,
                'city': city,
                'county': county,
                'state': state,
                'lat':lat,
                'lng':lng,
                'n_post': articla_num,
                'upvotes': int(upvotes),
                'n_comment': comments}
    except:
        return {'site': key_word,
                'date': date,
                'city': city,
                'county': county,
                'state': state,
                'lat':lat,
                'lng':lng,
                'n_post': 0,
                'upvotes': 0,
                'n_comment': 0}

    
