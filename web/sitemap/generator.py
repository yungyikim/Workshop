
import time
import lxml
import requests
import argparse
import urllib.parse
import datetime
from pytz import timezone
from lxml import etree, html
from lxml.html.clean import clean_html

tz = timezone('Asia/Seoul')

class Generator:
    def __init__(self, host):
        self.host = host
        self.parsed_urls = []
        pass

    def get_page(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
            }

            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code != 200:
                print (res)
                return None

            return res.text
        except Exception as e:
            print (e)
            return None

    def parse(self, url):
        html = self.get_page(url)
        if not html:
            print ('download failed, {}'.format(url))
            return None

        print (url)

        tree = lxml.html.fromstring(html)
        elements = tree.cssselect('a')
        for el in elements:
            link = el.get('href')
            if not link:
                continue

            if link[0] == '/' or link[0] == '?':
                link = urllib.parse.urljoin(self.host, link)

            if link.find(self.host) >= 0 or link[0] == '/' or link[0] == '?':
                if not link in self.parsed_urls:
                    self.parsed_urls.append(url)

    def generate(self):
        self.parsed_urls.append(self.host)

        start = 0
        while True:
            end = len(self.parsed_urls)
            if start == end:
                break

            for i in range(start, end):
                self.parse(self.parsed_urls[i])
            start = end

        now = datetime.datetime.now(tz).isoformat()

        t = ''
        for url in self.parsed_urls:
            t += '''<url>
  <loc>{}</loc>
  <lastmod>{}</lastmod>
  <priority>0.80</priority>
</url>'''.format(
                url,
                now
            )

        text = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
{}
</urlset>'''.format(
            t
        )

        filename = 'sitemap.xml'
        with open(name, 'w') as f:
            f.write(text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str)
    args = parser.parse_args()

    if not args.host:
        print ('usage: generator.py [--host] HOST')
    else:
        obj = Generator(args.host)
        obj.generate()
