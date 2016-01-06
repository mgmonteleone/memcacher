from __future__ import with_statement  # we'll use this later, has to be here
from argparse import ArgumentParser
import urllib2
from lib import ContentItem, getcontent
import htmlmin
import sys

import requests
from BeautifulSoup import BeautifulStoneSoup as Soup
from pprint import pprint
import time
from datetime import date

from lib import config, print_error, print_ok, print_warn


class sitePage(ContentItem):
    def __init__(self,loc,prio,change,last,lastdate
                 ,content=None, size=None, contenttype=None,headers=None
                 ):
        super(sitePage,self).__init__(
            uri=loc
        )
        self.uri = loc
        self.prio = prio
        self.change = change
        self.last = last
        self.lastdate = lastdate
        self.headers = headers

    def retrieveFromSite(self):
        try:
            resource = urllib2.urlopen(self.uri, None, config["fetchtimeout"])
        except IOError as e:
            print e.message
            print_error( "--Timed out when retrieving item, consider lengthening timeout.--")

        if resource.getcode() not in [404, 500]:
            meta = resource.info()
            try:
                self.content = resource.read()
                try:
                    self.headers = meta.getheaders()
                except:
                    self.headers = None
                try:
                    self.size = int(meta.getheaders("Content-Length")[0])
                except:
                    self.size = len(self.content)/1000
                try:
                    self.contenttype = meta.getheaders("Content-Type")[0]
                except:
                    contenttype = "text/html"


                print_ok( "Retrieved " + str(self.size) + "kB")
            except Exception as e:
                print_warn("--Could not parse the received object, length or contenttype was bad...--")
                print_warn(e.message)
        else:
            print_warn("----Can not retrieve resource----")


def parse_sitemap(url):
    resp = requests.get(url)
    # we didn't get a valid response, bail
    if 200 != resp.status_code:
        return False

    # BeautifulStoneSoup to parse the document
    soup = Soup(resp.content)

    # find all the <url> tags in the document
    urls = soup.findAll('url')

    # no urls? bail
    if not urls:
        return False

    # storage for later...
    out = []

    # extract what we need from the url
    for u in urls:
        loc = u.find('loc').string
        prio = u.find('priority').string
        change = u.find('changefreq').string
        last = u.find('lastmod').string
        lastdateinter = time.strptime(last, "%Y-%m-%d")
        lastdate = date(year=lastdateinter.tm_year, month=lastdateinter.tm_mon, day=lastdateinter.tm_mday)
        out.append(
            sitePage(
                loc = loc,
                prio = prio,
                change = change,
                last = last,
                lastdate= lastdate
            )
            )
    return out


data = parse_sitemap("http://www.dalmacijanews.hr/sitemap.xml")
for d in data[0:30]:
    if d.lastdate == date(year=2015,month=8,day=23) and d.prio == "0.7":
        d.retrieveFromSite()


        pprint(d.__dict__)
'''
if __name__ == '__main__':
    options = ArgumentParser()
    options.add_argument('-u', '--url', action='store', dest='url', help='The file contain one url per line')
    options.add_argument('-o', '--output', action='store', dest='out', default='out.txt',
                         help='Where you would like to save the data')
    args = options.parse_args()
    urls = parse_sitemap(args.url)
    if not urls:
        print 'There was an error!'
    with open(args.out, 'w') as out:
        for u in urls:
            out.write('\t'.join([i.encode('utf-8') for i in u]) + '\n')
'''