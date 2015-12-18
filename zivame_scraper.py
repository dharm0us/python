__author__ = 'Dharmendra Tolani'

#zivame scraper

from bs4 import BeautifulSoup
import time
import sys
import requests
import csv
import re


import urllib2

def fetch_product_list():
    for p in range(147,202):
     time.sleep(1)
     url = 'http://www.zivame.com/catalog/seo_sitemap/product/?p='+str(p)
     #print url
     #continue
     html_source = urllib2.urlopen(url).read()
     soup = BeautifulSoup(html_source)
     res = soup.find('ul', attrs={'class' : 'sitemap'})
     lis = res.findAll('li')
     for j in lis:
         try:
          print j.find('a').contents[0]
         except:
          continue

def fetch_single(url):
    html_source = '<div class="breadcrumbs"> <ul> <li class="home"> <span itemscope itemtype="http://data-vocabulary.org/Breadcrumb"> <a href="http://www.zivame.com/" itemprop="url" title="Go to Home Page"><span itemprop="title">Home</span></a> </span>	<span> &#47; </span> </li> <li class="product"> <strong>Enamor Seamless Transparent Back Wirefree Bra</strong> </li> </ul> </div>'
    soup = BeautifulSoup(html_source)
    crumb = soup.find('div', attrs={'class' : 'breadcrumbs'}).decode_contents(formatter="html")
    print crumb
    sys.exit()
    html_source = urllib2.urlopen(url).read()
    html_source = html_source.replace('<span>/','<span> &#47;')
    print html_source
    soup = BeautifulSoup(html_source)
    brand = soup.find('h3', attrs={'class' : 'brand_default_text'}).text
    name = soup.find('h1', attrs={'itemprop' : 'name'}).text
    rating = soup.find('span', attrs={'itemprop' : 'ratingValue'})
    if(rating):
        rating = rating.text
    reviewCount = soup.find('span', attrs={'itemprop' : 'reviewCount'})
    if(reviewCount):
        reviewCount = reviewCount.text
    price = soup.find('span', attrs={'itemprop' : 'price'}).text
    avail = soup.find('input', attrs={'id' : 'addtocartbtn'})
    instock = False
    if(avail):
        instock = True
    #crumbs = soup.findAll('span', attrs={'itemtype' : 'http://data-vocabulary.org/Breadcrumb'})
    #soup.fetch('td', {'valign':re.compile('top')})
    crumb = soup.find('div', attrs={'class' : 'breadcrumbs'}).decode_contents(formatter="html")
    print crumb




def create_csv():
    row = ['url','brand','type','title','jdid','phone','lat','lng','short_addr','full_addr','img']
    with open('C:/zivame.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def add_to_csv(row):
    with open('C:/test.csv', 'ab') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def main():
    fetch_product_list();
    #fetch_single('http://www.zivame.com/enamor-seamless-transparent-back-wirefree-bra.html')
    #fetch_single('http://www.zivame.com/enamor-floral-lace-brief.html')

main()
