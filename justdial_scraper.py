__author__ = 'Dharmendra Tolani'
#justdial scraper
from HTMLParser import HTMLParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import sys

import unittest, time, re

from bs4 import BeautifulSoup

import requests
import csv

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    html = str(html)
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def getAddresses(str):
    ret = []
    arr = str.split('|')
    ret[0] = arr[0].strip()
    ret[1] = arr[1].strip()
    return ret


def getLatLong(data):
   latlong = [0,0]
   if(data):
       arr = data[0].get('onclick').split(",")
       latlong[0] = arr[3].strip().strip("'")
       latlong[1] = arr[4].strip().strip("'")
   return latlong

def getJustDialId(href):
   arr = href.split('?')
   arr1 = arr[0].split('/')
   return arr1[-1]

def create_csv():
    row = ['city','area','type','title','jdid','phone','lat','lng','short_addr','full_addr','img']
    with open('C:/test.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def add_to_csv(row):
    with open('C:/test.csv', 'ab') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def fetch(driver,city,area,type):
    url = "http://www.justdial.com/"+city+"/"+type+"-<near>-"+area
    print url
    driver.get(url)
    for i in range(1,1):
     #elem = driver.find_element_by_xpath('//*[@id="best_deal_div"]/section/span')
     #print elem
     #exit
     #if elem.is_visible():
     #    elem.click()
     driver.execute_script("window.scrollTo(0, "+str(i*2000)+");")
     time.sleep(1)
    time.sleep(4)
    html_source = driver.page_source
    soup = BeautifulSoup(html_source.encode('utf-8'))
    for i in range(0,99):
     base_selector  = '#bcard'+str(i)+' > section.jcar > section.jrcl > aside.compdt'
     title_soup  = soup.select(base_selector+' > p.jcnwrp > span > a')
     if not title_soup:
        break
     title = title_soup[0].get('title')#title
     href = title_soup[0].get('href')#href
     jdid = getJustDialId(href)
     print str(i)+" "+title+" "+jdid
     phone = ""
     phone_soup = soup.select(base_selector+' > p.jrcw > a > b')
     if phone_soup:
         phone = strip_tags(phone_soup[0])#phone
     latlong = getLatLong(soup.select(base_selector+' > p.jaid > a'))
     lat = latlong[0]
     lng = latlong[1]
     adrs = strip_tags(soup.select(base_selector+' > p.jaid > span.jaddt.trans')[0]).split('|')
     short_addr =  adrs[0].strip().strip('..')#area
     full_addr = adrs[1].strip().strip('more...').strip()#full address
     img_url = ""
     img_soup = soup.select("#bcard"+str(i)+" > section.jdvwrp > a")
     if img_soup:
         img_url = img_soup[0].get('data-original')
     row = [city,area,type,title,jdid,phone,lat,lng,short_addr,full_addr,img_url]
     add_to_csv(row)



cities  = {}
cities['Bangalore'] = ["Indira-nagar","koramangala"]
types = ["Yoga-Classes","Gym","Zumba-Classes","Aerobics-Classes","Salsa-Classes","Kick-Boxing-Classes","Mixed-Martial-Art-Training-Centres"]
driver = webdriver.Firefox()
create_csv()
for city in cities:
    areas = cities[city]
    for a in areas:
        for type in types:
            fetch(driver,city,a,type)


