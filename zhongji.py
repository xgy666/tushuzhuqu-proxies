import requests
import urllib.robotparser
from urllib.parse import urlparse, urljoin
import re
from  datetime import *
import time
import itertools


def get_index():
    urls = []
    for i in range(0, 50):
        url = 'http://example.webscraping.com/places/default/index/%d' % i
        urls.append(url)
    return urls


def get_html(url, tries, proxies):
    try:
        response = requests.get(url, proxies=proxies)
        html = response.text
        #      print(html)
    except Exception:
        html = None
        if tries > 0:
            if 500 <= response.status_code < 600:
                return get_html(url, tres - 1)
    return html


def get_ip():
    response = requests.get('http://localhost:5000/get')
    ip = response.text
    proxies = {'http': 'http://' + ip}
    res = requests.get('http://example.webscraping.com', proxies=proxies)
    if res.status_code == 200:
        return proxies
    else:
        return requests.get('http://localhost:5000/get')


def get_links(html):
    pattern = re.compile('<td><div><a href="(.*?)">.*?</a>')
    links = re.findall(pattern, html)
    return links


def robot():
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url('http://example.webscraping.com' + '/robot.txt')
    rp.read()
    return rp


def get_info(seed_url, delay=5, num=5, tries=2, user_agent='BadCrawler', proxies=get_ip()):
    print(proxies)
    rp = robot()
    crawl = [seed_url]
    seen = {seed_url: 0}
    depth = seen[seed_url]
    throttle = Throttle(delay)

    while crawl:
        url = crawl.pop()
        if rp.can_fetch(user_agent, url):

            throttle.wait(url)
            html = get_html(url, tries, proxies)
            if html == None:
                num = num - 1
                if num == 0:
                    break

                else:
                    num = 5
                links = get_links(html)
                if depth < 2:
                    for link in links:
                            #         print(link)
                        link = urljoin(url, link)
                        if link not in seen:
                            if re.search('/view', link):
                                seen[link] = depth + 1

                                crawl.append(link)
        print(seen)
            #              print(crawl)

class Throttle:

    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()

if __name__ == '__main__':
    urls = get_index()
    for url in urls:
        print(url)
        get_info(url)


