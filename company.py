import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
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

        try:
            url = self.baseURL + uri
            request = Request(url)
            response = urlopen(request)
            html = response.read()
            return html.decode('utf-8')
        except HTTPError as e:
            print(e.msg)
            return None

    def get_directory_list(self, uri):
        html = self.fetch_content(uri)

        db_handler = db.Factory()

        collection = re.findall(self.companyInfo, html)
        try_count = 0
        for tempRow in collection:
            try_count += 1
            print(try_count)
            print(tempRow)

            sql = "insert into company_info(company_id, url) VALUES (" + tempRow[0] + ",'" + tempRow[1] + "')"
            db_handler.execute(sql, False)

        db_handler.commit()

        next_url = re.findall(self.nextUrl, html)
        if next_url:
            time.sleep(random.randint(1, 30) / 100)
            next_url = next_url[0]
            self.get_directory_list(next_url.lstrip('/'))


class Spider:
    def __init__(self):
        self.handler = Handler()

    def run(self):
        db.Factory().init_table()

        collection = json.loads(open('doc/directory.json').read())

        for directory in collection:
            uri = 'directory/' + directory
            self.handler.get_directory_list(uri)


s = Spider()
s.run()
