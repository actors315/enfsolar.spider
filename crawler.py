import re
from urllib.request import Request, urlopen

from xlsxwriter.workbook import Workbook


# 爬虫的动作
class Handler:
    def __init__(self):
        self.userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.baseURL = u"https://www.enfsolar.com/"
        self.reNextURL = '<li><a href="(.*?)" target="_self"><i class="fa fa-chevron-right">'
        self.enfListTable = '<table class="enf-list-table " >[\s\S]*?<tbody>([\s\S]*?)</tbody>'
        self.companyLine = '<tr>[\s\S]*?</tr>'
        self.companyName = '<a onclick="fire_event.*">[\s]*(.*)[\s]*</a>'
        self.regionName = '<td class="no-padding ">[\s]*<img[\s\S]+?>[\s]*(.*?)[\s]*?</td>'

    def fetch_content(self, url):
        request = Request(url)
        response = urlopen(request)
        html = response.read()
        return html.decode('utf-8')

    def get_company_name(self, line):
        item = re.findall(self.companyName, line)
        if len(item) > 0:
            return item[0]
        return ''

    def get_region_name(self, line):
        print(line)
        item = re.findall(self.regionName, line)
        if len(item) > 0:
            return item[0]
        return ''

    def get_company_list(self, html):
        items = []

        list_html = re.findall(self.enfListTable, html)
        if len(list_html) > 0:
            list_html = list_html[0]
            list_line = re.findall(self.companyLine, list_html)
            for line in list_line:
                company = {
                    'name': self.get_company_name(line),
                    'region': self.get_region_name(line)
                }
                items.append(company)

        return items


class Capsule:

    def collect(self, list):
        workbook = Workbook('doc/test.xlsx')
        worksheet = workbook.add_worksheet()
        row = col = 0
        worksheet.write(0, col, u"Company Name")
        worksheet.write(0, col + 1, u"Region")
        worksheet.write(0, col + 2, u"公司网站")
        worksheet.write(0, col + 3, u"公司电话")
        worksheet.write(0, col + 4, u"传真")

        for item in list:
            print(item)
            row += 1
            worksheet.write(row, col, item['name'])
            worksheet.write(row, col+1, item['region'])

        workbook.close()


class Spider:

    def __init__(self):
        self.handler = Handler()
        self.capsule = Capsule()

    def run(self):
        html = self.handler.fetch_content('https://www.enfsolar.com/directory/panel/monocrystalline')
        company_list = self.handler.get_company_list(html)
        self.capsule.collect(company_list)


s = Spider()
s.run()
