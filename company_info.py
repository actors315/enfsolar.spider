import os
import random
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from xlsxwriter.workbook import Workbook

from enfsolar.spider import db


class Handler:

    def __init__(self):
        self.baseURL = u"https://www.enfsolar.com/"
        self.companyName = '<h1 class="blue-title" itemprop="name">[\s]*(.*?)[\s]*?</h1>'
        self.category = '<a\s*class="enf-icon-type enf-icon-type-.*? current enf-tooltip" data-container="body" data-content="(.*?)"'
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
        self.email2 = '<[\s]*a[\s]*onclick="fire_event(\'EmailClickFromCompanyProfile\', [\d]+?)"[\s]*href[\s]*=[\s]*"mailto: (.*?)"[\s]*>'
        self.site2 = '<a onclick="fire_event(\'WebsiteClickFromCompanyProfile\', [\d]+?)" itemprop="url" href="(.*?)" target="_blank" title=".*">'
        self.region2 = '<div class="word"  style="margin-left: 40px;">[\s]*(.*?)[\s]*<img class="enf-flag" '

        self.companyInfoFile = 'doc/company_list%s.xlsx'

    def get_email(self, code, uri):
        try:
            url = self.baseURL + 'company_email/' + code
            headers = {'User-Agent': self.userAgent[3], 'Referer': self.baseURL + uri}
            request = Request(url, headers=headers)

            response = urlopen(request, timeout=60)

            html = response.read()
            html = html.decode('utf-8')
            html = re.sub('<a href="(.*?)">', '', html)
            html = re.sub('</a>', '', html)
            return html
        except (HTTPError, URLError) as e:
            print(e)
            return None

    def fetch_content(self, uri):

        url = self.baseURL + uri
        try:
            headers = {'User-Agent': self.userAgent[random.randint(0, 3)]}
            request = Request(url, headers=headers)

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

        collection = re.findall(self.email_click, html)
        if collection:
            row['email_sign'] = collection[0]

            time.sleep(random.randint(180, 540) / 3)

            email = self.get_email(row['email_sign'], uri)
            if not email:
                return False
            row['email'] = email.replace('#2019#', '@')
        else:
            collection = re.findall(self.email, html)
            if collection:
                row['email'] = collection[0]
            else:
                collection = re.findall(self.email2, html)
                if collection:
                    row['email'] = collection[0]

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

        sql = "SELECT id,company_id,url FROM company_info WHERE `email` = '' order by try_index ASC,id ASC LIMIT 10"
        arr = db_handler.fetch_data(sql)

        for temp in arr:
            info = self.get_company_info(temp[2].lstrip('/'))

            if not info:
                break

            if "Too many requests" == info['email']:
                break

            try:
                sql = "UPDATE company_info SET `name` = '" + info['name'] + "',`category` = '" + info[ 'category'] + "'," + \
                      "`region` = '" + info['region'] + "',`site` = '" + info['site'] + "'," + \
                      "`email` = '" + info['email'] + "'," + "`email_sign` = '" + info['email_sign'] + "'," + \
                      "`tel` = '" + info['tel'] + "',`try_index` = ifnull(try_index,0) + 1" + \
                      " WHERE id = %d"
                db_handler.execute(sql % temp[0])
            except ValueError as e:
                print(sql)
                print(e)

            sleep = random.randint(10, 60) / 10
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' sleep ' + str(sleep))
            sys.stdout.flush()
            time.sleep(sleep)

    def dump_to_excel(self):

        index = 1
        last_id = 0
        while True:

            sql = "SELECT company_id,name,region,site,tel,email,category,id FROM company_info WHERE id > " + \
                  str(last_id) + " ORDER BY id ASC LIMIT 50000"
            arr = db.Factory().fetch_data(sql)

            if not arr:
                break

            file = self.companyInfoFile % index

            if os.path.exists(file):
                os.remove(file)

            workbook = Workbook(file)
            worksheet = workbook.add_worksheet()
            row = col = 0
            worksheet.write(0, col, 'id')
            worksheet.write(0, col + 1, u"公司名称")
            worksheet.write(0, col + 2, u"国家")
            worksheet.write(0, col + 3, u"公司网站")
            worksheet.write(0, col + 4, u"公司电话")
            worksheet.write(0, col + 5, u"邮箱")
            worksheet.write(0, col + 6, u'类别')

            for tempRow in arr:
                last_id = tempRow[7]

                row += 1
                worksheet.write(row, col, tempRow[0])
                worksheet.write(row, col + 1, tempRow[1])
                worksheet.write(row, col + 2, tempRow[2])
                worksheet.write(row, col + 3, tempRow[3])
                worksheet.write(row, col + 4, tempRow[4])
                worksheet.write(row, col + 5, tempRow[5])
                worksheet.write(row, col + 6, tempRow[6])

            workbook.close()

            index += 1


class Spider:
    def __init__(self):
        self.handler = Handler()

    def run(self):
        self.handler.collect()
        self.handler.dump_to_excel()
        print('sleep to wait')
        time.sleep(random.randint(180, 600) / 3)


s = Spider()
s.run()
