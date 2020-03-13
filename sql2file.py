import re
import urllib.request
from urllib.request import Request, urlopen, HTTPError
import csv
from xlsxwriter.workbook import Workbook
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

    def get_email(self, code, uri):
        try:
            url = self.baseURL + 'company_email/' + code
            headers = {'User-Agent': self.userAgent[random.randint(0, 3)], 'Referer': self.baseURL + uri}
            request = Request(url, headers=headers)

            if self.proxies:
                proxy_handler = urllib.request.ProxyHandler(self.proxies)
                opener = urllib.request.build_opener(proxy_handler)
                response = opener.open(request)
            else:
                response = urlopen(request)

            html = response.read()
            html = html.decode('utf-8')
            html = re.sub('<a href="(.*?)">', '', html)
            html = re.sub('</a>', '', html)
            return html
        except HTTPError as e:
            print(e.msg)
            time.sleep(random.randint(5, 60))
            return None

    def get_company_info(self, uri):
        html = self.fetch_content(uri)

        if not html:
            return None

        row = {
            'name': '',
            'region': '',
            'site': '',
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
        workbook = Workbook(self.companyInfoFile)
        worksheet = workbook.add_worksheet()
        row = col = 0
        worksheet.write(0, col, 'id')
        worksheet.write(0, col + 1, u"公司名称")
        worksheet.write(0, col + 2, u"国家")
        worksheet.write(0, col + 3, u"公司网站")
        worksheet.write(0, col + 4, u"公司电话")
        worksheet.write(0, col + 5, u"邮箱")
        worksheet.write(0, col + 6, u'类别')

        with open(self.file) as f:
            reader = csv.reader(f)
            for tempRow in reader:

                row += 1
                worksheet.write(row, col, tempRow[0])

                info = self.get_company_info(tempRow[1].lstrip('/'))

                worksheet.write(row, col + 1, info['name'])
                worksheet.write(row, col + 2, info['region'])
                worksheet.write(row, col + 3, info['site'])
                worksheet.write(row, col + 4, info['tel'])
                worksheet.write(row, col + 5, info['email'])
                worksheet.write(row, col + 6, info['category'])

                time.sleep(random.randint(1, 100) / 80)

                if 10 == row:
                    break

        workbook.close()


class Spider:
    def __init__(self):
        self.handler = Handler()

    def run(self):
        if os.path.exists(self.handler.companyInfoFile):
            os.remove(self.handler.companyInfoFile)

        self.handler.collect()


s = Spider()
s.run()