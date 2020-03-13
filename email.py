import re
import urllib.request
from urllib.request import Request, urlopen, HTTPError
from xlsxwriter.workbook import Workbook
import os
import time
import random
from enfsolar.spider import db


class Handler:

    def __init__(self):
        self.baseURL = u"https://www.enfsolar.com/"
        self.userAgent = [
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
        ]
        self.proxies = ''
        self.companyInfoFile = 'doc/company_list.xlsx'

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

    def collect(self):
        db_handler = db.Factory()

        sql = "SELECT id,email_sign,url FROM company_info WHERE `email` = '' AND email_sign <> '' LIMIT 100"
        arr = db_handler.fetch_data(sql)
        try_count = 0
        for temp in arr:
            email = self.get_email(temp[1], temp[2].lstrip('/'))

            try_count += 1
            if 1 == try_count % 10:
                print(try_count)
                print(email)

            if not email:
                time.sleep(60)
                break

            sql = "UPDATE company_info SET `email` = '" + email + "' WHERE id = " + temp[0]
            db_handler.execute(sql, False)
            time.sleep(random.randint(60, 120) / 2)

        db_handler.commit()

    def dump_to_excel(self):

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

        sql = "SELECT company_id,name,region,site,tel,email,category FROM company_info ORDER BY id ASC "
        arr = db.Factory().fetch_data(sql)
        for tempRow in arr:
            row += 1
            worksheet.write(row, col, tempRow[0])
            worksheet.write(row, col + 1, tempRow[1])
            worksheet.write(row, col + 2, tempRow[2])
            worksheet.write(row, col + 3, tempRow[3])
            worksheet.write(row, col + 4, tempRow[4])
            worksheet.write(row, col + 5, tempRow[5])
            worksheet.write(row, col + 6, tempRow[6])

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
