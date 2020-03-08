
import re
from urllib.request import Request, urlopen

from xlsxwriter.workbook import Workbook


# 爬虫的动作
class Handler:
    def __init__(self):
        self.userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.baseURL = u"https://www.enfsolar.com/"
        self.reNextURL = '<li><a href="(.*?)" target="_self"><i class="fa fa-chevron-right">'

    def fetch_content(self, url):
        request = Request(url)
        response = urlopen(request)
        html = response.read()
        print(html)
        return html


class Capsule:

    def collect(self, handler):
        workbook = Workbook('doc/test.xlsx')
        worksheet = workbook.add_worksheet()
        col = 0
        worksheet.write(0, col, u"公司名称")
        worksheet.write(0, col + 1, u"公司地址")
        worksheet.write(0, col + 2, u"公司网站")
        worksheet.write(0, col + 3, u"公司电话")
        worksheet.write(0, col + 4, u"传真")

        workbook.close()


class Spider:

    def __init__(self):
        self.handler = Handler()
        self.capsule = Capsule()

    def run(self):
        self.handler.fetch_content('https://www.enfsolar.com/directory/panel/monocrystalline')
        self.capsule.collect(self.handler)


s = Spider()
s.run()
