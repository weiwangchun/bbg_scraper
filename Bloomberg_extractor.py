# Bloomberg Extractor
# weiwangchun
# using requests and beautifulsoup to grab headlines from Bloomberg


import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
from lxml.html import fromstring
import sys

# grab a set proxies
# ----------------------------
def get_proxies():
    url = 'https://free-proxy-list.net/anonymous-proxy.html'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:30]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


# header settings
# ----------------------------
# ua_list:  https://udger.com/resources/ua-list
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0',
    'From': 'marcus.aurelius@rome.com' 
}


# bloomberg scraper fn
# ----------------------------
def scrape_bloomberg(subject, page_number, headers, proxies):
    full_url = 'https://www.bloomberg.com/search?query=' + subject + '&sort=time:desc' + '&page=' + str(page_number)
    response = requests.get(full_url, headers=headers, proxies = proxies)
    soup = BeautifulSoup(response.content, 'html.parser')
    #dates = [''.join(s.findAll(text=True))for s in soup.findAll(['time'])]
    #text = [''.join(s.findAll(text=True))for s in soup.findAll(['h1'])]
    #tmp = np.column_stack((dates, text))
    #_, idx = np.unique(tmp, axis = 0, return_index = True)
    #tmp = tmp[np.sort(idx)]
    links = [''.join(s.attrs['href']) for s in soup.findAll('a', class_="search-result-story-thumbnail__link", href = True)]
    #tmp = np.column_stack((tmp,  links))
    return links



if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Error: Please provide subject title, page_min and pages_max. \nFor Example: >Bloomberg_extractor.py bitcoin 1 99\n")
        sys.exit(1)

    subject = str(sys.argv[1])
    pages_min = int(sys.argv[2])
    pages_max = int(sys.argv[3])

    completed_page = pages_min - 1
    #full = np.array(['date', 'title', 'link'])
    full = np.array(['link'])

    while completed_page < pages_max:
        proxy_list = get_proxies()
        for proxy in proxy_list:
            pages = np.arange(completed_page + 1,pages_max+1,1)

            proxies = {
                'http': proxy,
                'https': proxy,
            }

            for page in pages:

                print('Trying Page ' + str(page) + ' using proxy ' + proxy)
                try:
                    full = np.append(full, scrape_bloomberg(subject = subject, page_number = page, headers = headers, proxies = proxies))
                    print('Page ' + str(page) + ' completed\n')
                    np.savetxt('RESULTS_TMP.csv', full, fmt='%s', delimiter=',')
                    completed_page = page
                except Exception as e:
                    print(str(e))
                    print('Failed Page ' + str(page) + ' using proxy ' + proxy)
                    break

    np.savetxt('results'+ subject + str(pages_max)+'.csv', full, fmt='%s', delimiter=',')
