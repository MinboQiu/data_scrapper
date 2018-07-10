import scrapy
import logging
import time
from scrapy.selector import Selector
from urllib.parse import urljoin
from landchina.landchina_com.items import LandChinaItem, Payment


class LandSpider(scrapy.Spider):
    name = "landchina_com"
    root_url = "http://www.landchina.com/default.aspx?tabid=263"
    encoding = "gbk"
    start_date = "2018-6-26"
    end_date = "2018-6-26"
    postData = {'TAB_QueryConditionItem': '9f2c3acd-0256-4da2-a659-6949c4671a2a',
                'TAB_QuerySubmitConditionData': '9f2c3acd-0256-4da2-a659-6949c4671a2a:{}~{}'.format(
                    start_date, end_date),
                'TAB_QuerySortItemList': '282:False',
                'TAB_QuerySubmitPagerData': '1',
                'hidComName': 'default',
                '__VIEWSTATE': "",
                '__EVENTVALIDATION': ""}

    def start_requests(self):
        self.log("begin login for {} - {}".format(self.start_date, self.end_date), logging.INFO)
        return [scrapy.Request(url=self.root_url, callback=self.parse_login, encoding=self.encoding)]

    def parse_login(self, response):
        self.log("process login ...", logging.INFO)
        resp = Selector(response)
        self.retrieve_state(resp)

        time.sleep(10)
        self.log("begin page 1 for {} - {}".format(self.start_date, self.end_date), logging.INFO)
        return scrapy.FormRequest(url=self.root_url, callback=self.parse_list, formdata=self.postData,
                                  meta=self.postData, encoding=self.encoding)

    def parse_list(self, response):
        self.log("process list page {}".format(response.url), logging.INFO)
        resp = Selector(response)
        table = resp.xpath('//table[@id="TAB_contentTable"]')[0]

        # push detail page links to scrapy
        detail_links = table.xpath('//a[contains(@href, "tabid=386")]/@href').extract()
        for link in detail_links:
            yield scrapy.Request(url=urljoin(self.root_url, link), callback=self.parse_detail, encoding=self.encoding)

        # push page links to scrapy
        if response.meta["TAB_QuerySubmitPagerData"] == 1:
            self.retrieve_state(resp)
            totalPage = table.xpath("//a[contains(., '尾页')]").re_first(r"QueryAction.GoPage\('TAB',(\d*)").strip()
            for pageNo in range(2, int(totalPage)):
                self.log("begin page {} for {} - {}".format(pageNo, self.start_date, self.end_date), logging.INFO)
                self.postData["TAB_QuerySubmitPagerData"] = str(pageNo)
                yield scrapy.FormRequest(url=self.root_url, callback=self.parse_list, formdata=self.postData,
                                         meta=self.postData, encoding=self.encoding)

    def parse_detail(self, response):
        self.log("process detail page {}".format(response.url), logging.INFO)
        resp = Selector(response)
        childTrs = resp.xpath('//table[@class="theme"]/tbody/tr')
        data = LandChinaItem()
        data["url"] = response.url
        data["guid"] = resp.xpath('//form/@action').re_first(r'recorderguid=(.*)')
        data["district"] = childTrs[2].xpath('td[2]/span/text()').extract_first()
        data["regulationNo"] = childTrs[2].xpath('td[4]/span/text()').extract_first()
        data["name"] = childTrs[3].xpath('td[2]/span/text()').extract_first()
        data["location"] = childTrs[4].xpath('td[2]/span/text()').extract_first()
        data["area"] = childTrs[5].xpath('td[2]/span/text()').extract_first()
        are2 = childTrs[5].xpath('td[4]/span/text()').extract()
        try:
            if are2 == "" or not are2:
                data["landSource"] = "新增建设用地(来自存量库)"
            elif float(data["area"]) == float(are2):
                data["landSource"] = "现有建设用地"
            elif float(are2) == 0:
                data["landSource"] = "新增建设用地"
            else:
                data["landSource"] = "新增建设用地(来自存量库)"
        except:
            data["landSource"] = "新增建设用地(来自存量库)"
        data["usage"] = childTrs[6].xpath('td[2]/span/text()').extract_first()
        data["wayOfSupply"] = childTrs[6].xpath('td[4]/span/text()').extract_first()
        data["tenureOfUse"] = childTrs[7].xpath('td[2]/span/text()').extract_first()
        data["industry"] = childTrs[7].xpath('td[4]/span/text()').extract_first()
        data["landLevel"] = childTrs[8].xpath('td[2]/span/text()').extract_first()
        data["price"] = childTrs[8].xpath('td[4]/span/text()').extract_first()
        data["owner"] = childTrs[10].xpath('td[2]/span/text()').extract_first()
        plotRatio = childTrs[12].xpath('td/table//tr[2]/td')
        data["plotRatioDownLimit"] = plotRatio[1].xpath('span/text()').extract_first()
        data["plotRatioUpperLimit"] = plotRatio[3].xpath('span/text()').extract_first()
        data["dateOfDeliveryAgreed"] = childTrs[12].xpath('td[4]/span/text()').extract_first()
        data["dateOfConstructionAgreed"] = childTrs[13].xpath('td[2]/span/text()').extract_first()
        data["dateOfCompletionAgreed"] = childTrs[13].xpath('td[4]/span/text()').extract_first()
        data["dateOfConstructionActual"] = childTrs[14].xpath('td[2]/span/text()').extract_first()
        data["dateOfCompletionActual"] = childTrs[14].xpath('td[4]/span/text()').extract_first()
        data["approvedBy"] = childTrs[15].xpath('td[2]/span/text()').extract_first()
        if "人民政府" not in data["approvedBy"]:
            data["approvedBy"] += "人民政府"
        data["dateOfSigning"] = childTrs[15].xpath('td[4]/span/text()').extract_first()
        paymentsTrs = childTrs[9].xpath('td[2]//tr[contains(@kvalue, "-")]')
        payments = []
        for paymentsTr in paymentsTrs:
            payment = Payment()
            payment["guid"] = paymentsTr.xpath('@kvalue').extract_first()
            payment["date"] = paymentsTr.xpath('td[2]/span/text()').extract_first()
            payment["amount"] = paymentsTr.xpath('td[3]/span/text()').extract_first()
            payment["comment"] = paymentsTr.xpath('td[4]/span/text()').extract_first()
            payments.append(dict(payment))
        data["payments"] = payments
        return data

    def parse(self, response):
        self.log("process parse func {}".format(response.url), logging.INFO)
        pass

    def retrieve_state(self, resp):
        vs = resp.xpath('//input[@id="__VIEWSTATE"]/@value').extract_first().strip()
        ev = resp.xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first().strip()
        self.postData['__VIEWSTATE'] = vs
        self.postData['__EVENTVALIDATION'] = ev
