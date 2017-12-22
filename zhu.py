#!/usr/bin/env python3
import random
import socket
import threading
import time
import urllib.request
from http.cookiejar import CookieJar

usable_proxy = set()


class UserAgent:
    agent = {}

    def random(self):
        self.get_platform()
        self.get_os()
        self.get_browser()

        if self.agent['browser'] == 'Chrome':
            webkit = str(random.randint(500, 599))
            version = "%s.0%s.%s" % (
            str(random.randint(0, 24)), str(random.randint(0, 1500)), str(random.randint(0, 999)))

            return "Mozilla/5.0 (%s) AppleWebKit/%s.0 (KHTML, live Gecko) Chrome/%s Safari/%s" % (
            self.agent['os'], webkit, version, webkit)
        elif self.agent['browser'] == 'Firefox':
            year = str(random.randint(2000, 2015))
            month = str(random.randint(1, 12)).zfill(2)
            day = str(random.randint(1, 28)).zfill(2)
            gecko = "%s%s%s" % (year, month, day)
            version = "%s.0" % (str(random.randint(1, 15)))

            return "Mozillia/5.0 (%s; rv:%s) Gecko/%s Firefox/%s" % (self.agent['os'], version, gecko, version)
        elif self.agent['browser'] == 'IE':
            version = "%s.0" % (str(random.randint(1, 10)))
            engine = "%s.0" % (str(random.randint(1, 5)))
            option = random.choice([True, False])
            if option:
                token = "%s;" % (random.choice(['.NET CLR', 'SV1', 'Tablet PC', 'Win64; IA64', 'Win64; x64', 'WOW64']))
            else:
                token = ''

            return "Mozilla/5.0 (compatible; MSIE %s; %s; %sTrident/%s)" % (version, self.agent['os'], token, engine)

    def get_os(self):
        if self.agent['platform'] == 'Machintosh':
            self.agent['os'] = random.choice(['68K', 'PPC'])
        elif self.agent['platform'] == 'Windows':
            self.agent['os'] = random.choice(
                ['Win3.11', 'WinNT3.51', 'WinNT4.0', 'Windows NT 5.0', 'Windows NT 5.1', 'Windows NT 5.2',
                 'Windows NT 6.0', 'Windows NT 6.1', 'Windows NT 6.2', 'Win95', 'Win98', 'Win 9x 4.90', 'WindowsCE',
                 'Windows NT 10.0'])
        elif self.agent['platform'] == 'X11':
            self.agent['os'] = random.choice(['Linux i686', 'Linux x86_64'])

    def get_browser(self):
        self.agent['browser'] = random.choice(['Chrome', 'Firefox', 'IE'])

    def get_platform(self):
        self.agent['platform'] = random.choice(['Machintosh', 'Windows', 'X11'])


def vote(proxy_str):
    global usable_proxy

    ua = UserAgent()
    header = {
        'Host': 'focus.uestc.edu.cn',
        'Connection': 'keep-alive',
        'Content-Length': '3',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'http://focus.uestc.edu.cn',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': ua.random(),
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'http://focus.uestc.edu.cn/specialtopic/28/vote?type=people',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'X-Forwarded-For': ip,
        # 'X-Real-IP': ip
    }
    login_url = 'http://focus.uestc.edu.cn/specialtopic/28/vote?type=people'
    cookie = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
    request = urllib.request.Request(
        url=login_url,
        data=bytes('119', 'utf-8'),
        headers=header,
    )
    proxy_elem = {
        'ip': proxy_str.split('@')[0],
        'port': proxy_str.split('@')[1],
        'method': proxy_str.split('@')[2].lower()
    }
    request.set_proxy(proxy_elem['ip'] + ':' + proxy_elem['port'], 'http')

    try:
        result = opener.open(request, timeout=12).read().decode('unicode-escape')
        print(result + '@' + proxy_elem['ip'])
        usable_proxy.add(proxy_str)
    except socket.timeout:
        print('bad proxy:' + proxy_elem['ip'])
    except ConnectionResetError:
        print('bad proxy:' + proxy_elem['ip'])
    except ConnectionAbortedError:
        print('bad proxy:' + proxy_elem['ip'])
    except urllib.error.HTTPError:
        print('bad proxy:' + proxy_elem['ip'])
    except ConnectionRefusedError:
        print('bad proxy:' + proxy_elem['ip'])
    except urllib.error.URLError:
        print('bad proxy:' + proxy_elem['ip'])


def load_proxy():
    proxy_list = set()
    f_in = open('proxy.list', 'r', encoding='utf-8')
    for line in f_in.readlines():
        line = line.strip()
        if len(line.split('@')) < 3:
            continue
        proxy_list.add(
            line.split('@')[0] +
            '@' + line.split('@')[1] +
            '@' + line.split('@')[2].lower()
        )
    f_in.close()
    return proxy_list


def for_every_proxy(proxy):
    for i in range(0, 12):
        vote(proxy)
        time.sleep(random.random() * 3)


class ProxyThread(threading.Thread):
    def __init__(self, proxy):
        super().__init__()
        self.proxy = proxy

    def run(self):
        for_every_proxy(self.proxy)


if __name__ == '__main__':
    proxies = list(load_proxy())
    f_out = open('proxy.list.tmp', 'a+')

    t_list = []
    for proxy in proxies:
        t_list.append(ProxyThread(proxy))

    for t in t_list:
        t.start()
    for t in t_list:
        t.join()

    for p in usable_proxy:
        f_out.write(p.strip() + '\n')
    print(len(usable_proxy))
    f_out.close()
