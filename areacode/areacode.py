import requests
from pyquery import PyQuery

rootUrl = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/'
out = open('result.csv', 'w', encoding='UTF-8')

class datas:
    def __init__(self, name=None, code=None, link='', level=0):
        self.name = name
        self.code = code
        self.link = link
        self.children = dict()
        self.parent = None
        self.level = level

    def push(self, data):
        self.children[data.name] = rootUrl + data.link

    def getData(self, func):
        resp = requests.get(self.link)
        if resp.ok:
            for result in func(resp.content):
                self.push(result)

    def __str__(self):
        space = ''
        for i in range(self.level):
            space += '\t'
        return '{}{}\t{}'.format(space, self.name, self.code)

def getProvince(content):
    pq = PyQuery(content)
    hrefs = pq('tr.provincetr')('a')
    result = map(lambda h: datas(h.text, None, rootUrl + h.attrib['href'], 1), hrefs)
    for r in result:
        print(r)
        out.write(str(r) + '\r\n')
        r.getData(getCity)
    return list(result)

def getCity(content):
    pq = PyQuery(content)
    cities = pq('tr.citytr')
    result = []
    for city in cities:
        c = PyQuery(city)('a')
        if len(c) == 0: continue
        r = datas(c[1].text, c[0].text, rootUrl + c[0].attrib['href'], 2)
        print(r)
        out.write(str(r) + '\r\n')
        r.getData(getDistrict)
        result.append(r)
    return result

def getDistrict(content):
    pq = PyQuery(content)
    cities = pq('tr.countytr')
    result = []
    for city in cities:
        c = PyQuery(city)('a')
        if len(c) == 0: continue
        r = datas(c[1].text, c[0].text, rootUrl + c[0].attrib['href'], 3)
        print(r)
        out.write(str(r) + '\r\n')
        result.append(r)
    return result

country = datas('中国', None, rootUrl + "index.html")
country.getData(getProvince)
print(country)

out.close()