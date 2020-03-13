import re
from urllib.request import Request, urlopen
import json
import os
import csv
import time
import random

from enfsolar.spider import db


class Handler:

    def __init__(self):
        self.baseURL = u"https://www.enfsolar.com/"
        self.companyInfo = '<a onclick="fire_event\(\'CompanyClickFromCompanyList\', (\d+)\)" href="(.*?)">'
        self.nextUrl = '<a href="(.*?)"[\s]*target="_self">[\s]*<i class="fa fa-chevron-right"></i>'
        self.file = 'doc/company_list.csv'

    def fetch_content(self, uri):
        url = self.baseURL + uri
        request = Request(url)
        response = urlopen(request)
        html = response.read()
        return html.decode('utf-8')

    def get_directory_list(self, uri):
        html = self.fetch_content(uri)

        db_handler = db.Factory()

        collection = re.findall(self.companyInfo, html)
        for tempRow in collection:
            print(tempRow)
            sql = "insert into company_info(company_id, url) VALUES (" + tempRow[0] + ",'" + tempRow[1] + "')"
            db_handler.execute(sql, False)

        db_handler.commit()

        next_url = re.findall(self.nextUrl, html)
        if next_url:
            time.sleep(random.randint(1, 10) / 10)
            next_url = next_url[0]
            self.get_directory_list(next_url.lstrip('/'))


class Spider:
    def __init__(self):
        self.handler = Handler()

    def run(self):
        db.Factory().init_table()

        collection = json.loads(open('doc/directory.json').read())
        if os.path.exists(self.handler.file):
            os.remove(self.handler.file)

        for directory in collection:
            uri = 'directory/' + directory
            self.handler.get_directory_list(uri)


s = Spider()
s.run()
