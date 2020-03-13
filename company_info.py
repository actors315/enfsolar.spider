import re
import urllib.request
from urllib.request import Request, urlopen, HTTPError
import csv
import os
import time
import random
from enfsolar.spider import db


class Handler:

    def __init__(self):
        self.baseURL = u"https://www.enfsolar.com/"
        self.companyName = '<h1 class="blue-title" itemprop="name">[\s]*(.*?)[\s]*?</h1>'
        self.category = '<a\s*class="enf-icon-type enf-icon-type-panel current enf-tooltip" data-container="body" data-content="(.*?)"'
        self.category2 = '<span itemprop="name">[\s]*<span class="glyphicon glyphicon-home"></span>[\s]*(.*?)[\s]*</span>'
        self.tel = '<td itemprop="telephone">[\s]*?<a.*>(.*)</a>[\s]*?</td>'
        self.email = '<td itemprop="email">[\s]*?<a.*?href="mailto: ([^\s]+?)">'
        self.email_click = '<span onclick="getEmail\(\'(.*)\', this\)" style="cursor: pointer;">'
        self.site = '<a onclick="fire_event\(\'WebsiteClickFromCompanyProfile\', [\d]+\)" itemprop="url" href="(.*?)" target="_blank" title=".*">'
        self.region = '<td[\s]*>[\s]*(.*?)[\s]*<img class="enf-flag" src'
        self.userAgent = [
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',

        ]
        self.proxies = ''
        self.file = 'doc/company_list.csv'
        self.companyInfoFile = 'doc/company_list.xlsx'

    def fetch_content(self, uri):
        try:
            url = self.baseURL + uri
            headers = {'User-Agent': self.userAgent[random.randint(0, 3)]}
            request = Request(url, headers=headers)

            if self.proxies:
                proxy_handler = urllib.request.ProxyHandler(self.proxies)
                opener = urllib.request.build_opener(proxy_handler)
                response = opener.open(request)
            else:
                response = urlopen(request)

            html = response.read()
            return html.decode('utf-8')
        except HTTPError as e:
            print(e.msg)
            return None

    def get_company_info(self, uri):
        html = self.fetch_content(uri)

        if not html:
            return False

        row = {
            'name': '',
            'region': '',
            'site': '',
            'email': '',
            'email_sign': '',
            'tel': '',
            'category': ''
        }

        collection = re.findall(self.companyName, html)
        if collection:
            row['name'] = collection[0]

        collection = re.findall(self.category, html)
        if collection:
            row['category'] = collection[0]
        else:
            collection = re.findall(self.category2, html)
            if collection:
                row['category'] = collection[0]

        collection = re.findall(self.tel, html)
        if collection:
            row['tel'] = collection[0]

        collection = re.findall(self.email, html)
        if collection:
            row['email'] = collection[0]

        collection = re.findall(self.email_click, html)
        if collection:
            row['email_sign'] = collection[0]

        collection = re.findall(self.site, html)
        if collection:
            row['site'] = collection[0]

        collection = re.findall(self.region, html)
        if collection:
            row['region'] = collection[0]

        return row

    def collect(self):
        db_handler = db.Factory()
        db_handler.init_table()
        with open(self.file) as f:
            reader = csv.reader(f)
            for tempRow in reader:
                info = self.get_company_info(tempRow[1].lstrip('/'))
                print(info)
                if not info:
                    break
                else:
                    sql = "insert into company_info(company_id, url, name, region, site, tel, email, email_sign, category) VALUES (" + \
                          tempRow[0] + ",'" + tempRow[1] + "','" + info['name'] + "','" + info['region'] + "','" + \
                          info['site'] + "','" + info['tel'] + "','" + info['email'] + "','" + info['email_sign'] + \
                          "','" + info['category'] + "')"
                    db_handler.execute(sql, False)
                    time.sleep(random.randint(10, 60) / 120)

        db_handler.commit()


class Spider:
    def __init__(self):
        self.handler = Handler()

    def run(self):
        if os.path.exists(self.handler.companyInfoFile):
            os.remove(self.handler.companyInfoFile)

        self.handler.collect()


s = Spider()
s.run()
