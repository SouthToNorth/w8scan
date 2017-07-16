#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib,hashlib,Queue,threading,json,urlparse,socket,base64,time

_DEBUG = True
if _DEBUG:
    _C = True
    _Plugin = '["http:\/\/127.0.0.1\/w8scan\/py\/plugins\/burtdir.py","http:\/\/127.0.0.1\/w8scan\/py\/plugins\/portscan.py","http:\/\/127.0.0.1\/w8scan\/py\/plugins\/whatcms.py"]'
    _SPlugin = '["http:\/\/127.0.0.1\/w8scan\/py\/spider\/2.py","http:\/\/127.0.0.1\/w8scan\/py\/spider\/email.py"]'
    _B = 'http://127.0.0.1/w8scan/'
    _U = 'https://yesfree.pw/'.rstrip('/')
    _Token = '29128d13a3b25e81bae0aa61c30f31f1'
    print "[...] w8scan is working!!!"
    print "[...] Initialize engine ..."
    time.sleep(2)
# init hackhttp
code = urllib.urlopen("https://raw.githubusercontent.com/BugScanTeam/hackhttp/master/hackhttp/hackhttp.py")
exec(code.read())

# Testing Hackhttp
# hh = hackhttp()
# code, head, body, redirect, log = hh.http('https://blog.yesfree.pw')
# print code,head,body
global plugin,splugins
plugin = json.loads(_Plugin)
splugins = json.loads(_SPlugin)

code = urllib.urlopen(_B + "py/common/w8_comon.py")
exec(code.read())


class UrlManager(object):
    def __init__(self):
        self.new_urls = set()
        self.old_urls = set()

    def add_new_url(self, url):
        if url is None:
            return
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)

    def add_new_urls(self, urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_new_url(url)

    def has_new_url(self):
        return len(self.new_urls) != 0

    def get_new_url(self):
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url

# 传递报告类
class w8_report(object):
    def __init__(self):
        self.data = {}
        
    def send(self):
        content = base64.encodestring(self._build())
        try:
            w8_Common.post(_B + "?send/"+_Token,"data=" + content)
        except Exception,e:
            print Exception,":",e

    def add(self,key,data):
        self.data[key] = data

    def add_list(self, key, data):
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(data)

    def add_set(self, key, data):
        if key not in self.data:
            self.data[key] = set()
        self.data[key].add(data)

    def _build(self):
        return json.dumps(self.data,cls=SetEncoder)

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

# spider code
import re
from urlparse import urljoin
class SpiderMain(object):
    def __init__(self, root, threadNum=10):
        global splugins
        self.urls = UrlManager()
        self.root = root
        self.threadNum = threadNum
        self.splugins = splugins

    def _judge(self, domain, url):
        if (url.find(domain) != -1):
            return True
        else:
            return False

    def _parse(self, page_url, content):
        if content is None:
            return
        # soup = BeautifulSoup(content, 'html.parser')
        webreg = re.compile('''<a[^>]+href=["\'](.*?)["\']''', re.IGNORECASE)
        urls = webreg.findall(content)
        _news = self._get_new_urls(page_url, urls)
        return _news

    def _get_new_urls(self, page_url, links):
        new_urls = set()
        for link in links:
            new_url = link
            new_full_url = urljoin(page_url, new_url)
            if (self._judge(self.root, new_full_url)):
                new_urls.add(new_full_url)
        return new_urls

    def craw(self):
        
        # splugins = [1]
        self.urls.add_new_url(self.root)
        while self.urls.has_new_url():
            if self.urls.has_new_url() is False:
                break
            new_url = self.urls.get_new_url()
            # print("craw:" + new_url)
            report.add_list("爬虫",new_url)
            code, head, body, redirect, log =w8_Common.get(new_url)
            if code != 200:
                continue
            new_urls = self._parse(new_url, body)
            self.urls.add_new_urls(new_urls)
            
            for tem_plugin in self.splugins:
                code = urllib.urlopen(tem_plugin).read()
                exec code
                exec "run(new_url,body)"
            report.send()

# _U = 'http://www.adfun.cn/'

report = w8_report()

def GetBaseInfo():
    report.add("server",w8_Common.getheaders(_U))
    report.add("title",w8_Common.gettitle(_U))
    report.add("ip",w8_Common.gethostbyname(_U))
GetBaseInfo()

if plugin is not None:
    for temp_plugin in plugin:
        code = urllib.urlopen(temp_plugin).read()
        exec code

if splugins is not None:
    ww = SpiderMain(_U)
    ww.craw()

if __name__ == '__main__':
    pass
    # w8_Common.getheaders("https://www.baidu.com")
    # print w8_Common.gettitle("https://www.baidu.com")