# content grabber for 中国土地市场网
# http://www.landchina.com/default.aspx?tabid=263

import requests
from pyquery import PyQuery
import datetime
import logging


class Payment:
    def __init__(self):
        self.date = None
        self.amount = None
        self.comment = None

class DataItem:
    def __init__(self):
        self.name = None
        self.regulationNo = None
        self.landSource = None
        self.tenureOfUse = None
        self.industry = None
        self.landLevel = None
        self.price = None
        self.owner = None
        self.plotRatioUpperLimit = None
        self.plotRatioDownLimit = None
        self.dateOfDeliveryAgreed = None
        self.dateOfConstructionAgreed = None
        self.dateOfConstructionActual = None
        self.dateOfCompletionAgreed = None
        self.dateOfCompletionActual = None
        self.approvedBy = None
        self.dateOfSigning = None
        self.district = None
        self.location = None
        self.area = None
        self.usage = None
        self.wayOfSupply = None
        self.url = None
        self.payments = []

    def getData(self, func):
        func(self)

    def __str__(self):
        return "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
            self.district,
            self.regulationNo,
            self.name,
            self.location,
            self.area,
            self.landSource,
            self.usage,
            self.wayOfSupply,
            self.tenureOfUse,
            self.industry,
            self.landLevel,
            self.price,
            self.owner,
            self.plotRatioUpperLimit,
            self.plotRatioDownLimit,
            self.dateOfDeliveryAgreed,
            self.dateOfConstructionAgreed,
            self.dateOfCompletionAgreed,
            self.dateOfConstructionActual,
            self.dateOfCompletionActual,
            self.approvedBy,
            self.dateOfSigning,
            self.url)

def pageFunc(content, sessionOnly=False):
    pq = PyQuery(content)
    results = []
    items = pq('#TAB_contentTable')('tr')
    vs = pq('#__VIEWSTATE')[0].get('value')
    ev = pq('#__EVENTVALIDATION')[0].get('value')
    if sessionOnly:
        return None, vs, ev, 1
    totalPage = 0
    for a in pq('a'):
        if a.text_content() == "尾页":
            onclick = a.get('onclick').split(',')[1]
            totalPage = int(onclick[:len(onclick) - 1])
            break
    for item in items:
        item.make_links_absolute(rootUrl)
        keys = item.xpath('td[@class="queryCellBordy"]')
        if len(keys) == 0: continue
        logging.info("getting %s", keys[1].xpath('a')[0].get('href'))
        resp = requests.get(keys[1].xpath('a')[0].get('href'))
        if resp.ok:
            row = detailFunc(keys[1].xpath('a')[0].get('href'), resp.content.decode('gbk'))
            results.append(row)
        else:
            logging.info("failed to get detailed page: %s", keys[1].xpath('a')[0].get('href'))
    return results, vs, ev, totalPage

def detailFunc(url, content):
    childTrs = PyQuery(content)('table.theme tbody')[0].xpath('tr')
    data = DataItem()
    data.url = url
    data.district = childTrs[2].xpath('td')[1].text_content()
    data.regulationNo = childTrs[2].xpath('td')[3].text_content()
    data.name = childTrs[3].xpath('td')[1].text_content()
    data.location = childTrs[4].xpath('td')[1].text_content()
    data.area = childTrs[5].xpath('td')[1].text_content()
    are2 = childTrs[5].xpath('td')[3].text_content()
    try:
        if are2 == "" or not are2:
            data.landSource = "新增建设用地(来自存量库)"
        elif float(data.area) == float(are2):
            data.landSource = "现有建设用地"
        elif float(are2) == 0:
            data.landSource = "新增建设用地"
        else:
            data.landSource = "新增建设用地(来自存量库)"
    except:
        data.landSource = "新增建设用地(来自存量库)"
    data.usage = childTrs[6].xpath('td')[1].text_content()
    data.wayOfSupply = childTrs[6].xpath('td')[3].text_content()
    data.tenureOfUse = childTrs[7].xpath('td')[1].text_content()
    data.industry = childTrs[7].xpath('td')[3].text_content()
    data.landLevel = childTrs[8].xpath('td')[1].text_content()
    data.price = childTrs[8].xpath('td')[3].text_content()
    data.owner = childTrs[10].xpath('td')[1].text_content()
    plotRatio = PyQuery(childTrs[12])('tbody tr')[1].xpath('td')
    data.plotRatioUpperLimit = plotRatio[1].text_content()
    data.plotRatioDownLimit = plotRatio[3].text_content()
    data.dateOfDeliveryAgreed = childTrs[12].xpath('td')[3].text_content()
    data.dateOfConstructionAgreed = childTrs[13].xpath('td')[1].text_content()
    data.dateOfCompletionAgreed = childTrs[13].xpath('td')[3].text_content()
    data.dateOfConstructionActual = childTrs[14].xpath('td')[1].text_content()
    data.dateOfCompletionActual = childTrs[14].xpath('td')[3].text_content()
    data.approvedBy = childTrs[15].xpath('td')[1].text_content()
    if "人民政府" not in data.approvedBy:
        data.approvedBy += "人民政府"
    data.dateOfSigning = childTrs[15].xpath('td')[3].text_content()
    paymentsTrs = PyQuery(childTrs[9])('table tbody')[0].xpath('tr[position()>3]')
    for paymentsTr in paymentsTrs:
        payment = Payment()
        payment.date = paymentsTr.xpath('td')[1].text_content()
        payment.amount = paymentsTr.xpath('td')[2].text_content()
        payment.comment = paymentsTr.xpath('td')[3].text_content()
        data.payments.append(payment)
    return data

