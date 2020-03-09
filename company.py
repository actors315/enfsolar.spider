import re
from urllib.request import Request, urlopen
import json
import os
import csv


class Handler:

    def __init__(self):
        self.baseURL = u"https://www.enfsolar.com/"
        self.companyInfo = '<a onclick="fire_event\(\'CompanyClickFromCompanyList\', (\d+)\)" href="(.*?)">'
        self.file = 'doc/company_list.csv'

    def fetch_content(self, uri):
        url = self.baseURL + uri
        request = Request(url)
        response = urlopen(request)
        html = response.read()
        return html.decode('utf-8')

    def get_directory_list(self, uri):
        html = self.fetch_content(uri)
        collection = re.findall(self.companyInfo, html)
        with open(self.file, "a+", newline='') as file:
            csv_file = csv.writer(file)
            csv_file.writerows(collection)


class Spider:
    def __init__(self):
        self.handler = Handler()

    def run(self):
        collection = json.loads(open('doc/directory.json').read())
        if os.path.exists(self.handler.file):
            os.remove(self.handler.file)

        for directory in collection:
            uri = 'directory/' + directory
            self.handler.get_directory_list(uri)
            exit(0)


s = Spider()
s.run()
