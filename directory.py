import re
from urllib.request import Request, urlopen
import json


class Handler:

    def __init__(self):
        self.baseURL = u"https://www.enfsolar.com/"
        self.directoryUrl = '<a href="/directory/(.*)" class="no-hover-underline">'

    def fetch_content(self, uri):
        url = self.baseURL + uri
        request = Request(url)
        response = urlopen(request)
        html = response.read()
        return html.decode('utf-8')

    def get_directory_list(self, directory):
        uri = 'directory/' + directory
        html = self.fetch_content(uri)
        directory_list = re.findall(self.directoryUrl, html)
        return directory_list


class Spider:
    def __init__(self):
        self.handler = Handler()

    def run(self):
        directory_list = ['panel', 'component', 'material', 'equipment']
        dir_url_list = [];
        for directory in directory_list:
            temp_list = self.handler.get_directory_list(directory)
            dir_url_list.extend(temp_list)

        fw = open('doc/directory.json', 'w')
        fw.write(json.dumps(dir_url_list))


s = Spider()
s.run()
