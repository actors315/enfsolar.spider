import re
from urllib.request import Request, urlopen, ProxyHandler, build_opener
from urllib.error import HTTPError, URLError
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
        self.companyInfoFile = 'doc/company_list%s.xlsx'

    def get_email(self, code, uri):
        try:
            url = self.baseURL + 'company_email/' + code
            headers = {'User-Agent': self.userAgent[3], 'Referer': self.baseURL + uri}
            print(url)
            print(headers)
            request = Request(url, headers=headers)

            if self.proxies:
                proxy_handler = ProxyHandler(self.proxies)
                opener = build_opener(proxy_handler)
                response = opener.open(request)
            else:
                response = urlopen(request, timeout=60)

            html = response.read()
            html = html.decode('utf-8')
            html = re.sub('<a href="(.*?)">', '', html)
            html = re.sub('</a>', '', html)
            return html
        except (HTTPError, URLError) as e:
            print(e)
            return None

    def collect(self):
        db_handler = db.Factory()

        sql = "SELECT id,email_sign,url FROM company_info WHERE `email` = '' AND email_sign <> '' AND try_index = 0 order by id ASC LIMIT 10"
        arr = db_handler.fetch_data(sql)
        print(arr)
        for temp in arr:
            email = self.get_email(temp[1], temp[2].lstrip('/'))

            if "Too many requests" == email:
                break

            print(email)
            sleep = random.randint(120, 180)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' sleep ' + str(sleep))
            time.sleep(sleep)

            if not email:
                sql = "UPDATE company_info SET `try_index` = try_index + 1 WHERE id = " + str(temp[0])
            else:
                sql = "UPDATE company_info SET `email` = '" + email + "' WHERE id = " + str(temp[0])

            db_handler.execute(sql)

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


s = Spider()
s.run()
