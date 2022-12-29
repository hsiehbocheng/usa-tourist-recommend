import pymongo
import datetime
import pickle
import csv
import time
import pandas as pd
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

from web_crawler import coounty_to_attraction, site_to_trending

if __name__ == '__main__':
    us_city_df = pd.read_csv('uscities.csv')
    us_city_df = us_city_df[['city', 'state_name', 'county_name','density','lat','lng']]
    us_city_dict = us_city_df.to_dict()
    target_us_city_dict = us_city_dict.to_dict()
    # webdriver setting:
    driver_location = 'chromedriver.exe'

    #英文版Chromedriver
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en-GB')
    driver = webdriver.Chrome(executable_path=driver_location, options=options)
    driver.maximize_window()

    client = pymongo.MongoClient("mongodb+srv://nccustat:nccustat@nccustat.lxkhf1q.mongodb.net/?retryWrites=true&w=majority")
    db = client.travel # 選擇操作 travel 資料庫

    # 選擇操作的集合
    Site_connection = db.TravelSite
    Trend_connection = db.SiteTrend

    # main::
# us_city_df
    date = datetime.datetime.today()
    for idx, city in target_us_city_dict['city'].items():
        # print(f'city: {city}, County: {us_city_dict["county_name"][idx]}, state: {us_city_dict["state_id"][idx]}')
        print(city, '.............')
        rawdata, site_list = coounty_to_attraction(city, 
                                                target_us_city_dict['county_name'][idx], 
                                                target_us_city_dict['state_name'][idx] , 
                                                target_us_city_dict['lat'][idx], 
                                                target_us_city_dict['lng'][idx])
        # print(f'[TravelSite DB inserting] number of data: {len(rawdata)}')
        try:
            Site_connection.insert_many(rawdata)
        except:
            continue
        trend_list = []
        for site in site_list:
            # print('---', site)
            trend = site_to_trending(site, 
                                    city,
                                    target_us_city_dict['county_name'][idx], 
                                    target_us_city_dict['state_name'][idx],
                                    date,
                                    target_us_city_dict['lat'][idx], 
                                    target_us_city_dict['lng'][idx] )
            time.sleep(random.randint(1, 4))
            # print(f'n_post: {trend["n_post"]}, upvotes: {trend["upvotes"]}, n_comments: {trend["n_comment"]}')
            trend_list.append(trend)
        # print(f'[SiteTrend DB inserting] number of data: {len(rawdata)}')
        Trend_connection.insert_many(trend_list)