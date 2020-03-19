import re
import urllib.request
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from xlsxwriter.workbook import Workbook
import os
import time
import random
from enfsolar.spider import db


class Handler:

    def __init__(self):
        self.baseURL = u"https://www.enfsolar.com/"
        self.companyName = '<h1 class="blue-title" itemprop="name">[\s]*(.*?)[\s]*?</h1>'
        self.category = '<a\s*class="enf-icon-type enf-icon-type-(.*?) current enf-tooltip" data-container="body" data-content="(.*?)"'
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

        self.companyName2 = '<div class="name">[\s]*(.*)[\s]*?</div>'
        self.tel2 = '<a href=\'tel:(.*?)\'>'
        self.email2 = '<a onclick="fire_event(\'EmailClickFromCompanyProfile\', [\d]+?)" href="mailto: (.*?)">'
        self.site2 = '<a onclick="fire_event(\'WebsiteClickFromCompanyProfile\', [\d]+?)" itemprop="url" href="(.*?)" target="_blank" title=".*">'
        self.region2 = '<div class="word"  style="margin-left: 40px;">[\s]*(.*?)[\s]*<img class="enf-flag" '

        self.proxies = ''

    def fetch_content(self, uri):

        url = self.baseURL + uri

        try:
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
        except (HTTPError, URLError) as e:
            print(url)
            print(e)
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
        else:
            collection = re.findall(self.companyName2, html)
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
        else:
            collection = re.findall(self.tel2, html)
            if collection:
                row['tel'] = collection[0]

        collection = re.findall(self.email, html)
        if collection:
            row['email'] = collection[0]
        else:
            collection = re.findall(self.email2, html)
            if collection:
                row['email'] = collection[0]

        collection = re.findall(self.email_click, html)
        if collection:
            row['email_sign'] = collection[0]

        collection = re.findall(self.site, html)
        if collection:
            row['site'] = collection[0]
        else:
            collection = re.findall(self.site2, html)
            if collection:
                row['site'] = collection[0]

        collection = re.findall(self.region, html)
        if collection:
            row['region'] = collection[0]
        else:
            collection = re.findall(self.region2, html)
            if collection:
                row['region'] = collection[0]

        return row

    def collect(self):
        db_handler = db.Factory()

        sql = "SELECT id,company_id,url FROM company_info WHERE `category` = '' LIMIT 1000"
        arr = db_handler.fetch_data(sql)

        error_count = 0

        for temp in arr:
            info = self.get_company_info(temp[2].lstrip('/'))

            if not info:
                time.sleep(60)
                error_count += 1
                print(info)
                continue

            if error_count == 10:
                break

            sql = "UPDATE company_info SET `name` = '" + info['name'] + "',`category` = '" + info['category'] + "'," + \
                  "`region` = '" + info['region'] + "',`site` = '" + info['site'] + "'," + \
                  "`email` = '" + info['email'] + "'," + "`email_sign` = '" + info['email_sign'] + "'," + \
                  "`tel` = '" + info['tel'] + "'" + \
                  " WHERE id = " + str(temp[0])
            db_handler.execute(sql, False)
            sleep = random.randint(10, 60) / 120
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' sleep ' + str(sleep))
            time.sleep(sleep)

        db_handler.commit()


class Spider:
    def __init__(self):
        self.handler = Handler()

    def run(self):

        self.handler.collect()


s = Spider()
s.run()