postData = {'TAB_QueryConditionItem': '9f2c3acd-0256-4da2-a659-6949c4671a2a',
                    'TAB_QuerySubmitConditionData': '9f2c3acd-0256-4da2-a659-6949c4671a2a:{}~{}'.format(
                        "2018-06-26", "2018-06-26"),
                    'TAB_QuerySortItemList': '282:False',
                    'TAB_QuerySubmitPagerData': 1,
                    'hidComName': 'default',
                    '__VIEWSTATE': "",
                    '__EVENTVALIDATION': ""}
resp = requests.post("http://www.landchina.com/default.aspx?tabid=263", data=postData)
if resp.ok:
    result = resp.content.decode('gbk')
    print(result)

logging.basicConfig(filename="land.log", filemode="a+", format="%(asctime)s %(levelname)s: %(message)s",
                    level=logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

output = open("result.csv", 'a+', encoding='utf-8')
output.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
    "行政区",
    "电子监管号",
    "项目名称",
    "项目名称",
    "面积(公顷)",
    "土地来源",
    "土地用途",
    "供地方式",
    "土地使用年限",
    "行业分类",
    "土地级别",
    "成交价格(万元)",
    "土地使用权人",
    "约定容积率-上限",
    "约定容积率-下限",
    "约定交地时间",
    "约定开工时间",
    "约定竣工时间",
    "实际开工时间",
    "实际竣工时间",
    "批准单位",
    "合同签订日期",
    "链接"))

rootUrl = "http://www.landchina.com/"

start_date = datetime.datetime(2018, 6, 26)
step = datetime.timedelta(days=5)

# get session
data, vs, ev, totalPage = None, None, None, None
resp = requests.get("http://www.landchina.com/default.aspx?tabid=263")
if resp.ok:
    content = resp.content.decode('gbk')
    data, vs, ev, totalPage = pageFunc(content, True)

# grab
while True:
    pageNo = 0
    totalPage = 1
    end_date = start_date - step
    while pageNo <= totalPage:
        pageNo += 1
        logging.info('getting page: %s-%s No: %d/%d', end_date.strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d'),
                     pageNo, totalPage)
        postData = {'TAB_QueryConditionItem': '9f2c3acd-0256-4da2-a659-6949c4671a2a',
                    'TAB_QuerySubmitConditionData': '9f2c3acd-0256-4da2-a659-6949c4671a2a:{}~{}'.format(
                        end_date.strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d')),
                    'TAB_QuerySortItemList': '282:False',
                    'TAB_QuerySubmitPagerData': pageNo,
                    'hidComName': 'default',
                    '__VIEWSTATE': vs,
                    '__EVENTVALIDATION': ev}
        resp = requests.post("http://www.landchina.com/default.aspx?tabid=263", data=postData)
        if resp.ok:
            content = resp.content.decode('gbk')
            data, vs, ev, totalPage = pageFunc(content)
            for row in data:
                output.write(str(row) + '\r\n')
        else:
            logging.error("failed to proceed page %d", pageNo)
    start_date = start_date - step

output.close()
